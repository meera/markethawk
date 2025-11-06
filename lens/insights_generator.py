"""
Insights generation module for VideoToBe transcriptions.

This module extracts metadata, insights, and entities from transcripts
in a single OpenAI call to optimize costs.

Based on test_llm_pipeline.py but adapted for production use.
"""

import json
import os
import re
import string
import random
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path


try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
    print("Warning: OpenAI not installed. Insights generation will be skipped.")


# Comprehensive JSON Schema for VideoToBe insights extraction
INSIGHTS_EXTRACTION_SCHEMA = {
    "name": "videotobe_insights",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            # Metadata for content.metadata JSONB
            "metadata": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": ["string", "null"],
                        "description": "Suggested title based on content"
                    },
                    "description": {
                        "type": ["string", "null"],
                        "description": "Brief description of the content"
                    },
                    "summary": {
                        "type": ["string", "null"],
                        "description": "2-3 sentence summary of key discussion points"
                    },
                    "content_type": {
                        "type": ["string", "null"],
                        "enum": ["meeting", "interview", "presentation", "webinar", "podcast", "lecture", "call", "general", None],
                        "description": "Type of content"
                    },
                    "event_date": {
                        "type": ["string", "null"],
                        "description": "Date mentioned in the content (ISO format or null)"
                    },
                    "event_location": {
                        "type": ["string", "null"],
                        "description": "Location mentioned for the event"
                    },
                    "participants_count": {
                        "type": ["integer", "null"],
                        "description": "Number of participants if determinable"
                    }
                },
                "required": ["title", "description", "summary", "content_type", "event_date", "event_location", "participants_count"],
                "additionalProperties": False
            },

            # Table of Contents for navigation
            "table_of_contents": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "timestamp": {
                            "type": "number",
                            "description": "Timestamp in seconds where this section begins"
                        },
                        "title": {
                            "type": "string",
                            "description": "3-7 word descriptive title for this section"
                        },
                        "description": {
                            "type": ["string", "null"],
                            "description": "Optional 1 sentence description of what's covered"
                        }
                    },
                    "required": ["timestamp", "title", "description"],
                    "additionalProperties": False
                },
                "description": "5-10 major sections/chapters identified from the content"
            },

            # Insights for content.insights JSONB
            "insights": {
                "type": "object",
                "properties": {
                    "suggested_questions": {
                        "type": ["array", "null"],
                        "items": {"type": "string"},
                        "description": "1-5 thought-provoking questions users might ask to explore this content further"
                    },
                    "keywords": {
                        "type": ["array", "null"],
                        "items": {
                            "type": "object",
                            "properties": {
                                "term": {"type": "string"},
                                "explanation": {"type": ["string", "null"]}
                            },
                            "required": ["term", "explanation"],
                            "additionalProperties": False
                        },
                        "description": "5-6 key terms/phrases mentioned in the transcript with brief explanations if available"
                    },
                    "key_takeaways": {
                        "type": ["array", "null"],
                        "items": {"type": "string"},
                        "description": "5-7 main points from the discussion, or null if not applicable"
                    },
                    "action_items": {
                        "type": ["array", "null"],
                        "items": {
                            "type": "object",
                            "properties": {
                                "task": {"type": "string"},
                                "owner": {"type": ["string", "null"]},
                                "priority": {
                                    "type": ["string", "null"],
                                    "enum": ["high", "medium", "low", None]
                                },
                                "context": {"type": "string"}
                            },
                            "required": ["task", "owner", "priority", "context"],
                            "additionalProperties": False
                        },
                        "description": "Action items with owners and priorities, or null if not applicable"
                    },
                    "main_topics": {
                        "type": ["array", "null"],
                        "items": {
                            "type": "object",
                            "properties": {
                                "topic": {"type": "string"},
                                "mentions": {"type": "integer"}
                            },
                            "required": ["topic", "mentions"],
                            "additionalProperties": False
                        },
                        "description": "Main topics with mention counts, or null if not applicable"
                    },
                    "notable_quotes": {
                        "type": ["array", "null"],
                        "items": {
                            "type": "object",
                            "properties": {
                                "quote": {"type": "string"},
                                "speaker": {"type": ["string", "null"]},
                                "context": {"type": ["string", "null"]}
                            },
                            "required": ["quote", "speaker", "context"],
                            "additionalProperties": False
                        },
                        "description": "Notable quotes from the content, or null if not applicable"
                    }
                },
                "required": ["suggested_questions", "keywords", "key_takeaways", "action_items", "main_topics", "notable_quotes"],
                "additionalProperties": False
            },

            # Speaker identification
            "speaker_names": {
                "type": "object",
                "description": "Mapping of SPEAKER_XX labels to identified real names from transcript",
                "additionalProperties": {
                    "type": ["string", "null"]
                }
            },

            # Entities for content.insights.entities
            "entities": {
                "type": "object",
                "properties": {
                    "people": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "role": {"type": ["string", "null"]},
                                "company": {"type": ["string", "null"]},
                                "mention_count": {"type": "integer"},
                                "context": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["name", "role", "company", "mention_count", "context"],
                            "additionalProperties": False
                        }
                    },
                    "organizations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": ["string", "null"]},
                                "mention_count": {"type": "integer"},
                                "context": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["name", "type", "mention_count", "context"],
                            "additionalProperties": False
                        }
                    },
                    "products": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": ["string", "null"]},
                                "mention_count": {"type": "integer"},
                                "context": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["name", "type", "mention_count", "context"],
                            "additionalProperties": False
                        }
                    },
                    "locations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": ["string", "null"]},
                                "mention_count": {"type": "integer"},
                                "context": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["name", "type", "mention_count", "context"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["people", "organizations", "products", "locations"],
                "additionalProperties": False
            }
        },
        "required": ["metadata", "table_of_contents", "insights", "speaker_names"],
        "additionalProperties": False
    }
}


