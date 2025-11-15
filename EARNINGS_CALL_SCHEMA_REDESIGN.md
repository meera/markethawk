# Earnings Call Schema Redesign

## Current Issues
1. `youtube_id` in separate column (should be in metadata)
2. `audio_url` naming too specific (should be `media_url`)
3. No structured way to store rich content (SEC filings, images, CEO statements, etc.)

## Proposed Schema

```sql
CREATE TABLE markethawkeye.earnings_calls (
  -- Identity
  id VARCHAR(255) PRIMARY KEY,  -- Format: {SYMBOL}-{QUARTER}-{YEAR}-{BATCH_CODE}

  -- Company identifiers (keep both!)
  cik_str VARCHAR(20) NOT NULL,   -- Permanent SEC identifier (foreign key)
  symbol VARCHAR(10) NOT NULL,    -- User-friendly ticker (can change over time)

  -- Period
  quarter VARCHAR(10) NOT NULL,   -- Q1, Q2, Q3, Q4
  year INTEGER NOT NULL,          -- Fiscal year

  -- Primary media
  media_url VARCHAR(512),          -- Public URL to primary media (audio/video)

  -- Versioning
  is_latest BOOLEAN NOT NULL DEFAULT true,

  -- Rich content (JSONB)
  content JSONB DEFAULT '{}',

  -- Pipeline metadata (JSONB)
  metadata JSONB DEFAULT '{}',

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMP DEFAULT NOW() NOT NULL
);

-- Indexes
CREATE INDEX idx_earnings_calls_cik ON markethawkeye.earnings_calls(cik_str);
CREATE INDEX idx_earnings_calls_symbol ON markethawkeye.earnings_calls(symbol);
CREATE INDEX idx_earnings_calls_quarter_year ON markethawkeye.earnings_calls(quarter, year);
CREATE INDEX idx_earnings_calls_symbol_latest ON markethawkeye.earnings_calls(symbol, is_latest) WHERE is_latest = true;
CREATE INDEX idx_earnings_calls_created_desc ON markethawkeye.earnings_calls(created_at DESC);
CREATE INDEX idx_earnings_calls_content ON markethawkeye.earnings_calls USING GIN (content);
```

## JSONB Field: `content`

Rich content for earnings call - SEC filings, images, CEO statements, financial data, etc.

### Schema Structure

