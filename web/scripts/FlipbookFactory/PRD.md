# FlipbookFactory PRD
## AI Video-to-Flipbook Experimentation Playground

## 1. Purpose

Personal sandbox for experimenting with AI methods to convert videos into flipbook animations. Build custom workflows by mixing and matching reusable processing steps defined in YAML configs.

**Core Principle:** Flexible pipeline composition - every experiment can use different steps in different orders.

---

## 2. Key Concepts

### 2.1 Steps (Reusable Building Blocks)

Each step is a modular processing unit:
- **Pose extraction:** MediaPipe, OpenPose, MoveNet
- **Stylization:** ControlNet, AnimateDiff, SD-Video, img2img
- **Temporal processing:** Optical flow, frame blending, interpolation
- **Utilities:** Extract frames, encode video, upscale, color grade

### 2.2 Workflows (YAML Pipeline Definitions)

Compose steps into custom pipelines via YAML:

```yaml
experiment_id: exp_001
description: "ControlNet sketch with MediaPipe pose"
tags: [controlnet, sketch, mediapipe]

workflow:
  - step: extract_frames
    params:
      input: data/inputs/dance.mp4
      fps: 24

  - step: mediapipe_pose
    params:
      input: ${prev.output}
      confidence: 0.5

  - step: controlnet_stylize
    params:
      input: ${prev.output}
      pose_data: ${steps.mediapipe_pose.output}
      prompt: "hand-drawn pencil sketch, flipbook animation"
      model: control_v11p_sd15_openpose
      steps: 20
      cfg_scale: 7.5

  - step: optical_flow_smooth
    params:
      input: ${prev.output}
      strength: 0.3

  - step: encode_video
    params:
      input: ${prev.output}
      output: experiments/exp_001/final.mp4
      fps: 24
```

**Different experiment, different workflow:**
```yaml
experiment_id: exp_002
tags: [animatediff, no-pose]

workflow:
  - step: animatediff
    params:
      input: data/inputs/dance.mp4
      prompt: "charcoal sketch animation"
      motion_module: v2

  - step: encode_video
    params:
      input: ${prev.output}
      output: experiments/exp_002/final.mp4
```

### 2.3 Experiment Tracking

Auto-save each experiment:
- YAML config (what you did)
- Outputs (videos, frames, data)
- Metadata (timestamps, duration)
- Notes (your observations)

---

## 3. Core Features

### 3.1 Run Experiments
```bash
# Run from YAML config
python run.py experiments/exp_001.yaml

# Or use helper to create config
python run.py --interactive
```

### 3.2 Track Everything

Auto-organized outputs:
```
experiments/
  exp_001/
    config.yaml          # Workflow definition
    metadata.json        # Auto-tracked stats
    notes.md             # Your observations
    outputs/
      final.mp4
      frames/
      pose_data.json
```

### 3.3 Compare Results

```bash
# Visual comparison
python compare.py exp_001 exp_002 exp_005

# Config diff
python diff.py exp_001 exp_003

# Search experiments
python search.py --tag controlnet --rating 4+
```

### 3.4 Reuse & Iterate

```bash
# Clone and modify
cp experiments/exp_001.yaml experiments/exp_001b.yaml
# Edit YAML to change prompt, re-run

# Resume from intermediate step
python run.py exp_001.yaml --from-step controlnet_stylize
```

---

## 4. Technical Design

### 4.1 Step Registry

Each step is a Python class:
```python
class Step:
    def process(self, input, params):
        # Do work
        return output

    def get_config(self):
        # Return settings for tracking
        return self.params
```

**Example steps:**
```python
class MediaPipePose(Step):
    def process(self, video_path, params):
        # Extract pose data
        return pose_data

class ControlNetStylize(Step):
    def process(self, frames, params):
        # Generate styled frames
        return styled_frames
```

### 4.2 Workflow Engine

Reads YAML → executes steps → saves results:
```python
def run_workflow(config_path):
    config = load_yaml(config_path)
    experiment = Experiment(config['experiment_id'])

    for step_def in config['workflow']:
        step = get_step(step_def['step'])
        output = step.process(**step_def['params'])
        experiment.track_step(step_def, output)

    experiment.save()
```

### 4.3 Project Structure

