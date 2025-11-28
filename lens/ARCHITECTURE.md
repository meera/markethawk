# Architecture: Function + Main Pattern

All scripts follow a dual-use pattern: they can be called **standalone** OR **imported as functions**.

## Pattern Overview

```python
# my_script.py

def my_function(arg1: str, arg2: int) -> dict:
    """
    Main processing function that can be imported.

    Args:
        arg1: Description
        arg2: Description

    Returns:
        Dictionary with results
    """
    # Do the work
    result = process(arg1, arg2)
    return result


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument("arg1", help="...")
    parser.add_argument("--arg2", type=int, default=10)

    args = parser.parse_args()

    try:
        result = my_function(args.arg1, args.arg2)
        print(f"Success: {result}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## Usage

### As Standalone Script
```bash
python my_script.py input_value --arg2 20
```

### As Imported Function
```python
from my_script import my_function

result = my_function("input_value", 20)
print(result)
```

---

## Implementation in MarketHawk

### 1. download-source.py

**Function:**
```python
def download_video(url: str, downloads_dir: str = "/var/markethawk/_downloads") -> Dict:
    """Download video from YouTube URL"""
    # Returns: {file_path, metadata_path, title, description, ...}
```

**Usage:**
```python
# Standalone
python scripts/download-source.py "https://youtube.com/..."

# Imported
from scripts.download_source import download_video
result = download_video("https://youtube.com/...")
```

### 2. parse-metadata.py

**Function:**
```python
def parse_video_metadata(metadata_path: str) -> Dict:
    """Parse metadata to extract company and quarter"""
    # Returns: {ticker, quarter, company_name, confidence, ...}
```

**Usage:**
```python
# Standalone
python scripts/parse-metadata.py /path/to/metadata.json

# Imported
from scripts.parse_metadata import parse_video_metadata
result = parse_video_metadata("/path/to/metadata.json")
```

### 3. remove-silence.py

**Function:**
```python
def remove_silence(input_path: str, output_path: str,
                   threshold: str = "-50dB", min_duration: float = 0.5) -> dict:
    """Remove initial silence from video"""
    # Returns: {silence_duration, input_size_mb, output_size_mb, ...}
```

**Usage:**
```python
# Standalone
python scripts/remove-silence.py input.mp4 output.mp4

# Imported
from scripts.remove_silence import remove_silence
result = remove_silence("input.mp4", "output.mp4")
```

---

## Main Orchestrator

The `process_earnings.py` orchestrator **imports functions directly**:

```python
# Import functions
from scripts.download_source import download_video
from scripts.parse_metadata import parse_video_metadata
from scripts.remove_silence import remove_silence as remove_silence_func

class EarningsProcessor:
    def step_download(self):
        # Call function directly (no subprocess)
        result = download_video(self.url, str(DOWNLOADS_DIR))

    def step_parse(self):
        # Call function directly
        result = parse_video_metadata(str(metadata_file))

    def step_remove_silence(self):
        # Call function directly
        result = remove_silence_func(str(source_file), str(trimmed_file))
```

**Benefits:**
- ✅ Faster (no subprocess overhead)
- ✅ Better error handling (native exceptions)
- ✅ Type safety (can use type hints)
- ✅ Easier debugging (direct stack traces)
- ✅ Can still run scripts standalone for testing

---

## Scripts That Use Subprocess

Some scripts **still use subprocess** because they don't have importable functions yet:

```python
def step_transcribe(self):
    # Uses subprocess (for now)
    script = PIPELINE_DIR / "transcribe.py"
    self._run_python_script(script, [str(input_file), "--output", str(output_file)])

def step_insights(self):
    # Uses subprocess (for now)
    script = PIPELINE_DIR / "extract_insights.py"
    self._run_python_script(script, [str(transcript_file), "--output", str(output_file)])
```

**To refactor later:**
- Add `transcribe_video()` function to `transcribe.py`
- Add `extract_insights()` function to `process_video.py`
- Import and call directly in orchestrator

---

## Testing Pattern

### Test Standalone
```bash
cd ~/markethawk/sushi

# Test download
python scripts/download-source.py "https://youtube.com/..."

# Test parse
python scripts/parse-metadata.py /var/markethawk/_downloads/jUnV3LiN0_k/input/metadata.json

# Test silence removal
python scripts/remove-silence.py input.mp4 output.mp4
```

### Test Imported
```python
# test_pipeline.py
from scripts.download_source import download_video
from scripts.parse_metadata import parse_video_metadata
from scripts.remove_silence import remove_silence

# Test download
result = download_video("https://youtube.com/...")
assert result['file_path']

# Test parse
result = parse_video_metadata("/path/to/metadata.json")
assert result['ticker'] == "PLTR"

# Test silence removal
result = remove_silence("input.mp4", "output.mp4")
assert result['silence_duration'] >= 0
```

---

## Migration Guide

To convert an existing script to this pattern:

### Before (Old)
```python
def main():
    # Parse args
    # Do work
    # Print result

if __name__ == "__main__":
    main()
```

### After (New)
```python
def my_function(arg1, arg2):
    """Importable function"""
    # Do work
    return result

def main():
    # Parse args
    result = my_function(args.arg1, args.arg2)
    # Print result

if __name__ == "__main__":
    main()
```

**Steps:**
1. Extract core logic into a function
2. Add type hints and docstring
3. Make main() call the function
4. Update orchestrator to import function

---

## Best Practices

1. **Functions should be pure** - No global state, no side effects (except file I/O)
2. **Return dictionaries** - Easy to serialize, extend, and debug
3. **Raise exceptions** - Don't sys.exit() in functions, let caller handle errors
4. **Type hints** - Makes imports clearer and enables IDE autocomplete
5. **Docstrings** - Explain args and return values

---

**Last Updated:** November 5, 2024
