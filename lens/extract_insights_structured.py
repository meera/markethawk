#!/usr/bin/env python3
"""
MarketHawk Insights Extraction with OpenAI Structured Outputs
Extract earnings call metadata, speaker identification, and insights

Adapted from VideotoBe's transcript_openai_analysis.py
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict
from openai import OpenAI
import json
from pathlib import Path


class Speaker(BaseModel):
    """Speaker identification"""
    speaker_id: str = Field(description="Original speaker ID from transcript (e.g., SPEAKER_00)")
    speaker_name: str = Field(description="Identified speaker name (or 'Unknown' if can't identify)")
    role: Optional[str] = Field(default=None, description="Role (e.g., CEO, CFO, Analyst)")


class FinancialMetric(BaseModel):
    """Financial metric highlight"""
    metric: str = Field(description="Metric name (e.g., Revenue, EPS, Operating Income)")
    value: str = Field(description="Value mentioned (e.g., $94.9B, $1.64)")
    change: Optional[str] = Field(default=None, description="Change vs prior period (e.g., +6% YoY, -3% QoQ)")
    timestamp: int = Field(description="Timestamp in seconds when mentioned")
    context: str = Field(description="Brief context around the metric")


class Highlight(BaseModel):
    """Key highlight or insight"""
    timestamp: int = Field(description="Timestamp in seconds")
    text: str = Field(description="Highlight text (concise, <280 chars)")
    category: Literal["financial", "product", "guidance", "strategy", "qa"] = Field(
        description="Category of highlight"
    )
    speaker: str = Field(description="Speaker who said it")


class Chapter(BaseModel):
    """Video chapter marker"""
    timestamp: int = Field(description="Start time in seconds")
    title: str = Field(description="Chapter title")


class EarningsInsights(BaseModel):
    """Complete earnings call insights"""
    speakers: List[Speaker] = Field(description="All speakers identified in the call")
    financial_metrics: List[FinancialMetric] = Field(description="Key financial metrics mentioned")
    highlights: List[Highlight] = Field(description="5-10 key highlights from the call")
    chapters: List[Chapter] = Field(description="Video chapter markers for major sections")
    summary: str = Field(description="2-3 paragraph narrative summary of the call")
    youtube_title: str = Field(description="Optimized YouTube video title")
    youtube_description: str = Field(description="YouTube description with timestamps")


def extract_earnings_insights(
    transcript_file: Path,
    company_name: str,
    ticker: str,
    quarter: str,
    output_file: Optional[Path] = None
) -> EarningsInsights:
    """
    Extract structured insights from earnings call transcript

    Args:
        transcript_file: Path to transcript.json (from WhisperX)
        company_name: Company name
        ticker: Stock ticker
        quarter: Quarter (e.g., Q3-2025)
        output_file: Optional path to save raw OpenAI response

    Returns:
        EarningsInsights object
    """
    # Load transcript
    with open(transcript_file, 'r', encoding='utf-8') as f:
        transcript_data = json.load(f)

    # Format transcript for analysis
    formatted_transcript = format_transcript_for_analysis(transcript_data)

    # System prompt
    system_prompt = f"""You are an expert financial analyst specializing in earnings calls.
Your role is to extract key financial metrics, identify speakers, and create structured insights
while maintaining accuracy and context.

Focus on:
- Identifying C-suite executives and analysts by name
- Extracting financial metrics with exact values mentioned
- Highlighting strategic announcements and guidance
- Creating clear chapter markers for major sections (Opening Remarks, Financial Results, Guidance, Q&A)
"""

    # User prompt
    user_prompt = f"""
Analyze this {company_name} ({ticker}) {quarter} earnings call transcript.

SPEAKER IDENTIFICATION:
- Map SPEAKER_00, SPEAKER_01, etc. to actual names
- Identify roles (CEO, CFO, IR Head, Analyst from [Firm])
- Use 'Unknown' only if name truly can't be identified from context

FINANCIAL METRICS:
- Extract key metrics: Revenue, EPS, Operating Income, Free Cash Flow, Margins
- Include exact values and % changes vs prior period
- Note timestamp when mentioned

