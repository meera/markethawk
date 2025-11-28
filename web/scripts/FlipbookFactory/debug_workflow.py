#!/usr/bin/env python3
"""
Debug workflow execution - see exactly how data flows between steps.

Usage:
    python debug_workflow.py experiments/exp_001.yaml
"""

import sys
import json
from pathlib import Path

# Import to register all steps
import flipbook.steps
from flipbook.workflow import WorkflowEngine


class DebugWorkflowEngine(WorkflowEngine):
    """
    Extended workflow engine that prints detailed debugging info.
    Shows exactly how data flows between steps.
    """

    def run(self):
        """Execute workflow with detailed logging"""
        print(f"{'='*70}")
        print(f"🔍 DEBUG MODE - Workflow Data Flow")
        print(f"{'='*70}")
        print(f"Experiment: {self.config.get('experiment_id', 'unknown')}")
        print(f"Config: {self.config_path}")
        print(f"{'='*70}\n")

        workflow_steps = self.config['workflow']
        results = []

        for i, step_def in enumerate(workflow_steps, 1):
            step_name = step_def.get('step')
            step_id = step_def.get('id', step_name)
            params = step_def.get('params', {})

            print(f"\n{'#'*70}")
            print(f"# Step {i}/{len(workflow_steps)}: {step_name} (id={step_id})")
            print(f"{'#'*70}\n")

            # Show raw params from YAML
            print("📄 Raw params from YAML:")
            print(json.dumps(params, indent=2))

            # Show current step_outputs state
            if self.step_outputs:
                print("\n💾 Available step outputs in memory:")
                for stored_id, stored_output in self.step_outputs.items():
                    print(f"  • {stored_id}:")
                    print(f"    {json.dumps(stored_output, indent=6)}")
            else:
                print("\n💾 No previous step outputs yet")

            # Resolve parameters
            print("\n🔧 Resolving references...")
            resolved_params = self._resolve_params(params, step_id)

            # Show what changed
            has_references = False
            for key, value in params.items():
                if isinstance(value, str) and '${' in value:
                    has_references = True
                    print(f"  • {key}:")
                    print(f"      Before: {value}")
                    print(f"      After:  {resolved_params[key]}")

            if not has_references:
                print("  No references to resolve")

            print("\n✅ Final resolved params:")
            print(json.dumps(resolved_params, indent=2))

            # Create and execute step
            print(f"\n▶️  Executing {step_name}.process()...")
            print(f"{'─'*70}")

            from flipbook.step import StepRegistry
            step_instance = StepRegistry.create(step_name, self.experiment_dir)
            if not step_instance:
                raise ValueError(f"Unknown step: {step_name}")

            output = step_instance.process(**resolved_params)

            print(f"{'─'*70}")
            print(f"\n📤 Step returned:")
            print(json.dumps(output, indent=2))

            # Store output
            self.step_outputs[step_id] = output
            self.step_outputs['prev'] = output

            print(f"\n💾 Stored as step_outputs['{step_id}']")
            print(f"💾 Also stored as step_outputs['prev']")

            results.append({
                'step': step_name,
                'id': step_id,
                'params': resolved_params,
                'output': output
            })

        print(f"\n{'='*70}")
        print(f"✅ Workflow completed!")
        print(f"{'='*70}")

        print(f"\n📊 Final Summary:")
        print(f"Total steps executed: {len(results)}")
        print(f"\nFinal outputs:")
        for result in results:
            print(f"  • {result['id']}: {result['output'].get('output', 'N/A')}")

        return {
            'experiment_id': self.config.get('experiment_id'),
            'results': results,
            'final_output': results[-1]['output'] if results else None
        }


def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_workflow.py <workflow_config.yaml>")
        print("\nExample:")
        print("  python debug_workflow.py experiments/exp_001.yaml")
        sys.exit(1)

    config_path = Path(sys.argv[1])

    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)

    # Use experiment directory
    experiment_id = config_path.stem
    experiment_dir = config_path.parent / experiment_id
    experiment_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Use debug workflow engine instead of normal one
        workflow = DebugWorkflowEngine(config_path, experiment_dir)
        result = workflow.run()

        print(f"\n{'='*70}")
        print("🎓 Learning Points:")
        print(f"{'='*70}")
        print("1. Each step returns a dictionary")
        print("2. The 'output' key contains the main result (usually a file path)")
        print("3. References like ${step_id.output} get replaced with actual values")
        print("4. All previous step outputs stay in memory for later reference")
        print("5. Steps are decoupled - they don't know about each other!")
        print(f"{'='*70}\n")

    except Exception as e:
        print(f"\n❌ Debug workflow failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
