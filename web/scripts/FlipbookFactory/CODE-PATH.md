# Code Execution Path - Line by Line

This shows **exactly** what code executes when you run:
```bash
python run.py experiments/exp_001.yaml
```

---

## Phase 1: Startup

### run.py:48-56
```python
workflow = load_workflow(config_path, experiment_dir)
```
↓

### flipbook/workflow.py:197-200
```python
def load_workflow(config_path, experiment_dir):
    return WorkflowEngine(config_path, experiment_dir)
```
↓

### flipbook/workflow.py:25-30
```python
def __init__(self, config_path, experiment_dir):
    self.config_path = Path(config_path)
    self.experiment_dir = Path(experiment_dir)
    self.config = self._load_config()  # Loads YAML
    self.step_outputs = {}             # Empty dict for storing outputs
```

**State after init:**
```python
workflow = WorkflowEngine(
    config_path="experiments/exp_001.yaml",
    experiment_dir="experiments/exp_001",
    step_outputs={}  # ← Empty, will be filled as steps run
)
```

---

## Phase 2: Execute Workflow

### run.py:57
```python
result = workflow.run()
```
↓

### flipbook/workflow.py:42-56
```python
def run(self):
    workflow_steps = self.config['workflow']  # List of step definitions
    results = []

    for i, step_def in enumerate(workflow_steps, 1):
        # Process each step...
```

---

## Phase 3: First Step (download_video)

### workflow.py:58-60
```python
step_name = step_def.get('step')      # "download_video"
step_id = step_def.get('id', step_name)  # "download"
params = step_def.get('params', {})   # {'url': 'https://...'}
```

### workflow.py:67
```python
resolved_params = self._resolve_params(params, step_id)
```
↓

### workflow.py:102-110
```python
def _resolve_params(self, params, current_step_id):
    resolved = {}
    for key, value in params.items():
        if isinstance(value, str) and '${' in value:
            resolved[key] = self._resolve_reference(value, current_step_id)
        else:
            resolved[key] = value  # No reference, use as-is
    return resolved
```

**For first step, no references to resolve:**
```python
resolved_params = {'url': 'https://www.youtube.com/shorts/iYsOFDa4DDU'}
```

### workflow.py:70-72
```python
step_instance = StepRegistry.create(step_name, self.experiment_dir)
# Creates an instance of DownloadVideo class
```
↓

### flipbook/step.py:100-107
```python
@classmethod
def create(cls, name, experiment_dir):
    step_class = cls.get(name)  # Get DownloadVideo class
    if step_class:
        return step_class(experiment_dir=experiment_dir)
```

**Now we have:**
```python
step_instance = DownloadVideo(experiment_dir="experiments/exp_001")
```

### workflow.py:75
```python
output = step_instance.process(**resolved_params)
# Calls: DownloadVideo.process(url='https://...')
```
↓

### flipbook/steps/download_video.py:40-108
```python
def process(self, **params):
    url_or_id = params.get('url')  # 'https://www.youtube.com/shorts/iYsOFDa4DDU'
    video_id = self._extract_video_id(url_or_id)  # 'iYsOFDa4DDU'

    # Download the video...
    video_path = output_dir / f"{video_id}.mp4"
    # video_path = Path("data/inputs/iYsOFDa4DDU.mp4")

    self._download_file(mp4_url, video_path)

    return {
        'output': str(video_path),  # "data/inputs/iYsOFDa4DDU.mp4"
        'video_id': video_id,
        'metadata_path': str(metadata_path),
        'metadata': {...}
    }
```

**Step returns:**
```python
output = {
    'output': 'data/inputs/iYsOFDa4DDU.mp4',
    'video_id': 'iYsOFDa4DDU',
    'metadata_path': 'data/inputs/iYsOFDa4DDU_metadata.json',
    'metadata': {'title': '...', 'duration': 15, 'file_size_mb': 3.2}
}
```

### workflow.py:78-79
```python
self.step_outputs[step_id] = output     # step_outputs['download'] = {...}
self.step_outputs['prev'] = output      # step_outputs['prev'] = {...}
```

**State now:**
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
        # ... same as above
    }
}
```

---

## Phase 4: Second Step (extract_frames)

### workflow.py:58-60 (second iteration)
```python
step_name = "extract_frames"
step_id = "frames"
params = {
    'input': '${download.output}',  # ← Reference to previous step!
    'fps': 24
}
```

### workflow.py:67
```python
resolved_params = self._resolve_params(params, step_id)
```
↓

### workflow.py:102-110
```python
def _resolve_params(self, params, current_step_id):
    resolved = {}
    for key, value in params.items():
        # key='input', value='${download.output}'
        if isinstance(value, str) and '${' in value:  # TRUE!
            resolved[key] = self._resolve_reference(value, current_step_id)
        else:
            # key='fps', value=24
            resolved[key] = value
    return resolved
