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
    assert "/approve" in ctx.commands
