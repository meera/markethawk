# Answer to Your Question

> "Explain how step has same parameters and output from one are wired to next step.
> Specially when youtubedownload will have say source.mp4 as output and that may get
> piped to ffmpeg make frames that will make it as frame1.jpg, frame2.jpg etc.."

## The Answer in 3 Parts

### Part 1: Steps Return Dictionaries (Not Files!)

**Important:** Steps don't "pipe" data. They return **paths to files** in a dictionary.

```python
# flipbook/steps/download_video.py
def process(self, **params):
    # ... downloads video to disk ...
    video_path = "data/inputs/iYsOFDa4DDU.mp4"  # File saved to disk

    return {
        'output': video_path,  # ← Returns PATH, not the video file itself!
        'video_id': 'iYsOFDa4DDU'
    }
```

The step **writes the file to disk** and **returns the path**.

---

### Part 2: Workflow Engine Stores Paths in Memory

```python
# flipbook/workflow.py:78-79
output = step_instance.process(**params)
# output = {'output': 'data/inputs/iYsOFDa4DDU.mp4', 'video_id': 'iYsOFDa4DDU'}

self.step_outputs['download'] = output
# Now we have the path stored in memory
```

**In memory:**
```python
step_outputs = {
    'download': {
        'output': 'data/inputs/iYsOFDa4DDU.mp4',  # ← Path to file
        'video_id': 'iYsOFDa4DDU'
    }
}
```

**On disk:**
```
data/inputs/iYsOFDa4DDU.mp4  ← Actual video file
```

---

### Part 3: Next Step Gets the Path

```yaml
# YAML says:
- step: extract_frames
  params:
    input: ${download.output}
```

**Workflow engine resolves it:**
```python
# Before: params = {'input': '${download.output}'}
# After:  params = {'input': 'data/inputs/iYsOFDa4DDU.mp4'}
```

**Extract frames receives the path:**
```python
# flipbook/steps/extract_frames.py
def process(self, **params):
    input_path = params['input']  # 'data/inputs/iYsOFDa4DDU.mp4'

    # Read the file from disk
    cmd = ['ffmpeg', '-i', input_path, ...]  # ffmpeg reads from disk
    subprocess.run(cmd)

    # Write frames to disk
    # experiments/exp_001/frames/frame_0001.jpg
    # experiments/exp_001/frames/frame_0002.jpg
    # ...

    return {
        'output': 'experiments/exp_001/frames',  # ← Path to frames directory
        'frame_count': 360
    }
```

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: download_video                                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Downloads video from YouTube                                       │
│  Writes to: data/inputs/iYsOFDa4DDU.mp4  ← FILE ON DISK            │
│                                                                     │
│  Returns: {'output': 'data/inputs/iYsOFDa4DDU.mp4'}  ← JUST PATH   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
                 Workflow engine stores in memory
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ MEMORY: step_outputs                                                │
├─────────────────────────────────────────────────────────────────────┤
│  {                                                                  │
│    'download': {                                                    │
│      'output': 'data/inputs/iYsOFDa4DDU.mp4'  ← PATH STORED        │
│    }                                                                │
│  }                                                                  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
               YAML reference gets resolved
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ YAML: - step: extract_frames                                        │
│         params:                                                     │
│           input: ${download.output}                                 │
│                       ↓                                             │
│                  Resolves to                                        │
│                       ↓                                             │
│           input: 'data/inputs/iYsOFDa4DDU.mp4'  ← PATH INJECTED   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
                 extract_frames.process() called
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: extract_frames                                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Receives: input = 'data/inputs/iYsOFDa4DDU.mp4'  ← PATH AS STRING │
│                                                                     │
│  Reads file from disk: data/inputs/iYsOFDa4DDU.mp4                 │
│                                                                     │
│  Runs: ffmpeg -i data/inputs/iYsOFDa4DDU.mp4 ...                   │
│                                                                     │
│  Writes frames to disk:                                             │
│    experiments/exp_001/frames/frame_0001.jpg  ← FILES ON DISK      │
│    experiments/exp_001/frames/frame_0002.jpg                        │
│    ...                                                              │
│    experiments/exp_001/frames/frame_0360.jpg                        │
│                                                                     │
│  Returns: {                                                         │
│    'output': 'experiments/exp_001/frames',  ← DIRECTORY PATH       │
│    'frame_count': 360                                               │
│  }                                                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Key Points

### 1. No Piping - Files Written to Disk

Unlike Unix pipes (`cat file.txt | grep foo`), steps don't stream data.

**Each step:**
1. Reads files from disk (using paths from previous steps)
2. Processes them
3. Writes results to disk
4. Returns paths to the results

### 2. The "Wiring" is Just String Replacement

```python
# YAML reference
input: ${download.output}

# Gets replaced with
input: 'data/inputs/iYsOFDa4DDU.mp4'

# That's it! Just string substitution.
```

### 3. Steps Communicate via File Paths

```
download_video → Returns: 'data/inputs/video.mp4'
                          ↓
                    (stored in memory)
                          ↓
                    ${download.output}
                          ↓
                    'data/inputs/video.mp4'
                          ↓
extract_frames ← Receives: 'data/inputs/video.mp4'
```

### 4. Actual Data Lives on Disk

```
DISK:                           MEMORY (step_outputs):
─────────────                   ────────────────────────
data/inputs/                    {
  iYsOFDa4DDU.mp4  ←───────────   'download': {
                                     'output': 'data/inputs/iYsOFDa4DDU.mp4'
experiments/exp_001/                }
  frames/          ←───────────   'frames': {
    frame_0001.jpg                   'output': 'experiments/exp_001/frames'
    frame_0002.jpg                 }
    ...                          }
```

**Files = on disk** (the actual data)
**Paths = in memory** (how steps find the files)

---

## Analogy

Think of it like a treasure hunt:

1. **Step 1** hides treasure (downloads video)
   - Returns map: "Treasure is at data/inputs/video.mp4"

2. **Workflow engine** remembers the map
   - Stores: step_outputs['download']['output'] = 'data/inputs/video.mp4'

3. **Step 2** uses the map (extracts frames)
   - Receives: "Go to data/inputs/video.mp4"
   - Finds the file and processes it
   - Hides new treasure (frames)
   - Returns new map: "New treasure at experiments/exp_001/frames"

The workflow engine is just a **map keeper**!

---

## Summary

**Your question:** How does source.mp4 get "piped" to ffmpeg?

**Answer:** It doesn't get piped!

1. download_video **writes** source.mp4 to disk
2. download_video **returns the path** in a dict
3. Workflow engine **stores the path** in memory
4. YAML reference `${download.output}` gets **replaced with the path**
5. extract_frames **receives the path** as a string parameter
6. extract_frames **reads the file** from disk using that path
7. ffmpeg processes it and **writes frames** to disk
8. extract_frames **returns paths** to those frames

**The "wiring" = passing file paths as strings!**

---

Read **DATAFLOW-EXPLAINED.md** for even more detail with examples!
