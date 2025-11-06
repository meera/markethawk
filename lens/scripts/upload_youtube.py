#!/usr/bin/env python3
"""
Upload earnings call video to YouTube with comprehensive metadata.
Includes chapter markers, description, hashtags, and all extracted insights.
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment
load_dotenv()

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
except ImportError:
    print("❌ Error: Google API client not installed")
    print("Install: pip install google-api-python-client google-auth-oauthlib")
    sys.exit(1)


SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


def get_youtube_client():
    """Get authenticated YouTube API client."""

    creds = None
    token_file = Path.home() / '.youtube_token.json'

    # Load existing credentials
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Need to run OAuth flow with client secret file
            client_secret_file = os.getenv('YOUTUBE_CLIENT_SECRET_FILE')

            if not client_secret_file:
                raise ValueError("YOUTUBE_CLIENT_SECRET_FILE required in .env")

            if not Path(client_secret_file).exists():
                raise ValueError(f"Client secret file not found: {client_secret_file}")

            # Use the official client secrets file
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_file,
                SCOPES
            )
            creds = flow.run_local_server(port=8080)

        # Save credentials for future use
        with open(token_file, 'w') as f:
            f.write(creds.to_json())

    return build('youtube', 'v3', credentials=creds)


def upload_video(video_path: str, insights_path: str, metadata_path: str = None) -> Dict:
    """
    Upload video to YouTube with comprehensive metadata.

    Args:
        video_path: Path to video file
        insights_path: Path to insights.json
        metadata_path: Path to metadata.json (optional)

    Returns:
        Dictionary with upload results including video ID and URL
    """

    # Load insights
    with open(insights_path, 'r') as f:
        insights = json.load(f)

    metadata_info = insights['metadata']
    youtube_info = insights.get('youtube', {})

    # Build title
    title = metadata_info.get('title', 'Earnings Call')

    # Build description (with chapter markers)
    description = youtube_info.get('description', metadata_info.get('description', ''))

    # Tags
    tags = youtube_info.get('tags', [])
    if not tags:
        # Default tags
        tags = [
            metadata_info.get('ticker', ''),
            metadata_info.get('company', ''),
            metadata_info.get('quarter', ''),
            str(metadata_info.get('year', '')),
            'earnings call',
            'investor relations',
            'financial results'
        ]
        tags = [t for t in tags if t]  # Remove empty

    # Category: 28 = Science & Technology
    # Or 25 = News & Politics (for financial news)
    category_id = "25"

    # Request body
    request_body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': 'public',  # or 'unlisted' or 'private'
            'selfDeclaredMadeForKids': False
        }
    }

    # Upload video
    print(f"📤 Uploading video to YouTube...")
    print(f"   Title: {title}")
    print(f"   Tags: {len(tags)} tags")
    print(f"   Chapters: {len(insights.get('chapters', []))} chapters")

    youtube = get_youtube_client()

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype='video/*')

    request = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            print(f"   Uploading: {progress}%")

    video_id = response['id']
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    print(f"✓ Video uploaded successfully!")
    print(f"   Video ID: {video_id}")
    print(f"   URL: {video_url}")

    return {
        'video_id': video_id,
        'url': video_url,
        'title': title,
        'uploaded_at': response.get('snippet', {}).get('publishedAt')
    }


def main():
    parser = argparse.ArgumentParser(
        description="Upload earnings call video to YouTube with metadata"
    )
    parser.add_argument("video", help="Path to video file")
    parser.add_argument("insights", help="Path to insights.json")
    parser.add_argument("--metadata", help="Path to metadata.json (optional)")

    args = parser.parse_args()

    try:
        result = upload_video(args.video, args.insights, args.metadata)

        print("\n" + "="*50)
        print("Upload complete!")
        print("="*50)
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
