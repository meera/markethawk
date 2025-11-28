"""
Base Step class for FlipbookFactory workflow steps.

Each step is a reusable processing unit that:
- Takes input parameters
- Processes data
- Returns output (usually file paths or data)
- Tracks its configuration for reproducibility
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path


class Step(ABC):
    """
    Base class for all workflow steps.

    Subclasses must implement:
    - process(): The main processing logic
    - get_schema(): Parameter schema for validation (optional)
    """

    def __init__(self, experiment_dir: Optional[Path] = None):
        """
        Initialize step.

        Args:
            experiment_dir: Directory where experiment outputs are saved
        """
        self.experiment_dir = experiment_dir
        self.params = {}

    @abstractmethod
    def process(self, **params) -> Dict[str, Any]:
        """
        Execute the step's processing logic.

        Args:
            **params: Step-specific parameters from YAML config

        Returns:
            Dict with outputs, typically including 'output' key with result path/data

        Example:
            return {
                'output': 'path/to/output.mp4',
                'metadata': {'frame_count': 120}
            }
        """
        pass

    def get_config(self) -> Dict[str, Any]:
        """
        Return step configuration for tracking.
        Used to save what parameters were used in the experiment.

        Returns:
            Dictionary of parameters used
        """
        return self.params.copy()

    def get_schema(self) -> Optional[Dict[str, Any]]:
        """
        Optional: Return JSON schema for parameter validation.

        Returns:
            JSON schema dict or None
        """
        return None

    @classmethod
    def get_name(cls) -> str:
        """
        Get step name (defaults to class name in snake_case).
        Override if you want a different name in YAML.
        """
        # Convert CamelCase to snake_case
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
        return name.replace('_step', '')


class StepRegistry:
    """
    Registry to manage available steps.

    This allows the workflow engine to look up steps by name.
    """

    _steps: Dict[str, type] = {}

    @classmethod
    def register(cls, step_class: type) -> type:
        """
        Register a step class.

        Can be used as a decorator:
            @StepRegistry.register
            class MyStep(Step):
                ...
        """
        name = step_class.get_name()
        cls._steps[name] = step_class
        return step_class

    @classmethod
    def get(cls, name: str) -> Optional[type]:
        """Get step class by name"""
        return cls._steps.get(name)

    @classmethod
    def list_steps(cls) -> list:
        """List all registered step names"""
        return sorted(cls._steps.keys())

    @classmethod
    def create(cls, name: str, experiment_dir: Optional[Path] = None) -> Optional[Step]:
        """Create step instance by name"""
        step_class = cls.get(name)
        if step_class:
            return step_class(experiment_dir=experiment_dir)
        return None
