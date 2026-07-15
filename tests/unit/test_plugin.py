import os
import pytest
from unittest.mock import MagicMock
from digital_state.hermes.plugin import DigitalStatePlugin, register

class MockHermesContext:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.skills = {}
        self.hooks = {}
        self.commands = {}
        
    def register_skill(self, name: str, path: str):
        self.skills[name] = path
        
    def register_hook(self, name: str, callback):
        self.hooks[name] = callback
        
    def register_command(self, name: str, callback):
        self.commands[name] = callback

def test_plugin_registration():
    """Verify that the plugin registers tools, commands, and skills correctly."""
    ctx = MockHermesContext(workspace_root="/mock/root")
    plugin = DigitalStatePlugin(ctx)
    
    assert plugin.initialize() is True
    assert "governance_playbook" in ctx.skills
    assert "pre_tool_call" in ctx.hooks
    assert "/ds-approve" in ctx.commands

def test_plugin_version_mismatch():
    """Verify that version mismatch blocks initialization and returns False."""
    ctx = MockHermesContext(workspace_root="/mock/root")
    plugin = DigitalStatePlugin(ctx)
    plugin.version = "0.2.0"  # Incompatible version
    
    assert plugin.initialize() is False
    assert not plugin.is_loaded

def test_plugin_all_hooks_registration():
    """Verify that the plugin registers all six standard runtime hooks."""
    ctx = MockHermesContext(workspace_root="/mock/root")
    plugin = DigitalStatePlugin(ctx)
    assert plugin.initialize() is True
    
    assert "on_session_start" in ctx.hooks
    assert "pre_llm_call" in ctx.hooks
    assert "post_llm_call" in ctx.hooks
    assert "pre_tool_call" in ctx.hooks
    assert "post_tool_call" in ctx.hooks
    assert "on_session_end" in ctx.hooks

def test_plugin_hooks_fail_safe_deny():
    """Verify that hooks default to fail-safe DENY (False) on missing/invalid signatures."""
    ctx = MockHermesContext(workspace_root="/mock/root")
    plugin = DigitalStatePlugin(ctx)
    assert plugin.initialize() is True
    
    # 1. Test pre_tool_call_handler with invalid context
    assert plugin.pre_tool_call_handler("run_command", {}, {}).get("action") == "block"
    
    # 2. Test pre_llm_call_handler with invalid context
    assert plugin.pre_llm_call_handler("Hello", {}) is None
    
    # 3. Test on_session_start_handler with invalid context
    assert plugin.on_session_start_handler({}) is False


