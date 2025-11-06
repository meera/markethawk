I#!/bin/bash
#
# Unified earnings video processing orchestrator
# Can run all steps or individual steps
#
# Usage:
#   Run all steps:
#     ./process-earnings.sh --url <youtube-url>
#
#   Run individual steps:
#     ./process-earnings.sh --url <url> --step download
#     ./process-earnings.sh --url <url> --step parse
#     ./process-earnings.sh --url <url> --step remove-silence
#     ./process-earnings.sh --url <url> --step transcribe
#     ./process-earnings.sh --url <url> --step insights
#     ./process-earnings.sh --url <url> --step render
#     ./process-earnings.sh --url <url> --step upload
#
#   Run from specific step onwards:
#     ./process-earnings.sh --url <url> --from transcribe
#

set -e  # Exit on error

# Directories
SUSHI_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_ROOT="$(cd "$SUSHI_DIR/.." && pwd)"
DOWNLOADS_DIR="/var/earninglens/_downloads"
ORGANIZED_DIR="/var/earninglens"

# Load environment
if [ -f "$PROJECT_ROOT/.env" ]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging
log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"; }
log_success() { echo -e "${GREEN}✓ $1${NC}"; }
log_error() { echo -e "${RED}✗ $1${NC}"; }
log_step() { echo ""; echo -e "${YELLOW}==>${NC} $1"; }
log_info() { echo -e "${CYAN}ℹ $1${NC}"; }

# Parse arguments
URL=""
STEP=""
FROM_STEP=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            URL="$2"
            shift 2
            ;;
        --step)
            STEP="$2"
            shift 2
            ;;
        --from)
            FROM_STEP="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Validate
if [ -z "$URL" ]; then
    echo -e "${RED}Usage:${NC}"
    echo "  Run all: $0 --url <youtube-url>"
    echo "  Run one: $0 --url <youtube-url> --step <step-name>"
    echo "  Run from: $0 --url <youtube-url> --from <step-name>"
    echo ""
    echo "Steps: download, parse, remove-silence, transcribe, insights, render, upload"
    exit 1
fi

# Extract video ID
VIDEO_ID=""
if [[ "$URL" =~ youtu\.be/([a-zA-Z0-9_-]+) ]]; then
    VIDEO_ID="${BASH_REMATCH[1]}"
elif [[ "$URL" =~ v=([a-zA-Z0-9_-]+) ]]; then
    VIDEO_ID="${BASH_REMATCH[1]}"
fi

if [ -z "$VIDEO_ID" ]; then
    log_error "Could not extract video ID from URL"
    exit 1
fi

# State file
STATE_FILE="$DOWNLOADS_DIR/$VIDEO_ID/.state.json"

# Activate Python env
if [ -f "$SUSHI_DIR/.venv/bin/activate" ]; then
    source "$SUSHI_DIR/.venv/bin/activate"
else
    log_error "Python venv not found. Run: cd $SUSHI_DIR && python3 -m venv .venv && pip install -r requirements.txt"
    exit 1
fi

# Helper: Update state
update_state() {
    local step=$1
    local status=$2
    local data=$3

    mkdir -p "$DOWNLOADS_DIR/$VIDEO_ID"

    if [ -f "$STATE_FILE" ]; then
        STATE=$(cat "$STATE_FILE")
    else
        STATE="{}"
    fi

    STATE=$(echo "$STATE" | jq --arg step "$step" --arg status "$status" --argjson data "$data" \
        '.steps[$step] = {status: $status, timestamp: now, data: $data}')

    echo "$STATE" > "$STATE_FILE"
}

# Helper: Get state
get_state() {
    local step=$1
    if [ -f "$STATE_FILE" ]; then
        jq -r ".steps[\"$step\"].status // \"not_started\"" "$STATE_FILE"
    else
        echo "not_started"
    fi
}

# Helper: Get state data
get_state_data() {
    local step=$1
    local key=$2
    if [ -f "$STATE_FILE" ]; then
        jq -r ".steps[\"$step\"].data.$key // empty" "$STATE_FILE"
    fi
}

# ============================================================================
# STEP FUNCTIONS
# ============================================================================

step_download() {
    log_step "Step 1/7: Download video"

    if [ "$(get_state download)" = "completed" ]; then
        log_info "Already downloaded, skipping"
        return 0
    fi

    python3 "$SUSHI_DIR/scripts/download-source.py" "$URL"

    update_state "download" "completed" "{\"video_id\": \"$VIDEO_ID\", \"url\": \"$URL\"}"
    log_success "Download complete"
}

