# FlipbookFactory

AI Video-to-Flipbook Experimentation Playground

## Learning Resources

**New to this project? Start here:**
- **[QUICK-REFERENCE.md](QUICK-REFERENCE.md)** - Data flow cheat sheet
- **[DATAFLOW-EXPLAINED.md](DATAFLOW-EXPLAINED.md)** - How steps pass data (detailed)
- **[CODE-PATH.md](CODE-PATH.md)** - Line-by-line execution trace

**Debugging:**
```bash
python debug_workflow.py experiments/exp_001.yaml  # See data flow in action
python list_steps.py                                # List available steps
```

---

## Quick Start

### 1. Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Ensure ffmpeg is installed (for frame extraction)
ffmpeg -version
```

### 2. Run Your First Experiment

```bash
# Run the first experiment (download + extract frames)
python run.py experiments/exp_001.yaml
```

This will:
1. Download the YouTube Short to `data/inputs/`
2. Extract frames at 24fps to `experiments/exp_001/frames/`
3. Save metadata and config to `experiments/exp_001/`

## How It Works

### Step-Based Architecture

Every operation is a **Step** - a reusable, configurable processing unit:

```python
# flipbook/steps/download_video.py
@StepRegistry.register
class DownloadVideo(Step):
    def process(self, **params) -> Dict[str, Any]:
        # Download logic here
        return {'output': 'path/to/video.mp4', ...}
```

**Key concepts:**
- **Modular**: Each step does one thing well
- **Reusable**: Steps can be used in any workflow
- **Trackable**: Parameters and outputs are automatically saved
- **Registered**: `@StepRegistry.register` makes steps available in YAML

### YAML Workflows

Define experiments as pipelines in YAML:

```yaml
experiment_id: exp_001
description: "Download YouTube Short and extract frames"
tags: [test, download, frames]

workflow:
  - step: download_video
    id: download
    params:
      url: https://www.youtube.com/shorts/iYsOFDa4DDU

  - step: extract_frames
    params:
      input: ${download.output}  # Reference previous step output
      fps: 24
```

**Parameter references:**
- `${prev.output}` - Output from previous step
- `${step_id.output}` - Output from specific step
- `${download.metadata.title}` - Nested access

### Experiment Tracking

Each experiment auto-creates:
```
experiments/exp_001/
├── config.yaml          # Workflow definition (copied for reproducibility)
├── metadata.json        # Execution results and timestamps
├── notes.md            # Your observations
└── frames/             # Step outputs
    ├── frame_0001.jpg
    ├── frame_0002.jpg
    └── ...
```

## Available Steps

### download_video
Download video from YouTube using RapidAPI.

**Parameters:**
- `url` (required): YouTube URL or video ID
- `output_dir`: Where to save (default: `data/inputs`)
- `overwrite`: Overwrite existing file (default: `false`)

**Returns:**
- `output`: Path to downloaded video
- `video_id`: YouTube video ID
- `metadata`: Title, duration, file size

### extract_frames
Extract frames from video using ffmpeg.

**Parameters:**
- `input` (required): Path to video file
- `output_dir`: Where to save frames (default: auto-generated)
- `fps`: Frames per second (default: native fps)
- `format`: Output format - `jpg` or `png` (default: `jpg`)
- `quality`: JPEG quality 1-31, lower is better (default: `2`)

**Returns:**
- `output`: Path to frames directory
- `frame_count`: Number of frames extracted
- `fps`: Actual FPS used

## Creating New Steps

1. Create a new file in `flipbook/steps/`:

```python
# flipbook/steps/my_step.py
from flipbook.step import Step, StepRegistry

@StepRegistry.register
class MyStep(Step):
    """
    Description of what this step does.

    Parameters:
        input: Description
        param1: Description

    Returns:
        output: Description
    """

    def process(self, **params):
        self.params = params

        # Your processing logic
        input_path = params['input']
        result = do_something(input_path)

        return {
            'output': result,
            'metadata': {...}
        }
```

2. Import it in `flipbook/steps/__init__.py`:

```python
from flipbook.steps.my_step import MyStep
```

3. Use it in YAML:

```yaml
workflow:
  - step: my_step
    params:
      input: ${prev.output}
      param1: value
```

## Tips for Learning

### Understanding the Flow

1. **YAML defines what to do** (`experiments/exp_001.yaml`)
2. **WorkflowEngine reads YAML** and executes steps (`flipbook/workflow.py`)
3. **Each Step processes data** and returns outputs (`flipbook/steps/`)
4. **Outputs are referenced** by later steps using `${...}` syntax
5. **Everything is tracked** in experiment directory

### Experiment

Try modifying `exp_001.yaml`:

```yaml
# Extract at different FPS
- step: extract_frames
  params:
    input: ${download.output}
    fps: 12  # Half the frames

# Try PNG format
- step: extract_frames
  params:
    input: ${download.output}
    format: png
```

### Build Incrementally

Start simple, add complexity:
1. ✅ Download + extract frames (you are here!)
2. Add pose detection step
3. Add stylization step
4. Add video encoding step
5. Compare results

## Project Structure

```
FlipbookFactory/
├── data/
│   └── inputs/              # Downloaded videos
├── experiments/             # Experiment configs and outputs
│   ├── exp_001.yaml
│   └── exp_001/
│       ├── config.yaml
│       ├── metadata.json
│       ├── notes.md
│       └── frames/
├── flipbook/               # Core package
│   ├── __init__.py
│   ├── step.py            # Base Step class and registry
│   ├── workflow.py        # Workflow execution engine
│   └── steps/             # Step implementations
│       ├── __init__.py
│       ├── download_video.py
│       └── extract_frames.py
├── run.py                 # Main runner script
├── requirements.txt
└── README.md
```

## Next Steps

See [PRD.md](PRD.md) for the full vision and implementation phases.

**Phase 1 (Complete):**
- ✅ YAML workflow parser
- ✅ Workflow execution engine
- ✅ Basic experiment tracking
- ✅ 2 essential steps (download, extract_frames)

**Phase 2 (Next):**
- Add pose extraction steps (MediaPipe, MoveNet)
- Add stylization steps (ControlNet, AnimateDiff)
- Add video encoding step

**Phase 3:**
- Config diff utility
- Video comparison viewer
- Search/filter experiments
