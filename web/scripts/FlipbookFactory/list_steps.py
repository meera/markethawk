#!/usr/bin/env python3
"""
List all available workflow steps.

Usage:
    python list_steps.py
"""

import flipbook.steps
from flipbook.step import StepRegistry


def main():
    print("Available Steps:")
    print("=" * 60)

    steps = StepRegistry.list_steps()

    if not steps:
        print("No steps registered!")
        return

    for step_name in steps:
        step_class = StepRegistry.get(step_name)
        doc = step_class.__doc__ or "No description available"

        # Extract first line of docstring
        first_line = doc.strip().split('\n')[0]

        print(f"\n• {step_name}")
        print(f"  {first_line}")

    print("\n" + "=" * 60)
    print(f"Total: {len(steps)} steps")


if __name__ == "__main__":
    main()