```

**For 'input' key, resolve the reference:**
↓

### workflow.py:127-165
```python
def _resolve_reference(self, reference, current_step_id):
    # reference = '${download.output}'

    # Extract "download.output" from "${download.output}"
    pattern = r'\$\{([^}]+)\}'
    matches = re.findall(pattern, reference)  # ['download.output']

    for match in matches:  # match = 'download.output'
        parts = match.split('.')  # ['download', 'output']
        step_id = parts[0]        # 'download'
        path = parts[1:]          # ['output']

        # Get from memory
        value = self.step_outputs[step_id]
        # value = {'output': 'data/inputs/iYsOFDa4DDU.mp4', 'video_id': ..., ...}

        # Navigate to 'output' key
        for key in path:  # key = 'output'
            value = value.get(key)
        # value = 'data/inputs/iYsOFDa4DDU.mp4'

        # Replace ${download.output} with actual value
        result = reference.replace(f'${{{match}}}', str(value))
        # result = 'data/inputs/iYsOFDa4DDU.mp4'

    return result
```

**After resolution:**
```python
resolved_params = {
    'input': 'data/inputs/iYsOFDa4DDU.mp4',  # ← Resolved!
    'fps': 24
}
```

### workflow.py:70-75
```python
step_instance = StepRegistry.create("extract_frames", experiment_dir)
# Creates ExtractFrames instance

output = step_instance.process(**resolved_params)
# Calls: ExtractFrames.process(input='data/inputs/iYsOFDa4DDU.mp4', fps=24)
```
↓

### flipbook/steps/extract_frames.py:38-85
```python
def process(self, **params):
    input_path = Path(params.get('input'))
    # input_path = Path('data/inputs/iYsOFDa4DDU.mp4')

    fps = params.get('fps')  # 24

    # Build ffmpeg command
    output_pattern = output_dir / "frame_%04d.jpg"
    cmd = ['ffmpeg', '-i', str(input_path), '-vf', f'fps={fps}', str(output_pattern)]

    # Execute
    subprocess.run(cmd, ...)

    # Creates:
    #   experiments/exp_001/frames/frame_0001.jpg
    #   experiments/exp_001/frames/frame_0002.jpg
    #   ...
    #   experiments/exp_001/frames/frame_0360.jpg

    frames = sorted(output_dir.glob("frame_*.jpg"))
    frame_count = len(frames)  # 360

    return {
        'output': str(output_dir),      # "experiments/exp_001/frames"
        'frame_count': frame_count,     # 360
        'fps': fps,                     # 24
        'first_frame': str(frames[0]),
        'last_frame': str(frames[-1])
    }
```

**Step returns:**
```python
output = {
    'output': 'experiments/exp_001/frames',
    'frame_count': 360,
    'fps': 24,
    'first_frame': 'experiments/exp_001/frames/frame_0001.jpg',
    'last_frame': 'experiments/exp_001/frames/frame_0360.jpg'
}
```

### workflow.py:78-79
```python
self.step_outputs[step_id] = output     # step_outputs['frames'] = {...}
self.step_outputs['prev'] = output      # step_outputs['prev'] = {...} (updated)
```

**Final state:**
```python
self.step_outputs = {
    'download': {
        'output': 'data/inputs/iYsOFDa4DDU.mp4',
        'video_id': 'iYsOFDa4DDU',
        'metadata_path': 'data/inputs/iYsOFDa4DDU_metadata.json',
        'metadata': {...}
    },
    'frames': {
        'output': 'experiments/exp_001/frames',
        'frame_count': 360,
        'fps': 24,
        'first_frame': 'experiments/exp_001/frames/frame_0001.jpg',
        'last_frame': 'experiments/exp_001/frames/frame_0360.jpg'
    },
    'prev': {
        'output': 'experiments/exp_001/frames',
        'frame_count': 360,
        # ... same as 'frames'
    }
}
```

---

## Phase 5: Save Results

### run.py:61-67
```python
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
```

**Creates: experiments/exp_001/metadata.json**

---

## Summary: The Key Insight

### The "Wiring" Happens in 3 Places:

1. **Storage** (workflow.py:78-79)
   ```python
   self.step_outputs[step_id] = output
   ```
   Every step's return value is stored in a dictionary

2. **Reference Detection** (workflow.py:105-107)
   ```python
   if isinstance(value, str) and '${' in value:
       resolved[key] = self._resolve_reference(value, current_step_id)
   ```
   Finds `${...}` patterns in YAML params

3. **Resolution** (workflow.py:138-165)
   ```python
   value = self.step_outputs[step_id]  # Look up in memory
   for key in path:
       value = value.get(key)          # Navigate to the key
   ```
   Replaces `${download.output}` with actual value from memory

### No Magic - Just Dictionary Lookups!

```python
# What YAML says:
input: ${download.output}

# What Python does:
input = self.step_outputs['download']['output']

# Result:
input = 'data/inputs/iYsOFDa4DDU.mp4'
```

That's it! The entire "wiring" system is just storing dictionaries and doing string replacement.
