from abc import ABC, abstractmethod
from typing import Dict, Any


class RuntimeCapability(ABC):
    """Declarative interface representing the capabilities of a runtime integration layer."""

    @abstractmethod
    def supports_execution(self) -> bool:
        pass

    @abstractmethod
    def supports_web(self) -> bool:
        pass

    @abstractmethod
    def supports_tools(self) -> bool:
        pass

    @abstractmethod
    def supports_files(self) -> bool:
        pass

    @abstractmethod
    def supports_memory(self) -> bool:
        pass

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def self_test(self) -> bool:
        pass

    @abstractmethod
    def execute_command_context(self, command: str) -> Dict[str, Any]:
        pass