def generate_entity_id(entity_type: str, entity_name: str) -> str:
    """
    Generate a unique entity ID following PRD format: ent_<type>_<name>_<4char>

    Examples:
    - ent_person_sarah_chen_x3k2
    - ent_org_acme_corp_a2b7
    """
    type_mapping = {
        'person': 'person',
        'people': 'person',
        'organization': 'org',
        'organizations': 'org',
        'product': 'prod',
        'products': 'prod',
        'location': 'loc',
        'locations': 'loc'
    }

    type_prefix = type_mapping.get(entity_type.lower(), entity_type.lower()[:4])
    clean_name = re.sub(r'[^a-z0-9]+', '_', entity_name.lower())
    clean_name = clean_name.strip('_')[:20]

    chars = string.ascii_lowercase + string.digits
    suffix = ''.join(random.choice(chars) for _ in range(4))

    return f"ent_{type_prefix}_{clean_name}_{suffix}"


def build_prompt_for_paragraphs(
    paragraphs_json: str,
    filename: Optional[str] = None,
    input_context: Optional[str] = None
) -> str:
    """Build the prompt for insights extraction from paragraphs.json."""

    context_section = ""
    if filename:
        context_section += f"""
# FILENAME CONTEXT
The file is named: {filename}
This filename may contain dates, names, or other relevant information. Use it as a hint but verify against the transcript content.
"""

    if input_context:
        context_section += f"""
# USER CONTEXT
The user provided this context when uploading: "{input_context}"
This helps understand the content but should be verified against the actual transcript.
"""

    return f"""You are an expert metadata extractor and content analyzer for transcripts.

Your task: Analyze a transcript (provided as JSON with speaker-labeled segments) and extract:
1. Metadata (title, summary, content type, etc.)
2. Table of Contents (5-10 major sections with timestamps)
3. Insights (key takeaways, keywords, questions, action items, etc.)
4. Speaker names (identify real names from self-introductions)
5. Entities (people, organizations, products, locations mentioned)

Work precisely and factually. Use null for fields that cannot be determined.

{context_section}

# CRITICAL INSTRUCTIONS

**LANGUAGE REQUIREMENT - MOST IMPORTANT**
- **USE THE SAME LANGUAGE AS THE TRANSCRIPT** for ALL extracted content
- If transcript is in Swedish → write insights in Swedish
- If transcript is in English → write insights in English
- If transcript is in Spanish → write insights in Spanish
- JSON keys stay in English, but all VALUES match the transcript language

**EXTRACT ONLY WHAT IS EXPLICITLY STATED**
- Do not invent or assume information
- Use null for fields that cannot be determined
- Treat filename/context as hints only

# STEP 1: METADATA EXTRACTION

Extract the following metadata:

1. **Title**: Concise, descriptive title (or null)
2. **Description**: 1-2 sentence description (or null)
3. **Summary**: 2-3 sentence summary of key discussion points (or null)
4. **Content Type**: meeting|interview|presentation|webinar|podcast|lecture|sermon|call|general
5. **Event Date**: ISO format "YYYY-MM-DD" if mentioned (or null)
6. **Event Location**: Location if mentioned (or null)
7. **Participants Count**: Number of distinct speakers (or null)

# STEP 2: TABLE OF CONTENTS

Identify 5-10 major sections/chapters in the content based on topic shifts.

For each section provide:
- **timestamp**: When the section begins (in seconds, from the transcript segments)
- **title**: 3-7 word descriptive title
- **description**: Optional 1 sentence summary (or null)

Example:
```json
[
  {{"timestamp": 0, "title": "Introduction and Welcome", "description": "Hosts introduce themselves and the topic"}},
  {{"timestamp": 349, "title": "Pentecost and the Holy Spirit", "description": "Discussion of Acts chapter 2 and the role of the Holy Spirit"}},
  {{"timestamp": 669, "title": "Jewish Followers Maintain Identity", "description": "How early followers of Jesus continued practicing Judaism"}}
]
```

**Important**: Use ACTUAL timestamps from the provided segments. Do not invent timestamps.

# STEP 3: INSIGHTS EXTRACTION

Analyze the transcript for the following insights. **IMPORTANT**: If an insight type is not applicable to this content (e.g., action items for a podcast, task list for casual conversation), return **null** instead of an empty array.

1. **Suggested Questions** (REQUIRED): Generate 1-5 thought-provoking questions that users might want to ask to explore this content further.
   - These questions will be shown as "Explore More" prompts in the AI chat interface
   - Questions should be insightful, specific to the content, and encourage deeper engagement
   - Examples: "What were the key factors that led to this decision?", "How does this compare to industry standards?", "What are the practical implications for small businesses?"
   - Format: Array of strings, e.g., ["Question 1?", "Question 2?", "Question 3?"]

2. **Keywords** (REQUIRED): Extract 5-6 key terms/phrases mentioned in the transcript along with brief explanations.
   - Only include terms that are actually explained or defined in the transcript
   - If a term is mentioned but not explained, set explanation to null
   - Examples: {{"term": "Machine Learning", "explanation": "A type of AI that learns from data"}}, {{"term": "API", "explanation": null}}
   - Format: Array of objects with term and explanation fields

3. **Key Takeaways**: 5-7 main points that summarize the essence, or **null** if not applicable.
   - Return fewer if there are less than 5 substantial points
   - Return **null** if content doesn't have clear takeaways (e.g., casual conversation)
   - Format each takeaway as a string in a list

4. **Action Items**: Specific follow-up steps or tasks mentioned, or **null** if not applicable.
   - Each item includes: task (string), owner (string or null), priority (string or null), context (string)
   - Return **null** if there are no action items (e.g., podcasts, presentations, lectures)
   - Do NOT invent action items that weren't explicitly mentioned

5. **Main Topics**: Key themes discussed (at least 3 if possible), or **null** if not applicable.
   - Each topic should have: topic (string), mentions (integer)
   - Return fewer if not enough substantive topics exist
   - Return **null** if content doesn't have clear topics

6. **Notable Quotes**: 3–5 significant quotes, or **null** if not applicable.
   - Each quote includes: quote (string), speaker (string or null), context (string or null)
   - Return **null** if there are no memorable quotes worth highlighting
   - Only include quotes that are truly notable, insightful, or impactful

# STEP 3: SPEAKER IDENTIFICATION

Identify the real names of speakers from the transcript content:

1. Look for **self-introductions**: "I'm Sarah Chen", "My name is John", "This is Willem"
2. Look for **direct addresses**: When one speaker addresses another by name
3. Use **context clues**: Roles, companies mentioned by the speaker

**Rules**:
- ONLY return names that are EXPLICITLY mentioned in the transcript
- Return null if you cannot confidently identify a speaker's name
- First names are acceptable if full names are not mentioned
- For hosts/interviewers without clear names, you may use "Host" or "Interviewer"
- Do NOT guess or invent names that are not in the transcript
- Do NOT use generic descriptions like "Financial Analyst" - use null instead

**Output**: Return a mapping object like:
{{
  "SPEAKER_00": "Willem" or null,
  "SPEAKER_01": null,
  "SPEAKER_02": "Host"
}}

# STEP 4: ENTITY EXTRACTION

Identify ALL entities explicitly mentioned (return empty arrays if none):

1. **People**: Names or roles referenced.
   - Each person: name (string), role (string or null), company (string or null), mention_count (integer), context (array of 1-2 strings).
2. **Organizations**: Companies, institutions, agencies.
   - Each organization: name (string), type (string or null), mention_count (integer), context (array of strings).
3. **Products**: Products, services, tools, or platforms.
   - Each product: name (string), type (string or null), mention_count (integer), context (array of strings).
4. **Locations**: Cities, offices, regions, or venues.
   - Each location: name (string), type (string or null), mention_count (integer), context (array of strings).


# STEP 5: OUTPUT STRUCTURE VALIDATION

- Output all extracted information in a single JSON object according to the schema.
- For entity and insight arrays with no items, return empty arrays.
- For undeterminable fields, use null.
- If the transcript is empty or has no extractable content, return all JSON fields as null or empty arrays as appropriate.
- Do not make assumptions or add any content not verified explicitly in the transcript.

Finally, validate that output JSON matches schema:
- All required fields present
- Only expected keys
- Proper nulls and empty arrays
Then output final JSON only — no prose.

# TRANSCRIPT (JSON FORMAT)

The transcript is provided as JSON with the following structure:
- segments: Array of objects, each containing:
  - start: Timestamp in seconds when this segment begins
  - end: Timestamp in seconds when this segment ends
  - speaker: Speaker label (e.g., "SPEAKER_00", "SPEAKER_01")
  - text: The spoken text for this segment

```json
{paragraphs_json}
```
"""


