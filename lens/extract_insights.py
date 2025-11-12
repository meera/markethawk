#!/usr/bin/env python3
"""
Comprehensive insights extraction for earnings call transcripts.
Extracts speakers, entities, highlights, TOC, and generates YouTube metadata.

Based on VideotoBe insights_generator.py adapted for earnings calls.
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, Optional, Any, List
from dotenv import load_dotenv

# Load environment
load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    print("Warning: OpenAI not installed")


# Earnings-specific schema
EARNINGS_INSIGHTS_SCHEMA = {
    "name": "earnings_insights",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            # Metadata
            "metadata": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "summary": {"type": "string"},
                    "quarter": {"type": ["string", "null"]},
                    "year": {"type": ["integer", "null"]},
                    "company": {"type": ["string", "null"]},
                    "ticker": {"type": ["string", "null"]}
                },
                "required": ["title", "description", "summary", "quarter", "year", "company", "ticker"],
                "additionalProperties": False
            },

            # Table of contents / chapter markers
            "chapters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "timestamp": {"type": "number"},
                        "title": {"type": "string"},
                        "description": {"type": ["string", "null"]}
                    },
                    "required": ["timestamp", "title", "description"],
                    "additionalProperties": False
                }
            },

            # Speakers (executives)
            "speakers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "title": {"type": ["string", "null"]},
                        "speaker_label": {"type": ["string", "null"]}
                    },
                    "required": ["name", "title", "speaker_label"],
                    "additionalProperties": False
                }
            },

            # Key highlights
            "highlights": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "timestamp": {"type": "number"},
                        "highlight": {"type": "string"},
                        "category": {"type": ["string", "null"]}
                    },
                    "required": ["timestamp", "highlight", "category"],
                    "additionalProperties": False
                }
            },

            # Entities mentioned
            "entities": {
                "type": "object",
                "properties": {
                    "products": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "companies": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "people": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["products", "companies", "people"],
                "additionalProperties": False
            },

            # Financial metrics mentioned
            "metrics": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "metric": {"type": "string"},
                        "value": {"type": ["string", "null"]},
                        "context": {"type": ["string", "null"]}
                    },
                    "required": ["metric", "value", "context"],
                    "additionalProperties": False
                }
            },

            # YouTube metadata
            "youtube": {
                "type": "object",
                "properties": {
                    "hashtags": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["hashtags", "tags"],
                "additionalProperties": False
            }
        },
        "required": ["metadata", "chapters", "speakers", "highlights", "entities", "metrics", "youtube"],
        "additionalProperties": False
    }
}


def build_earnings_prompt(transcript_json: str, company_name: str = None, quarter: str = None) -> str:
    """Build prompt for earnings call insights extraction."""

    context = ""
    if company_name:
        context += f"Company: {company_name}\n"
    if quarter:
        context += f"Quarter: {quarter}\n"

    return f"""You are an expert at analyzing earnings call transcripts.

Extract comprehensive metadata, insights, and YouTube-ready content from this earnings call transcript.

{context}

# EXTRACTION REQUIREMENTS

## 1. METADATA
- title: Clear title like "Apple Q4 2024 Earnings Call"
- description: 2-3 sentence summary
- summary: Detailed 3-4 sentence summary of key points
- quarter, year, company, ticker: Extract from content

## 2. CHAPTERS (7-12 major sections)
Create chapter markers for YouTube timestamps:
- timestamp: When section begins (seconds)
- title: Concise 3-7 word title (e.g., "Q4 Revenue Performance", "Product Updates", "Q&A Session")
- description: Optional 1-sentence summary

**CRITICAL: Distribute chapters EVENLY throughout the entire call duration**
- Calculate total duration from last segment timestamp
- Divide duration into roughly equal intervals (5-8 minutes each)
- For a 44-minute call (~2640s), aim for chapters at: 0s, 300s, 600s, 900s, 1200s, 1500s, 1800s, 2100s, 2400s
- DO NOT cluster chapters in the first 10 minutes
- Q&A section should have multiple chapters if longer than 15 minutes (e.g., "Q&A Part 1", "Q&A Part 2", "Q&A Part 3")
- Each chapter should represent meaningful content at that timestamp

