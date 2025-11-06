# Deployment Architecture: Code vs Data Separation

## Principle: Code in Home, Data in /var

**This is the CORRECT and RECOMMENDED approach.**

### Directory Structure

```
~/earninglens/                    ← CODE (git-tracked)
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

/var/earninglens/                 ← DATA (not in git)
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
   cd ~/earninglens          # Run scripts here
   ls /var/earninglens       # Data via samba mount

   # Linux (GPU machine)
   cd ~/earninglens          # Same scripts
   ls /var/earninglens       # Data on local disk
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
   # smb://192.168.1.101/earninglens

   # Finder will mount to /Volumes/earninglens-1 (or -2, etc.)
   # After mounting, update symlink:
   sudo rm -f /var/earninglens
   sudo ln -s /Volumes/earninglens-1 /var/earninglens

   # Verify:
   ls -la /var/earninglens/_downloads

   # Note: Mounts don't survive restart - remount after each reboot
   ```

2. **Linux: Fix Permissions on Server (IMPORTANT)**
   ```bash
   # SSH into Linux GPU machine and fix ownership
   ssh meera@192.168.1.101
   sudo mkdir -p /var/earninglens/_downloads
   sudo chown -R meera:meera /var/earninglens
   exit

   # Now Mac can write to the mount
   ```

3. **Environment Variables**
   ```bash
   # .env (in ~/earninglens/.env)
   DOWNLOADS_DIR="/var/earninglens/_downloads"
   ORGANIZED_DIR="/var/earninglens"
   ```

## Running Scripts

### Always Run from Project Root

```bash
# ✅ CORRECT - Run from root
cd ~/earninglens
source .venv/bin/activate
python lens/process_earnings.py --url "https://youtube.com/..."

# ❌ WRONG - Don't cd into subdirectories
cd ~/earninglens/lens
python process_earnings.py --url "..."

# ❌ WRONG - Don't run from /var
cd /var/earninglens
python ~/earninglens/lens/process_earnings.py
```

### Why?

- **Consistency:** Working directory is always `~/earninglens/`
- **Environment:** `.env` is in `~/earninglens/.env` and `python-dotenv` loads from working directory
- **Clarity:** All paths are relative to project root
- **Data paths:** Scripts write to `/var/earninglens` via `DOWNLOADS_DIR` and `ORGANIZED_DIR`

## Workflow Example

```bash
# 1. Work on code (Mac or Linux)
cd ~/earninglens
git pull
vim lens/process_earnings.py
git commit -m "Update pipeline"
git push

# 2. Run pipeline from root (writes to /var)
cd ~/earninglens
source .venv/bin/activate
python lens/process_earnings.py --url "https://youtube.com/..."

# 3. Output goes to /var
ls /var/earninglens/_downloads/jUnV3LiN0_k/
ls /var/earninglens/PLTR/Q3-2024/

# 4. Code stays clean
cd ~/earninglens
git status
# → Only code changes, no video files
```

## Mount Check

Scripts automatically verify `/var/earninglens` is accessible:

```python
# process_earnings.py
if not ORGANIZED_DIR.parent.exists():
    print("ERROR: /var/earninglens not accessible")
    print("On Mac: Ensure samba mount is connected")
    print("On Linux: Ensure /var/earninglens directory exists")
    sys.exit(1)
```

## After Mac Restart

SMB mounts **don't survive restart**. After each reboot:

```bash
# 1. Mount via Finder: Cmd+K → smb://192.168.1.101/earninglens

# 2. Check what Finder mounted it as:
mount | grep earninglens
# Example: //meera@192.168.1.101/earninglens on /Volumes/earninglens-1

# 3. Update symlink to match:
sudo rm -f /var/earninglens
sudo ln -s /Volumes/earninglens-1 /var/earninglens  # Use whatever number Finder chose

# 4. Verify:
ls -la /var/earninglens/_downloads

# 5. Resume work:
cd ~/earninglens
source .venv/bin/activate
python lens/process_earnings.py --url "..."
```

**Why the number changes:** macOS creates an empty `/Volumes/earninglens` directory, so Finder adds `-1`, `-2`, etc. This is normal behavior.

---

## Summary

**Code:** `~/earninglens/` (git-tracked, portable, small)
**Data:** `/var/earninglens/` → `/Volumes/earninglens-1` (SMB mount, not tracked)
**Run from:** `~/earninglens/` (ALWAYS - never cd into subdirectories)

This is the **recommended architecture** and should not be changed.

---

**Last Updated:** November 5, 2024
