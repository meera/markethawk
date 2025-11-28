"""
Workflow execution engine for FlipbookFactory.

Reads YAML workflow configs and executes steps in sequence.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
import re

from flipbook.step import StepRegistry


class WorkflowEngine:
    """
    Execute workflows defined in YAML configs.

    Example YAML:
        workflow:
          - step: download_video
            params:
              url: https://youtube.com/watch?v=xxx

          - step: extract_frames
            params:
              input: ${prev.output}
              fps: 24
    """

    def __init__(self, config_path: Path, experiment_dir: Path):
        """
        Initialize workflow engine.

        Args:
            config_path: Path to YAML workflow config
            experiment_dir: Directory for experiment outputs
        """
        self.config_path = Path(config_path)
        self.experiment_dir = Path(experiment_dir)
        self.config = self._load_config()
        self.step_outputs = {}  # Store outputs from each step

    def _load_config(self) -> Dict[str, Any]:
        """Load and parse YAML config"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        if not config:
            raise ValueError("Empty config file")

        if 'workflow' not in config:
            raise ValueError("Config must contain 'workflow' key")

        return config

    def run(self) -> Dict[str, Any]:
        """
        Execute the workflow.

        Returns:
            Dictionary with workflow execution results
        """
        print(f"{'='*60}")
        print(f"🎬 Running Experiment: {self.config.get('experiment_id', 'unknown')}")
        if 'description' in self.config:
            print(f"📝 {self.config['description']}")
        if 'tags' in self.config:
            print(f"🏷️  Tags: {', '.join(self.config['tags'])}")
        print(f"{'='*60}\n")

        workflow_steps = self.config['workflow']
        results = []

        for i, step_def in enumerate(workflow_steps, 1):
            step_name = step_def.get('step')
            step_id = step_def.get('id', step_name)  # Use custom ID if provided
            params = step_def.get('params', {})

            print(f"\n[Step {i}/{len(workflow_steps)}] {step_name}")
            print(f"{'─'*60}")

            # Resolve parameter references (like ${prev.output})
            resolved_params = self._resolve_params(params, step_id)

            # Create and execute step
            step_instance = StepRegistry.create(step_name, self.experiment_dir)
            if not step_instance:
                raise ValueError(f"Unknown step: {step_name}")

            output = step_instance.process(**resolved_params)

            # Store output for later steps to reference
            self.step_outputs[step_id] = output
            self.step_outputs['prev'] = output  # Always update 'prev'

            results.append({
                'step': step_name,
                'id': step_id,
                'params': resolved_params,
                'output': output
            })

        print(f"\n{'='*60}")
        print(f"✅ Workflow completed successfully!")
        print(f"{'='*60}")

        return {
            'experiment_id': self.config.get('experiment_id'),
            'results': results,
            'final_output': results[-1]['output'] if results else None
        }

    def _resolve_params(self, params: Dict[str, Any], current_step_id: str) -> Dict[str, Any]:
        """
        Resolve parameter references like ${prev.output} or ${step_id.output}

        Args:
            params: Raw parameters from YAML
            current_step_id: ID of current step (for error messages)

        Returns:
            Resolved parameters with references replaced
        """
        resolved = {}

        for key, value in params.items():
            if isinstance(value, str) and '${' in value:
                resolved[key] = self._resolve_reference(value, current_step_id)
            else:
                resolved[key] = value

        return resolved

    def _resolve_reference(self, reference: str, current_step_id: str) -> Any:
        """
        Resolve a single reference like ${prev.output} or ${download.output}

        Syntax:
            ${prev.output} - Output from previous step
            ${step_id.output} - Output from step with id 'step_id'
            ${step_id.metadata.title} - Nested access

        Args:
            reference: Reference string to resolve
            current_step_id: ID of current step

        Returns:
            Resolved value
        """
        # Extract all ${...} references
        pattern = r'\$\{([^}]+)\}'
        matches = re.findall(pattern, reference)

        if not matches:
            return reference

        result = reference
        for match in matches:
            # Parse reference: "prev.output" -> step="prev", path="output"
            parts = match.split('.')
            step_id = parts[0]
            path = parts[1:] if len(parts) > 1 else []

            if step_id not in self.step_outputs:
                raise ValueError(
                    f"Step '{current_step_id}' references unknown step '{step_id}'. "
                    f"Available: {list(self.step_outputs.keys())}"
                )

            # Navigate nested dict
            value = self.step_outputs[step_id]
            for key in path:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    raise ValueError(
                        f"Cannot access '{key}' in {step_id}: not a dict"
                    )

            # Replace reference with value
            result = result.replace(f'${{{match}}}', str(value))

        return result


def load_workflow(config_path: Path, experiment_dir: Path) -> WorkflowEngine:
    """
    Load a workflow from YAML config.

    Args:
        config_path: Path to YAML workflow config
        experiment_dir: Directory for experiment outputs

    Returns:
        WorkflowEngine instance ready to run
    """
    return WorkflowEngine(config_path, experiment_dir)