Examples:
- {{timestamp: 0, title: "Opening Remarks", description: "CEO welcomes participants"}}
- {{timestamp: 300, title: "Q4 Financial Results", description: "Revenue and EPS overview"}}
- {{timestamp: 600, title: "Product Highlights", description: "New product launches and updates"}}
- {{timestamp: 900, title: "Strategic Initiatives", description: "Future roadmap discussion"}}
- {{timestamp: 1200, title: "Q&A Session - Part 1", description: "Analyst questions on financials"}}
- {{timestamp: 1800, title: "Q&A Session - Part 2", description: "Questions on operations and strategy"}}

## 3. SPEAKERS
Identify all speakers (usually CEO, CFO, analysts):
- name: Full name
- title: Role/title (CEO, CFO, VP, Analyst, etc.)
- speaker_label: Original label (SPEAKER_00, SPEAKER_01, etc.) if available

## 4. HIGHLIGHTS (Top 5-10 key moments)
Extract key highlights with timestamps:
- timestamp: When mentioned (seconds)
- highlight: What was said (1-2 sentences)
- category: "financial" | "product" | "guidance" | "strategy" | "qa" | null

Examples:
- {{timestamp: 250, highlight: "Revenue up 9% year-over-year to $94.9 billion", category: "financial"}}
- {{timestamp: 430, highlight: "Launched AI-powered platform reaching 1M users", category: "product"}}

## 5. ENTITIES
Extract all entities mentioned:
- products: Product names, platforms, services
- companies: Companies mentioned (partners, competitors, customers)
- people: Executive names, analyst names

## 6. METRICS
Extract financial and operational metrics:
- metric: Name of metric (e.g., "Revenue", "EPS", "Active Users")
- value: Actual value if stated (e.g., "$94.9B", "$1.64", "1.2M")
- context: Brief context (e.g., "up 9% YoY", "beat estimate of $1.58")

## 7. YOUTUBE METADATA
- hashtags: 5-10 relevant hashtags (e.g., ["AAPL", "Apple", "Earnings", "Q42024", "Tech"])
- tags: 10-15 YouTube tags (company name, ticker, quarter, year, "earnings call", "investor relations", etc.)

# IMPORTANT RULES
- Use EXACT timestamps from transcript segments
- Extract ONLY what is explicitly stated
- Use null for undeterminable fields
- Keep highlights concise but informative
- Chapters MUST be distributed evenly throughout the entire call duration (not clustered at start)

# TRANSCRIPT (JSON format with segments)

```json
{transcript_json}
```

