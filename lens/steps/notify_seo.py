"""
Notify Search Engines - Trigger sitemap update notification (production only)
"""

import os
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Load environment variables
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from env_loader import get_r2_bucket_name


def notify_seo(job_dir: Path, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Notify Google and Bing search engines of new earnings call page

    Only runs in production (DEV_MODE=false). Skips in development.

    Args:
        job_dir: Job directory path
        job_data: Job data dict

    Returns:
        Result dict with notification status
    """
    # Check if we're in production mode
    dev_mode = os.getenv('DEV_MODE', 'true').lower() == 'true'

    if dev_mode:
        print("⏭️  Skipping SEO notification (DEV_MODE=true)")
        return {
            'skipped': True,
            'reason': 'Development mode - SEO notifications disabled',
            'dev_mode': True
        }

    # Get company info
    confirmed = job_data.get('processing', {}).get('confirm_metadata', {}).get('confirmed', {})
    company = job_data.get('company', {})

    ticker = confirmed.get('ticker') or company.get('ticker')
    quarter = confirmed.get('quarter') or company.get('quarter')
    year = confirmed.get('year') or company.get('year')

    # Get company slug from match_company step
    match_result = job_data.get('processing', {}).get('match_company', {})
    company_match = match_result.get('company_match', {})
    slug = company_match.get('slug', '')

    if not slug:
        print("⚠️  Warning: No company slug found, cannot generate earnings URL")
        return {
            'skipped': True,
            'reason': 'No company slug available',
            'dev_mode': False
        }

    # Generate earnings call URL
    # Format: /earnings/{slug}/q{quarter}-{year}
    # Example: /earnings/nvidia/q3-2026
    quarter_lower = quarter.lower() if quarter else 'q1'
    earnings_url = f"https://markethawkeye.com/earnings/{slug}/{quarter_lower}-{year}"

    print(f"🔔 Notifying search engines of new earnings call...")
    print(f"   URL: {earnings_url}")

    # Get webhook secret
    webhook_secret = os.getenv('SEO_SITEMAP_WEBHOOK_SECRET')
    if not webhook_secret:
        print("⚠️  Warning: SEO_SITEMAP_WEBHOOK_SECRET not set")
        return {
            'skipped': True,
            'reason': 'SEO_SITEMAP_WEBHOOK_SECRET not configured',
            'dev_mode': False
        }

    # Call post-deploy webhook
    webhook_url = "https://markethawkeye.com/api/post-deploy"

    try:
        response = requests.post(
            webhook_url,
            headers={
                'Authorization': f'Bearer {webhook_secret}',
                'Content-Type': 'application/json'
            },
            json={
                'newUrls': [earnings_url]
            },
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

        print(f"✅ Search engines notified successfully")
        print(f"   Google: ✓")
        print(f"   Bing: ✓")
        print(f"   Sitemap: {result.get('sitemap', 'N/A')}")

        return {
            'notified': True,
            'earnings_url': earnings_url,
            'sitemap_url': result.get('sitemap'),
            'response': result,
            'notified_at': datetime.now().isoformat()
        }

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to notify search engines: {e}")

        # Don't fail the pipeline, just log the error
        return {
            'notified': False,
            'error': str(e),
            'earnings_url': earnings_url,
            'attempted_at': datetime.now().isoformat()
        }