step_parse() {
    log_step "Step 2/7: Parse metadata"

    if [ "$(get_state parse)" = "completed" ]; then
        log_info "Already parsed, skipping"
        return 0
    fi

    METADATA_FILE="$DOWNLOADS_DIR/$VIDEO_ID/input/metadata.json"

    if [ ! -f "$METADATA_FILE" ]; then
        log_error "Metadata not found. Run download step first."
        exit 1
    fi

    PARSE_RESULT=$(python3 "$SUSHI_DIR/scripts/parse-metadata.py" "$METADATA_FILE" | tail -1)

    TICKER=$(echo "$PARSE_RESULT" | jq -r '.ticker // empty')
    QUARTER=$(echo "$PARSE_RESULT" | jq -r '.quarter // empty')
    COMPANY_NAME=$(echo "$PARSE_RESULT" | jq -r '.company_name // empty')
    CONFIDENCE=$(echo "$PARSE_RESULT" | jq -r '.confidence // empty')

    if [ -z "$TICKER" ] || [ -z "$QUARTER" ]; then
        log_error "Could not parse company/quarter"
        log "Ticker: $TICKER, Quarter: $QUARTER, Company: $COMPANY_NAME"
        exit 1
    fi

    log_success "Detected: $COMPANY_NAME ($TICKER) $QUARTER (confidence: $CONFIDENCE)"

    # Create organized directory
    COMPANY_DIR="$ORGANIZED_DIR/$TICKER/$QUARTER"
    mkdir -p "$COMPANY_DIR"/{input,transcripts,take1}

    # Copy metadata
    cp "$METADATA_FILE" "$COMPANY_DIR/metadata.json"

    update_state "parse" "completed" "{\"ticker\": \"$TICKER\", \"quarter\": \"$QUARTER\", \"company_name\": \"$COMPANY_NAME\", \"company_dir\": \"$COMPANY_DIR\"}"
    log_success "Parse complete"
}

step_remove_silence() {
    log_step "Step 3/7: Remove initial silence"

    if [ "$(get_state remove_silence)" = "completed" ]; then
        log_info "Already trimmed, skipping"
        return 0
    fi

    TICKER=$(get_state_data parse ticker)
    QUARTER=$(get_state_data parse quarter)

    if [ -z "$TICKER" ] || [ -z "$QUARTER" ]; then
        log_error "Parse data not found. Run parse step first."
        exit 1
    fi

    SOURCE_FILE="$DOWNLOADS_DIR/$VIDEO_ID/input/source.mp4"
    COMPANY_DIR="$ORGANIZED_DIR/$TICKER/$QUARTER"
    TRIMMED_FILE="$COMPANY_DIR/input/source.mp4"

    python3 "$SUSHI_DIR/scripts/remove-silence.py" "$SOURCE_FILE" "$TRIMMED_FILE"

    update_state "remove_silence" "completed" "{\"trimmed_file\": \"$TRIMMED_FILE\"}"
    log_success "Silence removed"
}

step_transcribe() {
    log_step "Step 4/7: Transcribe with Whisper"

    if [ "$(get_state transcribe)" = "completed" ]; then
        log_info "Already transcribed, skipping"
        return 0
    fi

    TICKER=$(get_state_data parse ticker)
    QUARTER=$(get_state_data parse quarter)
    COMPANY_DIR="$ORGANIZED_DIR/$TICKER/$QUARTER"
    INPUT_FILE="$COMPANY_DIR/input/source.mp4"
    OUTPUT_FILE="$COMPANY_DIR/transcripts/transcript.json"

    if [ ! -f "$INPUT_FILE" ]; then
        log_error "Input file not found. Run previous steps first."
        exit 1
    fi

    python3 "$SUSHI_DIR/transcribe.py" "$INPUT_FILE" --output "$OUTPUT_FILE"

    update_state "transcribe" "completed" "{\"transcript\": \"$OUTPUT_FILE\"}"
    log_success "Transcription complete"
}

