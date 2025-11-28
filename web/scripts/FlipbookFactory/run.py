#!/usr/bin/env python3
"""
FlipbookFactory workflow runner.

Execute experiments defined in YAML configs.

Usage:
    python run.py experiments/exp_001.yaml
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Import to register all steps
import flipbook.steps
from flipbook.workflow import load_workflow


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py <workflow_config.yaml>")
        print("\nExample:")
        print("  python run.py experiments/exp_001.yaml")
        sys.exit(1)

    config_path = Path(sys.argv[1])

    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        sys.exit(1)

    # Determine experiment directory
    # experiments/exp_001.yaml -> experiments/exp_001/
    experiment_id = config_path.stem
    experiment_dir = config_path.parent / experiment_id

    # Create experiment directory
    experiment_dir.mkdir(parents=True, exist_ok=True)

    print(f"📂 Experiment directory: {experiment_dir}")

    # Copy config to experiment directory for reproducibility
    config_copy = experiment_dir / 'config.yaml'
    if not config_copy.exists():
        import shutil
        shutil.copy(config_path, config_copy)

    # Load and run workflow
    try:
        workflow = load_workflow(config_path, experiment_dir)
        result = workflow.run()

        # Save metadata
        metadata = {
            'experiment_id': experiment_id,
            'timestamp': datetime.now().isoformat(),
            'config_path': str(config_path),
            'results': result['results'],
            'final_output': result['final_output']
        }

        metadata_path = experiment_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\n📄 Metadata saved: {metadata_path}")
        print(f"📁 Experiment directory: {experiment_dir}")

        # Create notes file if it doesn't exist
        notes_path = experiment_dir / 'notes.md'
        if not notes_path.exists():
            with open(notes_path, 'w') as f:
                f.write(f"# {experiment_id}\n\n")
                f.write(f"## Notes\n\n")
                f.write(f"Add your observations here...\n\n")
            print(f"📝 Notes file created: {notes_path}")

        print(f"\n✅ Experiment completed successfully!")

    except Exception as e:
        print(f"\n❌ Experiment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
