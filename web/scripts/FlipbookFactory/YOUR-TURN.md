# Your Turn - Run the Experiment!

## What You've Built

You now have a **complete workflow system** that:
1. ✅ Downloads videos from YouTube
2. ✅ Extracts frames using ffmpeg
3. ✅ Connects steps via YAML references
4. ✅ Tracks experiments automatically
5. ✅ Provides debugging tools

## Step-by-Step Instructions

### 1. Setup Environment

```bash
# You are here: /home/meera/FlipbookFactory

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify ffmpeg is installed
ffmpeg -version
```

### 2. Understand the System (Optional but Recommended)

Read these in order:
1. **QUICK-REFERENCE.md** - 5 min read, core concepts
2. **DATAFLOW-EXPLAINED.md** - 10 min read, detailed walkthrough
3. **CODE-PATH.md** - Reference when you want to see exact code flow

### 3. Run Your First Experiment

```bash
# This will:
# 1. Download https://www.youtube.com/shorts/iYsOFDa4DDU
# 2. Extract frames at 24fps
# 3. Save everything to experiments/exp_001/

python run.py experiments/exp_001.yaml
```

**Expected output:**
```
============================================================
🎬 Running Experiment: exp_001
📝 Download YouTube Short and extract frames
🏷️  Tags: test, download, frames
============================================================

[Step 1/2] download_video
────────────────────────────────────────────────────────────
📹 Video ID: iYsOFDa4DDU
📡 Fetching video details from RapidAPI...
📄 Metadata saved: data/inputs/iYsOFDa4DDU_metadata.json
✅ Selected: 720p MP4 with audio
⬇️  Downloading video...
Progress: 100.0% (3.2 MB / 3.2 MB)
✅ Downloaded: [Video Title]
   Size: 3.2 MB, Duration: 15s

[Step 2/2] extract_frames
────────────────────────────────────────────────────────────
📹 Extracting frames from: iYsOFDa4DDU.mp4
📁 Output directory: experiments/exp_001/frames
🎞️  Target FPS: 24
⚙️  Running ffmpeg...
✅ Extracted 360 frames
   Format: JPG, Quality: 2

============================================================
✅ Workflow completed successfully!
============================================================
```

### 4. Explore the Results

```bash
# See what was created
ls -lh data/inputs/
ls -lh experiments/exp_001/

# Count the frames
ls experiments/exp_001/frames/ | wc -l
# Should show 360 frames (15 seconds * 24 fps)

# View a frame
open experiments/exp_001/frames/frame_0001.jpg  # macOS
# or: xdg-open experiments/exp_001/frames/frame_0001.jpg  # Linux

# Read the metadata
cat experiments/exp_001/metadata.json | jq .

# Add your observations
nano experiments/exp_001/notes.md
```

### 5. See the Data Flow (Learning Mode)

```bash
# Run in debug mode to see exactly how data flows
python debug_workflow.py experiments/exp_001.yaml
```

**This shows:**
- Raw params from YAML
- What's in memory (step_outputs)
- Reference resolution (${download.output} → actual path)
- What each step returns

### 6. Experiment!

#### Experiment A: Different Frame Rate

```bash
# Create a new experiment
cp experiments/exp_001.yaml experiments/exp_002.yaml

# Edit exp_002.yaml, change:
#   fps: 24  →  fps: 12

# Run it
python run.py experiments/exp_002.yaml

# Compare
ls experiments/exp_001/frames/ | wc -l  # 360 frames
ls experiments/exp_002/frames/ | wc -l  # 180 frames (half!)
```

#### Experiment B: PNG Format

```yaml
# experiments/exp_003.yaml
experiment_id: exp_003
description: "Extract as PNG instead of JPG"
tags: [test, png]

workflow:
  - step: download_video
    id: download
    params:
      url: https://www.youtube.com/shorts/iYsOFDa4DDU

  - step: extract_frames
    params:
      input: ${download.output}
      fps: 24
      format: png  # ← Changed from jpg
```

```bash
python run.py experiments/exp_003.yaml
```