```json
{
  "sources": {
    "youtube": {
      "video_id": "xw6oCFYNz8c",
      "channel_id": "UCxxxxx",
      "title": "Aehr Test Systems Q4 2023 Earnings Call",
      "description": "...",
      "published_at": "2023-08-15T10:00:00Z",
      "duration_seconds": 3600,
      "view_count": 1234,
      "thumbnail_url": "https://..."
    },
    "ir_website": {
      "url": "https://ir.aehr.com/events/...",
      "archived_at": "2025-11-14T10:00:00Z"
    },
    "podcast": {
      "platform": "spotify",
      "episode_id": "...",
      "url": "https://..."
    }
  },

  "media": {
    "primary": {
      "type": "audio",
      "url": "https://r2.../audio.mp3",
      "format": "mp3",
      "duration_seconds": 3600,
      "size_bytes": 55456000,
      "bitrate": "128kbps",
      "sample_rate": "44100Hz"
    },
    "alternatives": [
      {
        "type": "video",
        "url": "https://r2.../video.mp4",
        "format": "mp4",
        "resolution": "1080p",
        "duration_seconds": 3600,
        "size_bytes": 620000000
      }
    ],
    "segments": [
      {
        "type": "prepared_remarks",
        "start_time": 0,
        "end_time": 1200,
        "url": "https://r2.../segment_1.mp3"
      },
      {
        "type": "qa_session",
        "start_time": 1200,
        "end_time": 3600,
        "url": "https://r2.../segment_2.mp3"
      }
    ]
  },

  "transcript": {
    "full_text_url": "https://r2.../transcript.txt",
    "json_url": "https://r2.../transcript.json",
    "word_count": 8500,
    "language": "en",
    "speakers": [
      {
        "id": "SPEAKER_00",
        "name": "Gayn Erickson",
        "title": "President and CEO",
        "word_count": 3200,
        "speaking_time_seconds": 1400
      },
      {
        "id": "SPEAKER_01",
        "name": "Ken Spink",
        "title": "CFO",
        "word_count": 2100,
        "speaking_time_seconds": 900
      }
    ],
    "provider": "whisperx",
    "version": "3.3.1",
    "has_timestamps": true,
    "has_diarization": true
  },

  "sec_filings": [
    {
      "type": "10-K",
      "accession_number": "0001437749-23-025531",
      "filing_date": "2023-08-14",
      "period_end_date": "2023-05-31",
      "url": "https://www.sec.gov/...",
      "pdf_url": "https://r2.../10k.pdf",
      "pages": 82,
      "key_sections": {
        "item_1a_risk_factors": { "page": 12, "excerpt": "..." },
        "item_7_mda": { "page": 28, "excerpt": "..." },
        "item_8_financials": { "page": 45, "tables": ["balance_sheet", "income_statement", "cash_flow"] }
      }
    },
    {
      "type": "10-Q",
      "accession_number": "...",
      "filing_date": "2023-11-15",
      "url": "..."
    },
    {
      "type": "8-K",
      "accession_number": "...",
      "filing_date": "2023-08-15",
      "items": ["2.02", "9.01"],
      "description": "Results of Operations and Financial Condition",
      "url": "..."
    }
  ],

  "press_releases": [
    {
      "title": "Aehr Test Systems Announces Record Fourth Quarter...",
      "date": "2023-08-14",
      "url": "https://ir.aehr.com/...",
      "pdf_url": "https://r2.../press_release.pdf",
      "highlights": [
        "Record quarterly revenue of $24.5 million",
        "Gross margin of 55%",
        "Backlog increased to $67 million"
      ]
    }
  ],

  "presentations": {
    "earnings_deck": {
      "title": "Q4 2023 Earnings Presentation",
      "pdf_url": "https://r2.../earnings_deck.pdf",
      "pages": 25,
      "slides": [
        {
          "page": 1,
          "title": "Q4 2023 Financial Highlights",
          "thumbnail_url": "https://r2.../slide_1_thumb.jpg",
          "full_url": "https://r2.../slide_1.jpg"
        },
        {
          "page": 5,
          "title": "Revenue Breakdown by Segment",
          "chart_data": {
            "type": "bar_chart",
            "categories": ["Silicon Carbide", "Silicon Photonics"],
            "values": [18.2, 6.3]
          },
          "thumbnail_url": "https://r2.../slide_5_thumb.jpg"
        }
      ]
    },
    "webcast_replay": {
      "url": "https://edge.media-server.com/...",
      "available_until": "2024-08-15"
    }
  },

  "financial_data": {
    "revenue": {
      "value": 24500000,
      "currency": "USD",
      "yoy_growth": 0.89,
      "qoq_growth": 0.15,
      "segment_breakdown": {
        "silicon_carbide": 18200000,
        "silicon_photonics": 6300000
      }
    },
    "gross_margin": 0.55,
    "operating_income": 6200000,
    "net_income": 5800000,
    "eps": 0.22,
    "backlog": 67000000,
    "guidance": {
      "next_quarter": {
        "revenue_min": 20000000,
        "revenue_max": 24000000,
        "midpoint": 22000000
      }
    }
  },

  "key_metrics": [
    {
      "name": "Content Investment",
      "value": "1.5 billion",
      "unit": "USD",
      "context": "Paramount Plus content spending",
      "timestamp_seconds": 331.6,
      "speaker": "Bob Bakish",
      "importance": "high"
    },
    {
      "name": "Subscriber Growth",
      "value": 24,
      "unit": "percent",
      "context": "Paramount Plus YoY growth",
      "timestamp_seconds": 537.5,
      "importance": "high"
    }
  ],

  "highlights": [
    {
      "text": "Strategic focus on content quality over quantity",
      "timestamp_seconds": 183.2,
      "speaker": "David Ellison",
      "category": "strategy",
      "sentiment": "positive"
    }
  ],

  "images": [
    {
      "type": "logo",
      "url": "https://r2.../logo.png",
      "width": 512,
      "height": 512,
      "usage": "thumbnail"
    },
    {
      "type": "chart",
      "title": "Revenue Trend",
      "url": "https://r2.../revenue_chart.png",
      "width": 1920,
      "height": 1080,
      "timestamp_seconds": 245,
      "chart_data": {
        "type": "line",
        "x_axis": ["Q1", "Q2", "Q3", "Q4"],
        "y_axis": [15.2, 18.5, 21.3, 24.5]
      }
    }
  ],

  "executive_statements": [
    {
      "executive": {
        "name": "Gayn Erickson",
        "title": "President and CEO"
      },
      "type": "prepared_remarks",
      "full_text": "Thank you for joining us today...",
      "key_quotes": [
        {
          "text": "We achieved record revenue of $24.5 million",
          "timestamp_seconds": 120,
          "context": "quarterly_results"
        }
      ],
      "audio_segment_url": "https://r2.../ceo_remarks.mp3",
      "start_time": 0,
      "end_time": 1200
    }
  ],

  "analyst_coverage": [
    {
      "firm": "Craig-Hallum",
      "analyst": "Christian Schwab",
      "rating": "Buy",
      "price_target": 25.00,
      "date": "2023-08-15",
      "report_summary": "Strong execution, raising PT to $25"
    }
  ],

  "social_sentiment": {
    "twitter_mentions": 142,
    "reddit_discussions": 8,
    "sentiment_score": 0.72,
    "trending_topics": ["silicon_carbide", "backlog", "guidance"],
    "sampled_at": "2023-08-15T18:00:00Z"
  },

  "metadata": {
    "processed_at": "2025-11-14T11:05:42Z",
    "processing_version": "2.0",
    "quality_score": 0.95,
    "completeness": {
      "transcript": true,
      "sec_filings": true,
      "financial_data": true,
      "images": true,
      "press_release": true,
      "analyst_coverage": false
    }
  }
}
```

