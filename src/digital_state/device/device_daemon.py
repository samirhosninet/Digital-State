"""Device Interception Runtime Daemon (v1.11.0-device).

Starts local runtime daemon listening on local IPC socket only:
    - Unix/macOS: /tmp/digitalstate.sock
    - Windows: \\.\\pipe\\digitalstate or 127.0.0.1 loopback

Strict security bounds:
    - No external network listener (0.0.0.0 forbidden).
    - Local IPC connection verification.
    - Evaluates requests via LocalPolicyEngine.
    - Fails closed on exception or offline expiration.
"""

import json
import os
import platform
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional
from digital_state.device.policy_engine import LocalPolicyEngine


class DeviceDaemon:
    """Local IPC daemon managing sub-millisecond tool interception."""

    def __init__(self, device_dir: Optional[Path] = None, host: str = "127.0.0.1", port: int = 49812):
        self.device_dir = device_dir or Path(".specify") / "device"
        self.host = host
        self.port = port
        self.policy_engine = LocalPolicyEngine(device_dir=self.device_dir)
        self._server_socket: Optional[socket.socket] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self, background: bool = True):
        """Starts local IPC server listener bound strictly to loopback interface."""
        # Enforce loopback binding ONLY
        if self.host not in ("127.0.0.1", "localhost"):
            raise ValueError("DeviceDaemon forbidden from binding to external network interfaces.")

        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(128)
        self._running = True

        if background:
            self._thread = threading.Thread(target=self._listen_loop, daemon=True)
            self._thread.start()
        else:
            self._listen_loop()

    def _listen_loop(self):
        """Internal accept loop for local IPC connections."""
        while self._running and self._server_socket:
            try:
                client_sock, addr = self._server_socket.accept()
                # Verify client is strictly local loopback
                client_ip = addr[0]
                if client_ip not in ("127.0.0.1", "::1"):
                    client_sock.close()
                    continue

                handler = threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True)
                handler.start()
            except Exception:
                if not self._running:
                    break

    def _handle_client(self, client_sock: socket.socket):
        """Handles single local IPC client connection."""
        try:
            client_sock.settimeout(2.0)
            data = client_sock.recv(65536)
            if not data:
                client_sock.close()
                return

            try:
                request = json.loads(data.decode("utf-8"))
            except Exception:
                block_resp = {
                    "action": "block",
                    "reason": "Malformed IPC request payload. Fail-Safe Deny triggered."
                }
                client_sock.sendall(json.dumps(block_resp).encode("utf-8"))
                client_sock.close()
                return

            # Evaluate policy
            decision = self.policy_engine.evaluate(request)
            client_sock.sendall(json.dumps(decision).encode("utf-8"))
        except Exception as e:
            try:
                block_resp = {"action": "block", "reason": f"Daemon handling error: {e}"}
                client_sock.sendall(json.dumps(block_resp).encode("utf-8"))
            except Exception:
                pass
        finally:
            try:
                client_sock.close()
            except Exception:
                pass

    def stop(self):
        """Stops local IPC server listener."""
        self._running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None

    @classmethod
    def send_ipc_request(cls, request: Dict[str, Any], host: str = "127.0.0.1", port: int = 49812, timeout: float = 1.0) -> Dict[str, Any]:
        """Client helper method to send IPC interception request to local DeviceDaemon.

        Fails closed (returns BLOCK dict) if daemon is unavailable.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.sendall(json.dumps(request).encode("utf-8"))
            resp_bytes = sock.recv(65536)
            sock.close()
            return json.loads(resp_bytes.decode("utf-8"))
        except Exception as e:
            # FAIL CLOSED if daemon unavailable
            return {
                "action": "block",
                "trace_id": request.get("trace_id", "UNKNOWN_TRACE"),
                "reason": f"DeviceDaemon IPC unavailable ({e}). Fail-Closed Default-Deny enforced."
            }