def call_openai(prompt: str, model: str = "gpt-4o-mini") -> Optional[Dict[str, Any]]:
    """Call OpenAI API to generate insights."""

    if not OpenAI:
        print("OpenAI not available, skipping insights generation")
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("No OpenAI API key found, skipping insights generation")
        return None

    try:
        client = OpenAI(api_key=api_key)

        request_params = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert at extracting structured information from transcripts."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": INSIGHTS_EXTRACTION_SCHEMA
            }
        }

        # Temperature setting based on model
        if not model.startswith('o1-'):
            request_params["temperature"] = 0.3

        response = client.chat.completions.create(**request_params)
        result = json.loads(response.choices[0].message.content)

        return {
            'result': result,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            },
            'model': model
        }

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None


def add_entity_ids(entities: Dict[str, list]) -> Dict[str, list]:
    """Add unique IDs to entities following PRD format."""

    processed = {}

    for entity_type, entity_list in entities.items():
        processed_list = []

        for entity in entity_list:
            entity_id = generate_entity_id(entity_type, entity['name'])

            processed_entity = {
                'entity_id': entity_id,
                'name': entity['name'],
                'mention_count': entity.get('mention_count', 1),
                'context': entity.get('context', [])
            }

            # Add optional fields if present
            if entity.get('role'):
                processed_entity['role'] = entity['role']
            if entity.get('company'):
                processed_entity['company'] = entity['company']
            if entity.get('type'):
                processed_entity['type'] = entity['type']

            processed_list.append(processed_entity)

        processed[entity_type] = processed_list

    return processed


