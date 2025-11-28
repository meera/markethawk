# Quick Reference - Data Flow Between Steps

## The Three Key Concepts

### 1. Steps Return Dictionaries
```python
# Every step MUST return a dict
def process(self, **params):
    # ... do work ...
    return {
        'output': 'path/to/result',  # Main result
        'metadata': {...}             # Extra info
    }
```

### 2. Workflow Engine Stores Outputs
```python
# After each step runs:
self.step_outputs[step_id] = return_value

# Example after download_video:
self.step_outputs = {
    'download': {
        'output': 'data/inputs/video.mp4',
        'video_id': 'ABC123'
    }
}
```

### 3. YAML References Get Resolved
```yaml
# YAML syntax
params:
  input: ${download.output}

# Gets replaced with
params:
  input: 'data/inputs/video.mp4'
```

---

## Reference Syntax

```yaml
${prev.output}              # Previous step's 'output' key
${step_id.output}           # Specific step's 'output' key
${step_id.metadata.title}   # Nested access: step_id['metadata']['title']
${download.video_id}        # Any key from the return dict
```

---

## Complete Example

### YAML Config
```yaml
workflow:
  - step: download_video
    id: dl
    params:
      url: https://youtube.com/...
    # Returns: {'output': 'data/inputs/ABC123.mp4', 'video_id': 'ABC123'}

  - step: extract_frames
    id: frames
    params:
      input: ${dl.output}      # Resolved to 'data/inputs/ABC123.mp4'
      fps: 24
    # Returns: {'output': 'exp_001/frames', 'frame_count': 360}

  - step: some_step
    params:
      frames: ${frames.output}       # 'exp_001/frames'
      count: ${frames.frame_count}   # 360
      video: ${dl.output}            # 'data/inputs/ABC123.mp4'
```

### What's in Memory (step_outputs)

```python
# After step 1:
{
  'dl': {'output': 'data/inputs/ABC123.mp4', 'video_id': 'ABC123'},
  'prev': {'output': 'data/inputs/ABC123.mp4', 'video_id': 'ABC123'}
}

# After step 2:
{
  'dl': {'output': 'data/inputs/ABC123.mp4', 'video_id': 'ABC123'},
  'frames': {'output': 'exp_001/frames', 'frame_count': 360},
  'prev': {'output': 'exp_001/frames', 'frame_count': 360}
}
```

---

## Common Patterns

### Sequential Chain (use prev)
```yaml
workflow:
  - step: download_video
  - step: extract_frames
    params: {input: ${prev.output}}
  - step: upscale
    params: {input: ${prev.output}}
```

### Branching (use IDs)
```yaml
workflow:
  - step: download_video
    id: dl

  - step: extract_frames
    params: {input: ${dl.output}}

  - step: extract_audio
    params: {input: ${dl.output}}  # Also uses download
```

### Access Nested Data
```yaml
- step: some_step
  params:
    title: ${download.metadata.title}
    duration: ${download.metadata.duration}
    fps: ${frames.fps}
```

---

## Debugging

### See the data flow
```bash
python debug_workflow.py experiments/exp_001.yaml
```

### Check what a step returns
```python
# Look at the step code
# flipbook/steps/download_video.py:108-117

return {
    'output': str(video_path),     # ← This is what ${step.output} gives you
    'video_id': video_id,           # ← This is what ${step.video_id} gives you
    'metadata': {...}               # ← This is what ${step.metadata} gives you
}
```

### Print step_outputs during execution
```python
# In flipbook/workflow.py:78-79, add:
print(f"DEBUG: step_outputs = {self.step_outputs}")
```

---

## Rules of Thumb

1. **Always return a dict** from step.process()
2. **Put main result in 'output' key** (convention)
3. **Use descriptive step IDs** in YAML for clarity
4. **${prev.output}** for sequential processing
5. **${id.key}** for branching or skipping steps

---

## Files to Read

1. **DATAFLOW-EXPLAINED.md** - Detailed walkthrough
2. **CODE-PATH.md** - Line-by-line execution trace
3. **flipbook/workflow.py:127-165** - Reference resolution logic
4. **flipbook/steps/download_video.py:108-117** - Example return value
5. **experiments/exp_001.yaml** - Example workflow config