step_insights() {
    log_step "Step 5/7: Extract insights with LLM"

    if [ "$(get_state insights)" = "completed" ]; then
        log_info "Already extracted, skipping"
        return 0
    fi

    TICKER=$(get_state_data parse ticker)
    QUARTER=$(get_state_data parse quarter)
    COMPANY_DIR="$ORGANIZED_DIR/$TICKER/$QUARTER"
    TRANSCRIPT_FILE="$COMPANY_DIR/transcripts/transcript.json"
    OUTPUT_FILE="$COMPANY_DIR/transcripts/insights.json"

    if [ ! -f "$TRANSCRIPT_FILE" ]; then
        log_error "Transcript not found. Run transcribe step first."
        exit 1
    fi

    python3 "$SUSHI_DIR/process_video.py" "$TRANSCRIPT_FILE" --output "$OUTPUT_FILE"

    update_state "insights" "completed" "{\"insights\": \"$OUTPUT_FILE\"}"
    log_success "Insights extracted"
}

step_render() {
    log_step "Step 6/7: Render video with Remotion"

    if [ "$(get_state render)" = "completed" ]; then
        log_info "Already rendered, skipping"
        return 0
    fi

    if ! command -v node &> /dev/null; then
        log_error "Node.js not installed. Skipping render."
        return 0
    fi

    TICKER=$(get_state_data parse ticker)
    QUARTER=$(get_state_data parse quarter)
    COMPANY_DIR="$ORGANIZED_DIR/$TICKER/$QUARTER"
    OUTPUT_FILE="$COMPANY_DIR/take1/final.mp4"

    node "$SUSHI_DIR/scripts/render-video.js" "$COMPANY_DIR" "$OUTPUT_FILE"

    update_state "render" "completed" "{\"video\": \"$OUTPUT_FILE\"}"
    log_success "Video rendered"
}

step_upload() {
    log_step "Step 7/7: Upload to YouTube"

    if [ "$(get_state upload)" = "completed" ]; then
        log_info "Already uploaded, skipping"
        return 0
    fi

    TICKER=$(get_state_data parse ticker)
    QUARTER=$(get_state_data parse quarter)
    COMPANY_DIR="$ORGANIZED_DIR/$TICKER/$QUARTER"
    VIDEO_FILE="$COMPANY_DIR/take1/final.mp4"

    if [ ! -f "$VIDEO_FILE" ]; then
        log_error "Video not found. Run render step first."
        exit 1
    fi

    node "$SUSHI_DIR/scripts/upload-youtube.js" "$COMPANY_DIR"

    update_state "upload" "completed" "{\"status\": \"uploaded\"}"
    log_success "Uploaded to YouTube"
}

# ============================================================================
# EXECUTION LOGIC
# ============================================================================

ALL_STEPS=(download parse remove_silence transcribe insights render upload)

# Run single step
if [ -n "$STEP" ]; then
    log "Running single step: $STEP"
    case $STEP in
        download) step_download ;;
        parse) step_parse ;;
        remove-silence) step_remove_silence ;;
        transcribe) step_transcribe ;;
        insights) step_insights ;;
        render) step_render ;;
        upload) step_upload ;;
        *)
            log_error "Unknown step: $STEP"
            exit 1
            ;;
    esac
    exit 0
fi

# Run from specific step onwards
if [ -n "$FROM_STEP" ]; then
    log "Running from step: $FROM_STEP onwards"
    FOUND=false
    for step in "${ALL_STEPS[@]}"; do
        if [ "$step" = "$FROM_STEP" ]; then
            FOUND=true
        fi
        if [ "$FOUND" = true ]; then
            step_${step//-/_}
        fi
    done
    exit 0
fi

# Run all steps
log "Running all steps for: $URL"
echo ""

step_download
step_parse
step_remove_silence
step_transcribe
step_insights
step_render
step_upload

# Final summary
echo ""
log_success "========================================"
log_success "All steps complete!"
log_success "========================================"
echo ""

TICKER=$(get_state_data parse ticker)
QUARTER=$(get_state_data parse quarter)
COMPANY_NAME=$(get_state_data parse company_name)
COMPANY_DIR="$ORGANIZED_DIR/$TICKER/$QUARTER"

log "Company: $COMPANY_NAME ($TICKER) $QUARTER"
log "Location: $COMPANY_DIR"
echo ""
log "Files:"
log "  - Video: $COMPANY_DIR/take1/final.mp4"
log "  - Transcript: $COMPANY_DIR/transcripts/transcript.json"
log "  - Insights: $COMPANY_DIR/transcripts/insights.json"
echo ""
log "Original download: $DOWNLOADS_DIR/$VIDEO_ID"
log "State file: $STATE_FILE"
echo ""
