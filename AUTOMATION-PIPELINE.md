# Automation Pipeline - Scale to 1000+ Companies

## Vision

**Mass produce fantastic, visually appealing earnings videos at scale.**

- Every company (S&P 500, Russell 2000, International)
- Every quarter (4x per year)
- Within hours of earnings call
- Consistent quality
- Zero manual video editing

---

## The Value Proposition

### What We Do Best
1. **Visually Appealing Videos** - Transform drab earnings calls into engaging content
2. **Compelling Storytelling** - Turn data into narratives
3. **Automated at Scale** - 1000+ companies, 4000+ videos per year
4. **Speed** - Full video hours after earnings call ends

### What We DON'T Do
- ❌ Manual video production (can't scale)
- ❌ Just aggregate data (data is commodity)
- ❌ Provide opinions/analysis (we present facts)
- ❌ Wait days to publish (speed matters)

**We compete on presentation and automation, not data.**

---

## Automation Pipeline

### Phase 1: Manual (Week 1-2)
**Goal:** Generate first 10 videos to validate approach

```
1. Download audio (manual)
2. Create transcript (manual with your speaker tech)
3. Download speaker photos (manual)
4. Fill data JSON (manual)
5. Render video (automated - Remotion)
6. Upload to R2 (automated - script)
7. Upload to YouTube (manual)
8. Create 10 Shorts (manual editing)
```

**Time per video:** 4-6 hours
**Output:** 10 videos in 2 weeks

### Phase 2: Semi-Automated (Week 3-8)
**Goal:** 50 videos for YouTube monetization

```
1. Download audio (scripted - yt-dlp)
2. Create transcript (automated - AssemblyAI/Deepgram)
3. Download speaker photos (one-time database)
4. Fill data JSON (template + API)
5. Render video (automated - Remotion)
6. Upload to R2 (automated - script)
7. Upload to YouTube (API automation)
8. Create 10 Shorts (semi-automated - templates)
```

**Time per video:** 1-2 hours (mostly review)
**Output:** 50 videos in 6 weeks

### Phase 3: Fully Automated (Month 3+)
**Goal:** 500+ videos per quarter

```
1. Download audio (scheduled - monitor earnings calendar)
2. Create transcript (automated - speaker diarization)
3. Speaker photos (database lookup)
4. Data JSON (auto-generated from transcript + SEC filings)
5. Render video (background workers)
6. Upload to R2 (automated)
7. Upload to YouTube (API batch)
8. Create 10 Shorts (AI-selected key moments)
9. Quality review (human checks 10% sample)
```

**Time per video:** 15-30 minutes (mostly QA)
**Output:** 100+ videos per week during earnings season

---

## Technical Architecture

### Data Sources (Automated)
```python
# 1. Earnings Calendar
calendar_api = EarningsCalendar(providers=['yahoo', 'nasdaq'])
upcoming = calendar_api.get_upcoming(days=7)

# 2. Audio Download
for call in upcoming:
    audio = download_earnings_audio(
        company=call.ticker,
        sources=['youtube', 'company_ir', 'seeking_alpha']
    )

# 3. Speaker Diarization
transcript = diarize_audio(
    audio_path=audio,
    speakers=get_company_executives(call.ticker)
)

# 4. Key Metrics Extraction
metrics = extract_metrics(
    transcript=transcript,
    sec_filing=get_latest_filing(call.ticker)
)

# 5. Video Rendering
render_job = remotion.render(
    composition='EarningsCallVideo',
    props={
        'audio': audio,
        'transcript': transcript,
        'metrics': metrics,
        'speakers': get_speaker_photos(call.ticker)
    }
)

# 6. Upload to R2 + YouTube
upload_pipeline(video=render_job.output)

# 7. Create Shorts
shorts = extract_key_moments(
    video=render_job.output,
    transcript=transcript,
    count=10
)
batch_upload_shorts(shorts)
```

### Infrastructure

**Development (Week 1-8):**
- Local GPU rendering
- Manual triggers
- Small batch processing

**Production (Month 3+):**
- Cloud GPU rendering (AWS G4/G5 instances)
- Scheduled triggers (earnings calendar)
- Batch processing (50+ videos/day)
- Auto-scaling based on earnings season

### Cost Estimation

**Per Video Costs:**
- Audio transcription: $0.10 (AssemblyAI)
- Speaker diarization: $0.05
- GPU rendering (1 hour): $0.50
- Storage (R2): $0.02/month
- YouTube API: Free
**Total:** ~$0.70 per video

**At Scale (500 videos/quarter):**
- Video production: $350
- Storage: $10/month
- Infrastructure: $500/month
**Total:** ~$1000/quarter

**Revenue Potential:**
- YouTube ads: $2000-5000/month (after monetization)
- Website subs: $5000-20000/month (100-500 paying users)
**ROI:** 5-20x

---

## Quality Control

### Automated Checks
- ✅ Audio duration matches video duration
- ✅ All transcript segments have timing
- ✅ All metrics from transcript have sources
- ✅ Speaker photos exist and load
- ✅ No data fabrication (cross-check with SEC)
- ✅ Video renders successfully
- ✅ File size within limits

### Manual Review (10% sample)
- Visual quality (overlays render correctly)
- Audio sync (speaker shows when speaking)
- Metric accuracy (numbers match audio)
- No errors in text overlays
- Branding consistent

### Trust Verification
**The Three Pillars Check:**
1. Audio matches original source? ✓
2. Data from SEC filings? ✓
3. Initial prompt followed? ✓

If any pillar fails → don't publish, flag for review

---

## Scaling Milestones

### Week 8: 50 Videos
- Manual/semi-automated
- YouTube monetization enabled
- Proof of concept validated

### Month 3: 150 Videos
- Semi-automated pipeline
- Template refinement
- Quality metrics established

### Month 6: 500 Videos
- Fully automated pipeline
- Earnings season coverage
- Multiple video formats (full, shorts, clips)

### Month 12: 2000+ Videos
- All S&P 500 companies
- Historical earnings library
- International expansion (Europe, Asia)
- Multi-language support

### Year 2: 4000+ Videos/Year
- All publicly traded companies (USA)
- Real-time rendering during calls
- Live streaming enhanced calls
- White-label for institutions

---

## Automation Priorities

### Now (Week 1-8)
1. ✅ Remotion rendering (automated)
2. ✅ R2 upload script (automated)
3. ⏳ Audio download script (next)
4. ⏳ Speaker diarization integration (next)
5. ⏳ YouTube upload API (next)

### Month 3-6
1. Earnings calendar monitoring
2. Auto-trigger rendering pipeline
3. NLP for key metrics extraction
4. Auto-generate Shorts from moments
5. Batch processing optimization

### Month 6-12
1. Real-time rendering (during call)
2. Multi-company parallel processing
3. Quality scoring (auto-flag issues)
4. Historical library generation
5. API for enterprise access

---

## Success Metrics

### Automation Efficiency
- **Manual time per video:** <30 minutes (review only)
- **Render time:** <1 hour per 60-min video
- **Upload time:** <10 minutes
- **End-to-end:** <2 hours from call end to published

### Quality Metrics
- **Accuracy:** 99.9% (no data errors)
- **Audio sync:** 100% (perfect timing)
- **Visual quality:** 95%+ (no rendering errors)
- **Trust violations:** 0 (strict adherence)

### Scale Metrics
- **Videos per week:** 100+ (during earnings season)
- **Companies covered:** 500+ (by Month 12)
- **Shorts per video:** 10
- **Total content pieces:** 5000+ videos, 50000+ Shorts (Year 2)

---

## Competitive Advantage

### Why We Win

**1. Automation at Scale**
- Competitors: Manual video production (slow, expensive)
- Us: Automated pipeline (fast, cheap, scalable)

**2. Visual Storytelling**
- Competitors: Text transcripts, static charts
- Us: Dynamic visuals, engaging presentation

**3. Speed to Market**
- Competitors: Days after earnings call
- Us: Hours after earnings call (eventually: real-time)

**4. Trust**
- Competitors: Summarize, interpret, add opinions
- Us: Original audio, verified data only

**5. Distribution**
- Competitors: Website only
- Us: YouTube (discovery) + Shorts (viral) + Website (conversion)

---

## The Flywheel

```
More videos → More content → Better SEO
     ↓
More views → More subscribers → More watch time
     ↓
Monetization → More revenue → Better automation
     ↓
Scale to 1000+ companies → Market leader
```

**Goal:** Become the default destination for visual earnings content.

---

## Summary

**What makes MarketHawk special:**
1. 🎨 **Visually fantastic** - Engaging video production
2. 📖 **Compelling stories** - Data-driven narratives
3. 🤖 **Automated pipeline** - Mass production at scale
4. ⚡ **Speed** - Hours after earnings call
5. 🛡️ **Trust** - Three pillars (audio + SEC + prompt)

**We don't compete on data. We compete on presentation and automation.**

**Next Step:** Build the automation pipeline, one piece at a time.