HIGHLIGHTS:
- 5-10 most important moments from the call
- Financial results, guidance changes, product announcements, strategic shifts
- Include speaker attribution and timestamps

CHAPTERS:
- Create clear chapter markers:
  - Opening Remarks (usually ~0:00)
  - Financial Results (usually after intro)
  - Business Update / Product News
  - Guidance / Outlook
  - Q&A Session
- Use actual timestamps from transcript

SUMMARY:
- 2-3 paragraph narrative covering:
  - Financial performance highlights
  - Strategic announcements
  - Forward guidance
  - Key Q&A themes

YOUTUBE METADATA:
- Title: Optimized for search (include company, ticker, quarter, year)
- Description: Summary + timestamp links to chapters

Transcript:
{formatted_transcript}
"""

    # Call OpenAI with structured output
    client = OpenAI()

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=EarningsInsights,
    )

    insights = completion.choices[0].message.parsed

    # Save raw OpenAI response if output file specified
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            # Include usage stats
            raw_output = {
                "insights": insights.model_dump(),
                "usage": {
                    "prompt_tokens": completion.usage.prompt_tokens,
                    "completion_tokens": completion.usage.completion_tokens,
                    "total_tokens": completion.usage.total_tokens
                },
                "model": completion.model,
                "created_at": completion.created
            }
            json.dump(raw_output, f, indent=2, ensure_ascii=False)

    return insights


def format_transcript_for_analysis(transcript_data: Dict) -> str:
    """
    Format WhisperX transcript for OpenAI analysis

    Groups segments by speaker with timestamps
    """
    segments = transcript_data.get("segments", [])

    formatted_lines = []
    current_speaker = None
    current_text = []
    current_start = None

    for segment in segments:
        speaker = segment.get("speaker", "UNKNOWN")
        text = segment.get("text", "").strip()
        start = segment.get("start", 0)

        # Group consecutive segments from same speaker
        if speaker == current_speaker:
            current_text.append(text)
        else:
            # Write previous speaker's text
            if current_speaker and current_text:
                timestamp_str = format_timestamp(current_start)
                speaker_text = " ".join(current_text)
                formatted_lines.append(f"[{timestamp_str}] {current_speaker}: {speaker_text}")

            # Start new speaker
            current_speaker = speaker
            current_text = [text]
            current_start = start

    # Write last speaker
    if current_speaker and current_text:
        timestamp_str = format_timestamp(current_start)
        speaker_text = " ".join(current_text)
        formatted_lines.append(f"[{timestamp_str}] {current_speaker}: {speaker_text}")

    return "\n\n".join(formatted_lines)


def format_timestamp(seconds: float) -> str:
    """Format seconds to MM:SS"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract earnings call insights with OpenAI")
    parser.add_argument("transcript_file", help="Path to transcript.json")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--ticker", required=True, help="Stock ticker")
    parser.add_argument("--quarter", required=True, help="Quarter (e.g., Q3-2025)")
    parser.add_argument("--output", help="Path to save raw OpenAI response")

    args = parser.parse_args()

    insights = extract_earnings_insights(
        transcript_file=Path(args.transcript_file),
        company_name=args.company,
        ticker=args.ticker,
        quarter=args.quarter,
        output_file=Path(args.output) if args.output else None
    )

    # Print summary
    print("\n" + "="*60)
    print(f"{args.company} ({args.ticker}) {args.quarter} Earnings Call")
    print("="*60)
    print(f"\nSpeakers: {len(insights.speakers)}")
    for speaker in insights.speakers:
        role_str = f" ({speaker.role})" if speaker.role else ""
        print(f"  - {speaker.speaker_name}{role_str}")

    print(f"\nFinancial Metrics: {len(insights.financial_metrics)}")
    for metric in insights.financial_metrics[:5]:  # Show first 5
        print(f"  - {metric.metric}: {metric.value}" + (f" ({metric.change})" if metric.change else ""))

    print(f"\nHighlights: {len(insights.highlights)}")
    print(f"Chapters: {len(insights.chapters)}")
    print(f"\nYouTube Title: {insights.youtube_title}")
