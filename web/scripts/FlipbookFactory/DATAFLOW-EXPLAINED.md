# Data Flow Between Steps - Complete Example

## The Question
How does `source.mp4` from download_video get passed to extract_frames?

## The Answer: Return Values + References

### Step 1: download_video Returns a Dictionary

```python
# flipbook/steps/download_video.py:108-117
def process(self, **params):
    # ... download logic ...
    video_path = output_dir / f"{video_id}.mp4"
    # e.g., video_path = "data/inputs/iYsOFDa4DDU.mp4"

    return {
        'output': str(video_path),           # ← THE KEY PART
        'video_id': video_id,
        'metadata_path': str(metadata_path),
        'metadata': {
            'title': title,
            'duration': duration,
            'file_size_mb': round(file_size, 2)
        }
    }
```

**Return value example:**
```python
{
    'output': 'data/inputs/iYsOFDa4DDU.mp4',    # ← This is the path to the video
    'video_id': 'iYsOFDa4DDU',
    'metadata_path': 'data/inputs/iYsOFDa4DDU_metadata.json',
    'metadata': {
        'title': 'Some YouTube Short',
        'duration': 15,
        'file_size_mb': 3.2
    }
}
```

---

### Step 2: Workflow Engine Stores This Output

```python
# flipbook/workflow.py:85-93
output = step_instance.process(**resolved_params)

# Store output for later steps to reference
self.step_outputs[step_id] = output      # ← Stored with ID "download"
self.step_outputs['prev'] = output       # ← Also stored as "prev"
```

**What's in memory now:**
```python
self.step_outputs = {
    'download': {
        'output': 'data/inputs/iYsOFDa4DDU.mp4',
        'video_id': 'iYsOFDa4DDU',
        'metadata_path': 'data/inputs/iYsOFDa4DDU_metadata.json',
        'metadata': {...}
    },
    'prev': {
        'output': 'data/inputs/iYsOFDa4DDU.mp4',
        'video_id': 'iYsOFDa4DDU',
        # ... same as above
    }
}
```

---

### Step 3: YAML References Get Resolved

**Your YAML says:**
```yaml
- step: extract_frames
  params:
    input: ${download.output}    # ← This reference needs to be resolved
    fps: 24
```

**The workflow engine resolves it:**
```python
# flipbook/workflow.py:102-110
def _resolve_params(self, params, current_step_id):
    resolved = {}
    for key, value in params.items():
        if isinstance(value, str) and '${' in value:
            # Found a reference! Resolve it
            resolved[key] = self._resolve_reference(value, current_step_id)
        else:
            resolved[key] = value
    return resolved
```

**Specific resolution of `${download.output}`:**
```python
# flipbook/workflow.py:127-150
def _resolve_reference(self, reference, current_step_id):
    # reference = "${download.output}"

    # Extract: "download.output"
    match = "download.output"

    # Parse: step_id="download", path=["output"]
    parts = match.split('.')
    step_id = "download"      # parts[0]
    path = ["output"]         # parts[1:]

    # Get the step's output from memory
    value = self.step_outputs["download"]
    # value = {'output': 'data/inputs/iYsOFDa4DDU.mp4', 'video_id': ..., ...}

    # Navigate to the 'output' key
    for key in path:  # path = ["output"]
        value = value.get(key)
    # value = 'data/inputs/iYsOFDa4DDU.mp4'

    return value  # Returns the actual file path string!
```

**After resolution, params become:**
```python
{
    'input': 'data/inputs/iYsOFDa4DDU.mp4',    # ← Resolved from ${download.output}
    'fps': 24
}
```

---

### Step 4: extract_frames Receives the Path

```python
# flipbook/steps/extract_frames.py:38-45
def process(self, **params):
    self.params = params

    # Get parameters
    input_path = Path(params.get('input'))
    # input_path = Path('data/inputs/iYsOFDa4DDU.mp4')

    if not input_path or not input_path.exists():
        raise ValueError(f"Input video not found: {input_path}")
```

**Now extract_frames has the path to the video file!**

---

### Step 5: extract_frames Processes and Returns

```python
# flipbook/steps/extract_frames.py:70-85
def process(self, **params):
    # ... processing logic ...

    # Build ffmpeg command
    output_pattern = output_dir / f"frame_%04d.jpg"
    # output_pattern = "experiments/exp_001/frames/frame_%04d.jpg"

    cmd = ['ffmpeg', '-i', str(input_path)]  # input_path is the video
    cmd.extend(['-vf', f'fps={fps}'])
    cmd.append(str(output_pattern))

    # Execute ffmpeg
    subprocess.run(cmd, ...)

    # Count frames
    frames = sorted(output_dir.glob(f"frame_*.jpg"))
    frame_count = len(frames)

    return {
        'output': str(output_dir),           # ← Path to frames directory
        'frame_count': frame_count,
        'fps': fps,
        'first_frame': str(frames[0]),       # e.g., "experiments/exp_001/frames/frame_0001.jpg"
        'last_frame': str(frames[-1])
    }
```

**Return value example:**
```python
{
    'output': 'experiments/exp_001/frames',
    'frame_count': 360,
    'fps': 24,
    'first_frame': 'experiments/exp_001/frames/frame_0001.jpg',
    'last_frame': 'experiments/exp_001/frames/frame_0360.jpg'
}
```

---

## Visual Flow Diagram

