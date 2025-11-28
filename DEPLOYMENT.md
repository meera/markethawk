# Deployment Architecture: Code vs Data Separation

## Principle: Code in Home, Data in /var

**This is the CORRECT and RECOMMENDED approach.**

### Directory Structure

```
~/markethawk/                    ← CODE (git-tracked)
├── lens/                         ← Python pipeline scripts
│   ├── process_earnings.py      ← Main orchestrator
│   ├── transcribe.py
│   ├── extract_insights.py
│   └── scripts/
│       ├── download-source.py
│       ├── parse-metadata.py
│       ├── remove-silence.py
│       └── upload-youtube.py
├── .env                          ← Environment config
├── .gitignore                    ← Excludes .env, data
└── README.md

/var/markethawk/                 ← DATA (not in git)
├── _downloads/                   ← Permanent archive
│   └── <video_id>/
│       └── input/
│           ├── source.mp4
│           └── metadata.json
├── AAPL/                         ← Organized by company
│   └── Q4-2024/
│       ├── input/                ← Shared inputs
│       │   └── source.mp4
│       ├── transcripts/
│       │   ├── transcript.json
│       │   └── insights.json
│       ├── take1/                ← Separate takes
│       │   └── final.mp4
│       └── take2/
└── PLTR/
    └── Q3-2024/
```

## Why This Works

### ✅ Benefits

1. **Git-Friendly**
   - Repo stays small (no large video files)
   - Only code, docs, config tracked
   - .gitignore prevents accidental data commits

2. **Cross-Platform**
   ```bash
   # Mac
   cd ~/markethawk          # Run scripts here
   ls /var/markethawk       # Data via samba mount

   # Linux (GPU machine)
   cd ~/markethawk          # Same scripts
   ls /var/markethawk       # Data on local disk
   ```

3. **Standard Unix Convention**
   - `/var` = variable data (logs, caches, uploads, etc.)
   - `~` = user-specific code and config
   - Follows FHS (Filesystem Hierarchy Standard)

4. **Easy Backups**
   - Code: `git push` (automatic)
   - Data: Separate backup strategy (rsync, snapshots)

5. **Scalable**
   - Data can grow to TB without affecting repo
   - Can mount /var from NAS, SAN, or network storage

### ⚠️ Requirements

1. **Mac: Samba Mount**
   ```bash
   # Use Finder: Cmd+K, then enter:
   # smb://192.168.1.101/markethawk

   # Finder will mount to /Volumes/markethawk-1 (or -2, etc.)
   # After mounting, update symlink:
   sudo rm -f /var/markethawk
   sudo ln -s /Volumes/markethawk-1 /var/markethawk

   # Verify:
   ls -la /var/markethawk/_downloads

   # Note: Mounts don't survive restart - remount after each reboot
   ```

2. **Linux: Fix Permissions on Server (IMPORTANT)**
   ```bash
   # SSH into Linux GPU machine and fix ownership
   ssh meera@192.168.1.101
   sudo mkdir -p /var/markethawk/_downloads
   sudo chown -R meera:meera /var/markethawk
   exit

   # Now Mac can write to the mount
   ```

3. **Environment Variables**
   ```bash
   # .env (in ~/markethawk/.env)
   DOWNLOADS_DIR="/var/markethawk/_downloads"
   ORGANIZED_DIR="/var/markethawk"
   ```

## Running Scripts

### Always Run from Project Root

```bash
# ✅ CORRECT - Run from root
cd ~/markethawk
source .venv/bin/activate
python lens/process_earnings.py --url "https://youtube.com/..."

# ❌ WRONG - Don't cd into subdirectories
cd ~/markethawk/lens
python process_earnings.py --url "..."

# ❌ WRONG - Don't run from /var
cd /var/markethawk
python ~/markethawk/lens/process_earnings.py
```

### Why?

- **Consistency:** Working directory is always `~/markethawk/`
- **Environment:** `.env` is in `~/markethawk/.env` and `python-dotenv` loads from working directory
- **Clarity:** All paths are relative to project root
- **Data paths:** Scripts write to `/var/markethawk` via `DOWNLOADS_DIR` and `ORGANIZED_DIR`

## Workflow Example

```bash
# 1. Work on code (Mac or Linux)
cd ~/markethawk
git pull
vim lens/process_earnings.py
git commit -m "Update pipeline"
git push

# 2. Run pipeline from root (writes to /var)
cd ~/markethawk
source .venv/bin/activate
python lens/process_earnings.py --url "https://youtube.com/..."

# 3. Output goes to /var
ls /var/markethawk/_downloads/jUnV3LiN0_k/
ls /var/markethawk/PLTR/Q3-2024/

# 4. Code stays clean
cd ~/markethawk
git status
# → Only code changes, no video files
```

## Mount Check

Scripts automatically verify `/var/markethawk` is accessible:

```python
# process_earnings.py
if not ORGANIZED_DIR.parent.exists():
    print("ERROR: /var/markethawk not accessible")
    print("On Mac: Ensure samba mount is connected")
    print("On Linux: Ensure /var/markethawk directory exists")
    sys.exit(1)
```

## After Mac Restart

SMB mounts **don't survive restart**. After each reboot:

```bash
# 1. Mount via Finder: Cmd+K → smb://192.168.1.101/markethawk

# 2. Check what Finder mounted it as:
mount | grep markethawk
# Example: //meera@192.168.1.101/markethawk on /Volumes/markethawk-1

# 3. Update symlink to match:
sudo rm -f /var/markethawk
sudo ln -s /Volumes/markethawk-1 /var/markethawk  # Use whatever number Finder chose

# 4. Verify:
ls -la /var/markethawk/_downloads

# 5. Resume work:
cd ~/markethawk
source .venv/bin/activate
python lens/process_earnings.py --url "..."
```

**Why the number changes:** macOS creates an empty `/Volumes/markethawk` directory, so Finder adds `-1`, `-2`, etc. This is normal behavior.

---

## Summary

**Code:** `~/markethawk/` (git-tracked, portable, small)
**Data:** `/var/markethawk/` → `/Volumes/markethawk-1` (SMB mount, not tracked)
**Run from:** `~/markethawk/` (ALWAYS - never cd into subdirectories)

This is the **recommended architecture** and should not be changed.

---

**Last Updated:** November 5, 2024
