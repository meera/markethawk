# YouTube Thumbnail Generator

Automatically generates professional YouTube thumbnails for MarketHawk earnings call videos.

## Features

- **Professional Design**: Gradient background with modern styling
- **Company Branding**: Company name, ticker symbol prominently displayed
- **Earnings Info**: Quarter, fiscal year, and call date
- **MarketHawk Badge**: Branded logo in bottom-right corner
- **YouTube Optimized**: 1280x720 resolution, JPEG format, ~100KB file size

## Thumbnail Elements

The thumbnail includes:
1. **Company Name** - Large, centered at top (e.g., "Apple Inc.")
2. **Ticker Symbol** - In parentheses, blue color (e.g., "(AAPL)")
3. **Quarter & Year** - Highlighted yellow box (e.g., "Q4 2024")
4. **Event Date** - Formatted date (e.g., "Earnings Call • Nov 01, 2024")
5. **MarketHawk Logo** - Bottom-right corner with branding

## Usage

### Standalone Script

```bash
# Generate thumbnail from video data JSON
python generate_thumbnail.py <data_json_path> <output_path>

# Example
python generate_thumbnail.py ../studio/data/AAPL-Q4-2024.json output/aapl-thumbnail.jpg
```

### Integrated in Video Pipeline

```bash
# Process video WITH thumbnail generation
python process_video.py uploads/video.mp4 medium gpt-4o-mini ../studio/data/AAPL-Q4-2024.json

# Process video WITHOUT thumbnail
python process_video.py uploads/video.mp4 medium gpt-4o-mini
```

## Input Data Format

The script expects a JSON file with the following structure:

```json
{
  "company": "Apple Inc.",
  "ticker": "AAPL",
  "quarter": "Q4",
  "fiscal_year": 2024,
  "call_date": "2024-11-01"
}
```

**Required Fields:**
- `company` - Company name (string)
- `ticker` - Stock ticker symbol (string)
- `quarter` - Fiscal quarter (string, e.g., "Q1", "Q2", "Q3", "Q4")
- `fiscal_year` - Fiscal year (number)
- `call_date` - Call date in YYYY-MM-DD format (string)

## Output

- **Resolution**: 1280x720 (YouTube standard)
- **Format**: JPEG
- **Quality**: 95% (optimized)
- **File Size**: ~80-120 KB
- **Naming**: `{video_filename}.thumbnail.jpg`

## Examples

### AAPL Q4 2024

```bash
python generate_thumbnail.py ../studio/data/AAPL-Q4-2024.json /tmp/aapl-q4-2024-thumbnail.jpg
```

Output:
```
✅ Thumbnail generated successfully: /tmp/aapl-q4-2024-thumbnail.jpg
   Resolution: 1280x720
   Company: Apple Inc. (AAPL)
   Period: Q4 2024
   Date: Nov 01, 2024
```

### Integration Example

Full pipeline with thumbnail:

```bash
# 1. Download video
python scripts/download-youtube.py jUnV3LiN0_k

# 2. Process video (transcribe, insights, thumbnail)
python sushi/process_video.py \
  uploads/jUnV3LiN0_k.mp4 \
  medium \
  gpt-4o-mini \
  studio/data/AAPL-Q4-2024.json

# Output files:
# - uploads/jUnV3LiN0_k.json (transcript)
# - uploads/jUnV3LiN0_k.srt (subtitles)
# - uploads/jUnV3LiN0_k.vtt (captions)
# - uploads/jUnV3LiN0_k.txt (plain text)
# - uploads/jUnV3LiN0_k.paragraphs.json (structured)
# - uploads/jUnV3LiN0_k.insights.json (LLM insights)
# - uploads/jUnV3LiN0_k.thumbnail.jpg (thumbnail) ✨
```

## Customization

### Modify Colors

Edit `generate_thumbnail.py`:

```python
# Background gradient
create_gradient_background(
    width, height,
    (15, 23, 42),   # Dark blue (change this)
    (30, 41, 59)    # Darker blue (change this)
)

# Text colors
white = (255, 255, 255)      # Company name
blue = (96, 165, 250)        # Ticker symbol
yellow = (250, 204, 21)      # Quarter box
```

### Modify Layout

Edit position variables in `generate_thumbnail()`:

```python
company_y = 180        # Company name Y position
ticker_y = company_y + 130   # Ticker Y offset
quarter_y = ticker_y + 110   # Quarter Y offset
```

### Change Resolution

```python
# Generate custom size
generate_thumbnail(data, output_path, width=1920, height=1080)
```

## Dependencies

- **Pillow** >= 10.0.0 (Python Imaging Library)

Install:
```bash
pip install Pillow>=10.0.0
```

## Troubleshooting

### Font Issues

If fonts are not rendering correctly:

```bash
# Install DejaVu fonts (Ubuntu/Debian)
sudo apt-get install fonts-dejavu-core

# Verify fonts installed
ls /usr/share/fonts/truetype/dejavu/
```

The script will fallback to default fonts if DejaVu is not available.

### Missing Data Fields

If required fields are missing from JSON:

```python
# Script will use defaults:
company_name = data.get('company', 'Unknown Company')
ticker = data.get('ticker', '')
quarter = data.get('quarter', 'Q4')
fiscal_year = data.get('fiscal_year', 2024)
```

### File Permissions

If output directory doesn't exist:

```bash
# Script automatically creates directories
os.makedirs(output_dir, exist_ok=True)
```

## Design Rationale

### Why These Elements?

1. **Company Name Large** - Immediate recognition
2. **Ticker in Parentheses** - Quick investor identification
3. **Quarter Highlighted** - Visual emphasis on reporting period
4. **Date Included** - Temporal context
5. **MarketHawk Badge** - Brand awareness, trust signal

### Why This Layout?

- **Centered Design** - Readable on all devices (mobile, desktop, TV)
- **Gradient Background** - Professional, modern look
- **High Contrast** - Text readable in YouTube thumbnails (small preview)
- **Minimal Text** - Focus on key info, not overwhelming
- **Logo Bottom-Right** - Standard position, doesn't obstruct main content

## Future Enhancements

Potential improvements:

- [ ] Company logo integration (download from API)
- [ ] Dynamic color schemes per industry
- [ ] Performance indicators (revenue up/down arrows)
- [ ] Multiple thumbnail variants (A/B testing)
- [ ] Template system for different video types

## License

Part of MarketHawk project.