#### Experiment C: Different Video

```yaml
# experiments/exp_004.yaml
experiment_id: exp_004
description: "Try a different video"
tags: [test]

workflow:
  - step: download_video
    id: download
    params:
      url: <paste a different YouTube Short URL>

  - step: extract_frames
    params:
      input: ${download.output}
      fps: 24
```

### 7. Understanding What You Built

**The key insight:**

```python
# Steps are DECOUPLED
# download_video.py does NOT import extract_frames.py
# extract_frames.py does NOT import download_video.py

# They're connected by the workflow engine via YAML:
params:
  input: ${download.output}  # ← This is the "wiring"
```

**This means:**
1. You can add new steps without modifying existing ones
2. You can use steps in any order
3. You can create any workflow combination

**Example - If you later add a `upscale` step:**
```yaml
workflow:
  - step: download_video
    id: download

  - step: extract_frames
    id: frames
    params: {input: ${download.output}}

  - step: upscale           # New step!
    params: {input: ${frames.output}}

  - step: encode_video      # Another new step!
    params: {input: ${upscale.output}}
```

No code changes needed! Just define steps, use them in YAML.

---

## Next Steps

### Phase 1 Complete! ✅

You now have:
- ✅ YAML workflow system
- ✅ Step registry pattern
- ✅ Data flow via references
- ✅ Experiment tracking
- ✅ 2 working steps (download, extract_frames)

### Phase 2: Add More Steps

Pick one to implement:

#### Option A: Video Encoding Step
Create `flipbook/steps/encode_video.py`:
- Takes frames directory
- Uses ffmpeg to create video
- Returns video path

#### Option B: Simple Filter Step
Create `flipbook/steps/resize_frames.py`:
- Takes frames directory
- Resizes each frame
- Returns new frames directory

#### Option C: Pose Detection Step
Create `flipbook/steps/mediapipe_pose.py`:
- Takes video or frames
- Extracts pose landmarks
- Returns pose data JSON

**Follow the pattern:**
1. Copy `extract_frames.py` as template
2. Modify `process()` method
3. Register with `@StepRegistry.register`
4. Import in `flipbook/steps/__init__.py`
5. Use in YAML!

---

## Questions to Explore

1. **What happens if you reference a step that hasn't run yet?**
   ```yaml
   - step: extract_frames
     params: {input: ${future_step.output}}  # Error!
   ```

2. **Can you reference nested data?**
   ```yaml
   params: {title: ${download.metadata.title}}  # Yes!
   ```

3. **What if two steps have the same ID?**
   ```yaml
   - step: download_video
     id: download  # ← Second one overwrites first in memory
   - step: download_video
     id: download  # ← This one wins
   ```

4. **Can you use multiple references in one param?**
   ```yaml
   params:
     combined: "${download.video_id}_${frames.frame_count}"
   # Result: "iYsOFDa4DDU_360"
   ```

Try these! Break things! That's how you learn.

---

## Getting Help

**If something fails:**

1. Read the error message carefully
2. Check the YAML syntax
3. Run in debug mode: `python debug_workflow.py ...`
4. Look at the step's source code
5. Check what the step returns (the dict)

**Common issues:**

```bash
# "Step not found"
python list_steps.py  # Check registered steps

# "File not found"
# Check that previous step actually created the file
ls -la data/inputs/
ls -la experiments/exp_001/frames/

# "Reference not found"
# Make sure step ID matches what you're referencing
# ${download.output} requires a step with id: download
```

---

## You're Ready!

Run the experiment and see your workflow system in action. You've built something powerful - a **composable, modular pipeline system** that can handle any video processing workflow you dream up.

The principles you learned here (Step pattern, Registry pattern, Reference resolution) are used in:
- Apache Airflow (data pipelines)
- GitHub Actions (CI/CD workflows)
- AWS Step Functions (cloud workflows)
- Prefect/Dagster (ML pipelines)

You just built a mini version of these professional tools!

Now go run that experiment! 🚀

```bash
python run.py experiments/exp_001.yaml
```