```
FlipbookFactory/
├── data/inputs/              # Source videos
├── experiments/              # Experiment configs & outputs
│   ├── exp_001.yaml
│   ├── exp_001/             # Outputs
│   ├── exp_002.yaml
│   └── exp_002/
├── models/                   # Downloaded AI models
├── flipbook/
│   ├── steps/               # Step implementations
│   │   ├── pose/
│   │   ├── stylize/
│   │   └── temporal/
│   ├── workflow.py          # Workflow engine
│   ├── experiment.py        # Experiment tracking
│   └── utils.py
├── run.py                   # Main runner
├── compare.py               # Comparison tools
└── notebooks/               # Optional Jupyter experiments
```

---

## 5. Workflow Examples

### Linear Pipeline
```yaml
workflow:
  - step: extract_frames
  - step: mediapipe_pose
  - step: controlnet_stylize
  - step: optical_flow_smooth
  - step: encode_video
```

### Branching Workflow
```yaml
workflow:
  - step: extract_frames
    id: frames

  - step: mediapipe_pose
    params:
      input: ${frames.output}
    id: pose

  - step: controlnet_stylize
    params:
      input: ${frames.output}
      pose_data: ${pose.output}

  - step: encode_video
```

### Skip Steps (Test Different Approaches)
```yaml
# Experiment A: With pose
workflow:
  - step: mediapipe_pose
  - step: controlnet_stylize

# Experiment B: Direct stylization
workflow:
  - step: animatediff  # No pose step!
```

---

## 6. Comparison & Analysis

### 6.1 Built-in Tools

**Compare configs:**
```bash
$ python diff.py exp_001 exp_003

Differences:
  workflow[2].params.prompt:
    exp_001: "pencil sketch"
    exp_003: "charcoal drawing"

  workflow[2].params.cfg_scale:
    exp_001: 7.5
    exp_003: 9.0
```

**Visual comparison:**
```bash
$ python compare.py exp_001 exp_003 --layout side-by-side
# Opens video player with synchronized playback
```

**Search:**
```bash
$ python search.py --tag controlnet --date-after 2025-01-20
Found 3 experiments:
  exp_001 - "ControlNet sketch with MediaPipe" [4/5]
  exp_003 - "Charcoal style test" [3/5]
  exp_007 - "High CFG experiment" [2/5]
```

### 6.2 Experiment Index

Auto-maintained `.experiment_index.json`:
```json
{
  "exp_001": {
    "timestamp": "2025-01-22T10:30:00",
    "description": "ControlNet sketch with MediaPipe pose",
    "tags": ["controlnet", "sketch", "mediapipe"],
    "steps": ["extract_frames", "mediapipe_pose", "controlnet_stylize", "optical_flow_smooth", "encode_video"],
    "rating": 4,
    "outputs": ["experiments/exp_001/final.mp4"]
  }
}
```

---

## 7. Implementation Phases

### Phase 1: Core Pipeline (Week 1)
- YAML workflow parser
- Workflow engine (step execution)
- Basic experiment tracking
- 2-3 essential steps (extract frames, ControlNet, encode video)

### Phase 2: Step Library (Week 2)
- Add pose extraction steps (MediaPipe, MoveNet)
- Add stylization steps (AnimateDiff, SD-Video)
- Add temporal steps (optical flow, interpolation)

### Phase 3: Comparison Tools (Week 3)
- Config diff utility
- Video comparison viewer
- Search/filter experiments

### Phase 4: Polish (Week 4)
- Better error handling
- Step caching (reuse intermediate outputs)
- Performance optimization
- Documentation

---

## 8. Success Criteria

✓ Define custom workflows in YAML
✓ Mix and match steps in any order
✓ Run experiments with one command
✓ Auto-track all experiments and outputs
✓ Compare experiments visually and by config
✓ Reproduce any experiment exactly
✓ Easy to add new processing steps

---

## 9. Example Usage

```bash
# Create experiment config
cat > experiments/exp_010.yaml <<EOF
experiment_id: exp_010
tags: [test, sketch]
workflow:
  - step: extract_frames
    params: {input: data/inputs/dance.mp4}
  - step: controlnet_stylize
    params: {prompt: "pencil sketch"}
  - step: encode_video
EOF

# Run it
python run.py experiments/exp_010.yaml

# Review results
ls experiments/exp_010/outputs/

# Compare with previous
python compare.py exp_008 exp_010

# Clone and modify for next experiment
cp experiments/exp_010.yaml experiments/exp_011.yaml
# Edit prompt, re-run
```

---

## Next Steps

1. Implement YAML workflow parser
2. Build workflow execution engine
3. Create first 3 steps (frame extraction, ControlNet, video encoding)
4. Test end-to-end experiment
5. Add experiment tracking and indexing

Ready to build! 🎬
