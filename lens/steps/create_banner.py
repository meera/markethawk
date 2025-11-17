"""
Create Banner - Create static banner image for video background
"""

from pathlib import Path
from typing import Dict, Any
from PIL import Image, ImageDraw, ImageFont


def create_banner(job_dir: Path, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create static banner image with company info (for video background)

    Args:
        job_dir: Job directory path
        job_data: Job data dict

    Returns:
        Result dict with banner path
    """
    # Get confirmed metadata
    confirmed_meta = job_data.get('processing', {}).get('confirm_metadata', {}).get('confirmed', {})

    if not confirmed_meta:
        raise ValueError("No confirmed metadata found. Run 'confirm_metadata' step first.")

    company_name = confirmed_meta.get('company')
    ticker = confirmed_meta.get('ticker')
    quarter = confirmed_meta.get('quarter')
    year = confirmed_meta.get('year')

    # Create renders directory
    renders_dir = job_dir / "renders"
    renders_dir.mkdir(parents=True, exist_ok=True)

    # Output path
    banner_path = renders_dir / "banner.png"

    # Image dimensions (1920x1080)
    width, height = 1920, 1080

    # Create image with dark background
    img = Image.new('RGB', (width, height), color='#1a1a2e')
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fall back to default
    try:
        # Try common font paths
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 80)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Calculate text positions (centered)
    # Company name (top)
    company_bbox = draw.textbbox((0, 0), company_name, font=font_large)
    company_width = company_bbox[2] - company_bbox[0]
    company_x = (width - company_width) // 2
    company_y = height // 3

    # Earnings call text
    earnings_text = f"{quarter} {year} Earnings Call"
    earnings_bbox = draw.textbbox((0, 0), earnings_text, font=font_medium)
    earnings_width = earnings_bbox[2] - earnings_bbox[0]
    earnings_x = (width - earnings_width) // 2
    earnings_y = company_y + 150

    # Ticker (bottom)
    ticker_bbox = draw.textbbox((0, 0), ticker, font=font_small)
    ticker_width = ticker_bbox[2] - ticker_bbox[0]
    ticker_x = (width - ticker_width) // 2
    ticker_y = earnings_y + 120

    # Draw text
    draw.text((company_x, company_y), company_name, fill='#ffffff', font=font_large)
    draw.text((earnings_x, earnings_y), earnings_text, fill='#e94560', font=font_medium)
    draw.text((ticker_x, ticker_y), ticker, fill='#0f3460', font=font_small)

    # Save image
    img.save(banner_path)
    print(f"📸 Banner image created: {banner_path.name}")
    print(f"   Size: {width}x{height}")
    print(f"   Company: {company_name}")
    print(f"   Ticker: {ticker}")
    print(f"   Quarter: {quarter} {year}")

    return {
        'banner_path': str(banner_path),
        'width': width,
        'height': height,
        'format': 'png'
    }