```
YAML Config:
┌─────────────────────────────────────────────────────────────┐
│ - step: download_video                                      │
│   id: download                                              │
│   params:                                                   │
│     url: https://youtube.com/shorts/iYsOFDa4DDU            │
└─────────────────────────────────────────────────────────────┘
                           ↓
Workflow Engine runs download_video.process()
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ download_video returns:                                     │
│ {                                                           │
│   'output': 'data/inputs/iYsOFDa4DDU.mp4',                │
│   'video_id': 'iYsOFDa4DDU',                              │
│   'metadata': {...}                                         │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
Workflow Engine stores in self.step_outputs['download']
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Memory:                                                     │
│ step_outputs = {                                            │
│   'download': {                                             │
│     'output': 'data/inputs/iYsOFDa4DDU.mp4',              │
│     ...                                                     │
│   }                                                         │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
YAML Config:
┌─────────────────────────────────────────────────────────────┐
│ - step: extract_frames                                      │
│   params:                                                   │
│     input: ${download.output}  ← Reference!                │
│     fps: 24                                                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
Workflow Engine resolves ${download.output}
                           ↓
Looks up: step_outputs['download']['output']
Returns: 'data/inputs/iYsOFDa4DDU.mp4'
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Resolved params:                                            │
│ {                                                           │
│   'input': 'data/inputs/iYsOFDa4DDU.mp4',  ← Resolved!    │
│   'fps': 24                                                 │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
Workflow Engine runs extract_frames.process(**resolved_params)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ extract_frames.process() receives:                          │
│ - input = 'data/inputs/iYsOFDa4DDU.mp4'                   │
│ - fps = 24                                                  │
│                                                             │
│ Runs: ffmpeg -i data/inputs/iYsOFDa4DDU.mp4 -vf fps=24 ... │
│                                                             │
│ Creates:                                                    │
│   experiments/exp_001/frames/frame_0001.jpg                 │
│   experiments/exp_001/frames/frame_0002.jpg                 │
│   ...                                                       │
│   experiments/exp_001/frames/frame_0360.jpg                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ extract_frames returns:                                     │
│ {                                                           │
│   'output': 'experiments/exp_001/frames',                  │
│   'frame_count': 360,                                       │
│   'fps': 24                                                 │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
Workflow Engine stores in self.step_outputs['frames']
```

---

## Key Teaching Points

### 1. **Steps Return Dictionaries**
Every step **must** return a dictionary. The workflow engine doesn't care what's in it, but by convention:
- `'output'` key contains the main result (usually a file path)
- Other keys contain metadata

### 2. **The `output` Key Convention**
It's not enforced by code, but **by convention**, steps should put their main result in `'output'`:
```python
return {
    'output': 'path/to/main/result',  # ← This is what ${prev.output} references
    'other_data': 'can be anything'
}
```

### 3. **References Use Dot Notation**
```yaml
${step_id.output}           # Gets step_outputs['step_id']['output']
${step_id.metadata.title}   # Gets step_outputs['step_id']['metadata']['title']
${prev.output}              # Gets the previous step's output
```

### 4. **You Can Reference ANY Part of the Return Value**
```yaml
# If download_video returns:
# {
#   'output': 'data/inputs/iYsOFDa4DDU.mp4',
#   'video_id': 'iYsOFDa4DDU',
#   'metadata': {'title': 'My Video', 'duration': 15}
# }

# You can reference:
${download.output}              # → 'data/inputs/iYsOFDa4DDU.mp4'
${download.video_id}            # → 'iYsOFDa4DDU'
${download.metadata.title}      # → 'My Video'
${download.metadata.duration}   # → 15
```

### 5. **Steps Don't Know About Each Other**
```python
# download_video.py DOES NOT import extract_frames
# extract_frames.py DOES NOT import download_video

# They're completely decoupled!
# The workflow engine connects them via the YAML config
```

---

## Example: Chaining 3 Steps

```yaml
workflow:
  - step: download_video
    id: dl
    params:
      url: https://youtube.com/...

  - step: extract_frames
    id: frames
    params:
      input: ${dl.output}        # Gets the video path
      fps: 24

  - step: some_future_step
    params:
      frames_dir: ${frames.output}      # Gets the frames directory
      frame_count: ${frames.frame_count} # Gets the count
      original_video: ${dl.output}      # Can reference earlier steps too!
```

**What happens in memory:**
```python
# After step 1:
step_outputs = {
    'dl': {'output': 'data/inputs/video.mp4', ...}
}

# After step 2:
step_outputs = {
    'dl': {'output': 'data/inputs/video.mp4', ...},
    'frames': {'output': 'experiments/exp_001/frames', 'frame_count': 360, ...}
}

# Step 3 can reference BOTH previous steps!
```

---

## Common Patterns

### Pattern 1: Sequential Processing (prev)
```yaml
workflow:
  - step: download_video
    params: {url: "..."}

  - step: extract_frames
    params: {input: ${prev.output}}  # Use previous step

  - step: upscale_frames
    params: {input: ${prev.output}}  # Use previous step again
```

### Pattern 2: Branching (named IDs)
```yaml
workflow:
  - step: download_video
    id: download
    params: {url: "..."}

  - step: extract_frames
    id: frames
    params: {input: ${download.output}}

  - step: extract_audio
    id: audio
    params: {input: ${download.output}}  # Also uses download

  - step: combine
    params:
      frames: ${frames.output}
      audio: ${audio.output}
```

### Pattern 3: Pass Multiple Values
```yaml
- step: stylize
  params:
    frames: ${extract.output}
    fps: ${extract.fps}                    # Pass the FPS too
    title: ${download.metadata.title}      # Even metadata!
```

---

## TL;DR

1. **Steps return dictionaries** with file paths and metadata
2. **Workflow engine stores** these dictionaries in memory
3. **YAML references** like `${step_id.key}` get replaced with actual values
4. **Next step receives** the resolved values as regular parameters
5. **Steps are decoupled** - connected only through the workflow YAML

The "magic" is just **dictionary storage + string substitution**!