def extract_insights_from_paragraphs(
    paragraphs: Dict[str, Any],
    filename: Optional[str] = None,
    input_context: Optional[str] = None,
    job_data: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Extract insights from paragraphs.json (Whisper output).

    Args:
        paragraphs: Dict with 'segments' array from Whisper
        filename: Original filename for context
        input_context: User-provided context
        job_data: Additional job configuration

    Returns:
        Dict with:
        - metadata: {title, summary, description, ...}
        - table_of_contents: [{timestamp, title, description}, ...]
        - insights: {key_takeaways, keywords, entities, ...}
        - speaker_names: {SPEAKER_00: "Name", ...}
        - usage: {tokens, cost}
    """

    if not paragraphs or not paragraphs.get('segments'):
        print("No paragraphs or segments provided")
        return None

    # Convert paragraphs to JSON string for prompt
    paragraphs_json = json.dumps(paragraphs, indent=2, ensure_ascii=False)

    # Build prompt
    prompt = build_prompt_for_paragraphs(
        paragraphs_json=paragraphs_json,
        filename=filename,
        input_context=input_context
    )

    # Determine model
    model = "gpt-4o-mini"
    if job_data and isinstance(job_data, dict):
        model = job_data.get('llm_model', model)

    print(f"Calling OpenAI ({model}) for insights extraction from paragraphs.json...")
    start_time = time.time()

    # Call OpenAI
    result = call_openai(prompt, model=model)

    if not result:
        print("OpenAI API call failed")
        return None

    elapsed = time.time() - start_time
    print(f"✓ Insights extraction completed in {elapsed:.2f}s")

    # Add entity IDs
    if 'entities' in result:
        result['entities'] = add_entity_ids(result['entities'])

    return result


def extract_speaker_mapping(job_json: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Extract speaker mapping from job.json data."""

    if not job_json:
        return None

    # Look for speaker_labels in various places
    if 'speaker_labels' in job_json:
        labels = job_json['speaker_labels']
        if isinstance(labels, dict):
            # Handle nested structure
            if 'currentVersion' in labels:
                version = labels['currentVersion']
                if 'versions' in labels and version in labels['versions']:
                    version_data = labels['versions'][version]
                    if 'data' in version_data and 'speakers' in version_data['data']:
                        speakers = version_data['data']['speakers']
                        return {k: v.get('name', k) if isinstance(v, dict) else v
                               for k, v in speakers.items()}
            else:
                # Direct mapping
                return {k: v.get('name', k) if isinstance(v, dict) else v
                       for k, v in labels.items()}

    return None


def load_paragraphs(filepath: str) -> Optional[Dict[str, Any]]:
    """Load paragraphs.json from Whisper output."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading paragraphs.json: {e}")
        return None


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


def replace_speaker_labels(paragraphs: Dict[str, Any], speaker_mapping: Dict[str, str]) -> Dict[str, Any]:
    """
    Replace SPEAKER_XX labels with real names in paragraphs.

    Args:
        paragraphs: Dict with 'segments' array
        speaker_mapping: {SPEAKER_00: "Name", SPEAKER_01: None, ...}

    Returns:
        Modified paragraphs dict with speaker names replaced
    """
    if not paragraphs or not speaker_mapping:
        return paragraphs

    processed = paragraphs.copy()
    processed_segments = []

    for seg in paragraphs.get('segments', []):
        new_seg = seg.copy()
        speaker_label = seg.get('speaker', '')

        # Replace speaker label if we have a mapping
        if speaker_label in speaker_mapping and speaker_mapping[speaker_label]:
            new_seg['speaker'] = speaker_mapping[speaker_label]
        elif speaker_label.startswith('SPEAKER_'):
            # Fallback: SPEAKER_00 → Speaker 1
            speaker_num = speaker_label.replace('SPEAKER_', '')
            try:
                num = int(speaker_num) + 1
                new_seg['speaker'] = f"Speaker {num}"
            except ValueError:
                pass  # Keep original if can't parse

        processed_segments.append(new_seg)

    processed['segments'] = processed_segments
    return processed


def generate_readable_md(
    title: str,
    summary: str,
    takeaways: list,
    toc: list,
    paragraphs: Dict[str, Any]
) -> str:
    """
    Generate readable.md with chapter headings and timestamps.

    Args:
        title: Content title
        summary: 2-3 sentence summary
        takeaways: List of key points
        toc: Table of contents items [{timestamp, title, description}, ...]
        paragraphs: Processed paragraphs with speaker labels replaced

    Returns:
        Complete markdown document
    """

    # Header
    md = f"# {title}\n\n"

    # Summary
    md += "## Summary\n"
    md += f"{summary}\n\n"

    # Key Takeaways
    if takeaways:
        md += "## Key Takeaways\n"
        for takeaway in takeaways:
            md += f"- {takeaway}\n"
        md += "\n"

    # Table of Contents
    if toc:
        md += "## Table of Contents\n"
        for item in toc:
            ts = format_timestamp(item['timestamp'])
            seconds = int(item['timestamp'])
            md += f"- [[{ts}](#t={seconds})] {item['title']}\n"
        md += "\n"

    md += "---\n\n"
    md += "## Transcript\n\n"

    # Build chapter-segmented transcript
    segments = paragraphs.get('segments', [])
    toc_index = 0

    for i, seg in enumerate(segments):
        # Check if we need to insert a chapter heading
        if toc_index < len(toc):
            chapter = toc[toc_index]
            # Insert chapter when we reach or pass the chapter timestamp
            if seg['start'] >= chapter['timestamp']:
                # Insert chapter heading
                ts = format_timestamp(chapter['timestamp'])
                seconds = int(chapter['timestamp'])
                md += f"### [[{ts}](#t={seconds})] {chapter['title']}\n\n"
                toc_index += 1

        # Add paragraph with timestamp
        speaker = seg.get('speaker', 'Unknown')
        text = seg.get('text', '')
        ts = format_timestamp(seg['start'])
        seconds = int(seg['start'])

        md += f"**[[{ts}](#t={seconds})]** **{speaker}:** {text}\n\n"

    return md


# Test function for debugging
if __name__ == "__main__":
    sample_transcript = """
    SPEAKER_00: Good morning everyone, I'm Sarah Chen, CTO at Acme Corp.
    SPEAKER_01: Thanks Sarah. I'm John Smith, the CEO. Today we need to discuss our Q1 product launch.
    SPEAKER_00: Based on our progress, we can launch Platform v2.0 by March 31st with a budget of $2.5 million.
    SPEAKER_01: Great. Let's schedule a follow-up with Memorial Hospital next week.
    """

    result = generate_insights(
        sample_transcript,
        filename="2024-01-15_q1_planning.mp4",
        input_context="Q1 planning meeting with leadership team",
        speaker_mapping={"SPEAKER_00": "Sarah Chen", "SPEAKER_01": "John Smith"}
    )

    if result:
        print(json.dumps(result, indent=2))
    else:
        print("Failed to generate insights")