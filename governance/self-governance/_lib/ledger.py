"""Shared hash-chained, signed governance ledger for Digital State self-governance events.

Reusable primitive so each event gets its own immutable, signable audit trail
without duplicating crypto code. Keys are the registered local ECDSA identities
under governance/product-validation/test-keys/.
"""
from __future__ import annotations

import json
import base64
import hashlib
from pathlib import Path
from datetime import datetime, timezone

from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization

KEYS = Path("D:/Digital-State/governance/product-validation/test-keys")
GENESIS = "0" * 64


class Ledger:
    def __init__(self, path: Path):
        self.path = Path(path)

    # --- crypto ---
    def _load_priv(self, role):
        return serialization.load_pem_private_key(
            (KEYS / f"{role}-agent.pem").read_bytes(), password=None
        )

    def _load_pub(self, role):
        return serialization.load_pem_public_key(
            (KEYS / f"{role}-agent.pub.pem").read_bytes()
        )

    @staticmethod
    def _canon(obj) -> bytes:
        return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()

    def sign(self, role: str, payload: dict) -> dict:
        sig = self._load_priv(role).sign(self._canon(payload), ec.ECDSA(hashes.SHA256()))
        r, s = decode_dss_signature(sig)
        return {
            "signer": f"{role}-agent",
            "key_id": f"key-{role}",
            "algorithm": "ECDSA-P256-SHA256",
            "signature": base64.b64encode(sig).decode(),
            "r": hex(r),
            "s": hex(s),
        }

    def verify(self, role: str, payload: dict, env: dict) -> bool:
        try:
            self._load_pub(role).verify(
                base64.b64decode(env["signature"]), self._canon(payload),
                ec.ECDSA(hashes.SHA256()),
            )
            return True
        except Exception:
            return False

    # --- chain ---
    def _last_hash(self) -> str:
        if not self.path.exists():
            return GENESIS
        lines = [l for l in self.path.read_text().splitlines() if l.strip()]
        return json.loads(lines[-1])["hash"]

    def _next_seq(self) -> int:
        if not self.path.exists():
            return 1
        return len([l for l in self.path.read_text().splitlines() if l.strip()]) + 1

    def append(self, event_type: str, agent_id: str, details: dict) -> dict:
        seq = self._next_seq()
        prev = self._last_hash()
        payload = {
            "sequence_id": seq,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "agent_id": agent_id,
            "details": details,
        }
        h = hashlib.sha256(bytes.fromhex(prev) + self._canon(payload)).hexdigest()
        entry = {**payload, "prev_hash": prev, "hash": h}
        with self.path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
        return entry

    def valid(self) -> bool:
        prev = GENESIS
        for line in self.path.read_text().splitlines():
            if not line.strip():
                continue
            e = json.loads(line)
            p = {k: e[k] for k in ("sequence_id", "timestamp", "event_type", "agent_id", "details")}
            h = hashlib.sha256(bytes.fromhex(e["prev_hash"]) + self._canon(p)).hexdigest()
            if e["prev_hash"] != prev or e["hash"] != h:
                return False
            prev = h
        return True