Extract all information and return as a single JSON object matching the schema.
"""


def call_openai(prompt: str, model: str = "gpt-4o") -> Optional[Dict[str, Any]]:
    """Call OpenAI API for insights extraction."""

    if not OpenAI:
        raise ImportError("OpenAI not installed")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment")

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert at analyzing earnings call transcripts."},
            {"role": "user", "content": prompt}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": EARNINGS_INSIGHTS_SCHEMA
        },
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)

    return {
        'insights': result,
        'usage': {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        },
        'model': model
    }


def format_timestamp(seconds: float) -> str:
    """Convert seconds to MM:SS or H:MM:SS format."""
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def generate_youtube_description(insights: Dict[str, Any]) -> str:
    """Generate YouTube description with chapters."""

    metadata = insights['metadata']
    chapters = insights['chapters']
    highlights = insights['highlights']

    # Header
    desc = f"{metadata['summary']}\n\n"

    # Key Highlights
    if highlights:
        desc += "🔔 Key Highlights:\n"
        for h in highlights[:5]:  # Top 5
            desc += f"• {h['highlight']}\n"
        desc += "\n"

    # Chapters
    desc += "📖 Chapters:\n"
    for ch in chapters:
        ts = format_timestamp(ch['timestamp'])
        desc += f"{ts} - {ch['title']}\n"

    desc += "\n"

    # Footer
    ticker = metadata.get('ticker', 'unknown').lower() if metadata.get('ticker') else 'unknown'
    quarter = metadata.get('quarter', 'q1').lower() if metadata.get('quarter') else 'q1'
    year = metadata.get('year', 2025)
    desc += f"📊 Full interactive analysis: https://markethawkeye.com/{ticker}/{quarter}-{year}\n\n"
    desc += "Subscribe for more earnings call visualizations!\n\n"

    # Hashtags
    if insights.get('youtube', {}).get('hashtags'):
        desc += " ".join([f"#{tag}" for tag in insights['youtube']['hashtags']])

    return desc


def extract_insights(transcript_path: str, output_path: str = None,
                    company_name: str = None, quarter: str = None,
                    trim_offset: float = 0.0) -> Dict[str, Any]:
    """
    Extract comprehensive insights from earnings transcript.

    Args:
        transcript_path: Path to transcript.json (Whisper output with segments)
        output_path: Where to save insights.json
        company_name: Company name for context
        quarter: Quarter for context
        trim_offset: Seconds trimmed from beginning of video (to adjust timestamps)

    Returns:
        Dictionary with insights, YouTube metadata, and usage stats
    """

    # Load transcript
    with open(transcript_path, 'r') as f:
        transcript = json.load(f)

    if not transcript.get('segments'):
        raise ValueError("Transcript has no segments")

    # Convert to JSON string
    transcript_json = json.dumps(transcript, indent=2, ensure_ascii=False)

    # Build prompt
    prompt = build_earnings_prompt(transcript_json, company_name, quarter)

    # Call OpenAI
    print("Extracting insights with OpenAI...")
    start_time = time.time()

    result = call_openai(prompt)

    elapsed = time.time() - start_time
    print(f"✓ Insights extracted in {elapsed:.2f}s")
    print(f"  Tokens: {result['usage']['total_tokens']}")

    # Generate YouTube description
    insights = result['insights']
    youtube_description = generate_youtube_description(insights)

    # Add YouTube description to result
    insights['youtube']['description'] = youtube_description

    # Adjust all timestamps by trim_offset
    if trim_offset > 0:
        print(f"Adjusting timestamps by -{trim_offset:.2f}s (video trimmed)")

        # Adjust chapter timestamps
        for chapter in insights.get('chapters', []):
            chapter['timestamp'] = max(0, chapter['timestamp'] - trim_offset)

        # Adjust highlight timestamps
        for highlight in insights.get('highlights', []):
            highlight['timestamp'] = max(0, highlight['timestamp'] - trim_offset)

    # Save insights
    if output_path:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)

        print(f"✓ Insights saved to: {output_file}")

    return {
        'insights': insights,
        'usage': result['usage'],
        'model': result['model']
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract comprehensive insights from earnings call transcript"
    )
    parser.add_argument("transcript", help="Path to transcript.json")
    parser.add_argument("--output", help="Output path for insights.json")
    parser.add_argument("--company", help="Company name")
    parser.add_argument("--quarter", help="Quarter (e.g., Q3-2024)")
    parser.add_argument("--trim-offset", type=float, default=0.0,
                       help="Seconds trimmed from video start (adjusts timestamps)")

    args = parser.parse_args()

    try:
        result = extract_insights(
            args.transcript,
            args.output,
            args.company,
            args.quarter,
            args.trim_offset
        )

        print("\n" + "="*50)
        print("Insights extraction complete!")
        print("="*50)
        print(f"Speakers: {len(result['insights']['speakers'])}")
        print(f"Chapters: {len(result['insights']['chapters'])}")
        print(f"Highlights: {len(result['insights']['highlights'])}")
        print(f"Entities: {sum(len(v) for v in result['insights']['entities'].values())}")
        print(f"Metrics: {len(result['insights']['metrics'])}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