## JSONB Field: `metadata` (Pipeline-specific)

Internal processing metadata - batch info, pipeline config, system data.

```json
{
  "pipeline": {
    "batch_code": "sd07",
    "batch_name": "nov-14-2025-single-test",
    "job_id": "xw6oCFYNz8c_e5cd",
    "pipeline_type": "audio-only",
    "version": "2.0"
  },
  "storage": {
    "r2_bucket": "markeyhawkeye",
    "r2_base_path": "aehr-test-systems/Q4-2023/nov-14-2025-single-test-xw6oCFYNz8c_e5cd",
    "r2_audio_path": "audio.mp3",
    "r2_transcript_path": "transcript.json",
    "total_size_bytes": 55456000
  },
  "processing_steps": {
    "download": { "status": "completed", "duration_seconds": 2.3 },
    "transcribe": { "status": "completed", "duration_seconds": 81.5, "provider": "whisperx" },
    "insights": { "status": "completed", "duration_seconds": 37.2, "provider": "openai-gpt4" },
    "upload_r2": { "status": "completed", "duration_seconds": 4.1 }
  },
  "quality_checks": {
    "audio_quality": "high",
    "transcript_accuracy": 0.95,
    "diarization_confidence": 0.88
  }
}
```

## Migration SQL

```sql
-- 1. Rename audio_url to media_url
ALTER TABLE markethawkeye.earnings_calls
  RENAME COLUMN audio_url TO media_url;

-- 2. Add content JSONB field
ALTER TABLE markethawkeye.earnings_calls
  ADD COLUMN content JSONB DEFAULT '{}';

-- 3. Create GIN index for content field (for fast JSONB queries)
CREATE INDEX idx_earnings_calls_content
  ON markethawkeye.earnings_calls USING GIN (content);

-- 4. Migrate youtube_id to metadata
UPDATE markethawkeye.earnings_calls
SET metadata = jsonb_set(
  COALESCE(metadata, '{}'::jsonb),
  '{sources,youtube,video_id}',
  to_jsonb(youtube_id),
  true
)
WHERE youtube_id IS NOT NULL;

-- 5. Drop youtube_id column (after verifying migration)
-- ALTER TABLE markethawkeye.earnings_calls DROP COLUMN youtube_id;
```

## Benefits

### Content Field
✅ **Flexible** - Can add new content types without schema changes
✅ **Rich** - SEC filings, images, charts, quotes, all in one place
✅ **Queryable** - GIN index enables fast JSONB queries
✅ **Future-proof** - Easily extend for new data sources

### Metadata Field
✅ **Separation of concerns** - Pipeline data separate from user-facing content
✅ **Clean** - Processing details don't clutter content field
✅ **Internal** - Not exposed in public API

### Symbol + CIK
✅ **Reliability** - CIK never changes, perfect for foreign keys
✅ **Usability** - Symbol is human-friendly for queries and URLs
✅ **Historical tracking** - Can track ticker changes over time

## Example Queries

### Find earnings calls with SEC 10-K filings
```sql
SELECT id, symbol, quarter, year
FROM markethawkeye.earnings_calls
WHERE content->'sec_filings' @> '[{"type": "10-K"}]';
```

### Get all calls with CEO prepared remarks
```sql
SELECT id, symbol, quarter, year,
       content->'executive_statements'->0->'executive'->>'name' as ceo
FROM markethawkeye.earnings_calls
WHERE content->'executive_statements' @> '[{"type": "prepared_remarks"}]';
```

### Find calls with high-quality transcripts
```sql
SELECT id, symbol, quarter, year
FROM markethawkeye.earnings_calls
WHERE (metadata->'quality_checks'->>'transcript_accuracy')::float > 0.9;
```

### Get earnings calls with presentation slides
```sql
SELECT id, symbol, quarter, year,
       content->'presentations'->'earnings_deck'->>'pdf_url' as deck_url
FROM markethawkeye.earnings_calls
WHERE content->'presentations'->'earnings_deck' IS NOT NULL;
```
