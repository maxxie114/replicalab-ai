# Screen Recording and Video Guide (DOC 06, DOC 07, OBS 08)

---

## Screenshots to Capture (OBS 08)

Save all screenshots to `docs/screenshots/`. Use PNG format at 1920x1080 or higher.

### Required Screenshots

1. **`hf-space.png`** -- HF Space landing page
2. **`dashboard-hero.png`** -- Dashboard with 3D molecule background, three characters, and "Run Episode" button
3. **`dashboard-cast.png`** -- "Meet the Cast" section with the three tilt cards
4. **`episode-negotiation.png`** -- Active episode showing CharacterStage + negotiation log with at least 2 messages
5. **`episode-judge.png`** -- Judge character center-stage during the judging phase
6. **`episode-scores.png`** -- Complete episode with score card, Judge audit panel, and replay viewer
7. **`training-results.png`** -- Training Results panel with both baseline and trained lines visible
8. **`replay-viewer.png`** -- Replay viewer with the scrubber at a mid-episode position

### Optional GIFs

- **`character-tilt.gif`** -- Mouse hovering over a role card showing the 3D tilt effect
- **`judge-entrance.gif`** -- Judge dropping into center-stage with the scoring animation
- **`negotiation-flow.gif`** -- Messages sliding into the negotiation log

**Tool recommendation**: Use ShareX (Windows), CleanShot (Mac), or the browser DevTools screenshot tool.

---

## Screen Recording (DOC 06)

### Setup

1. Resolution: **1920x1080** (or 2560x1440 if Retina, then scale down in edit)
2. Browser: Chrome or Edge, no bookmarks bar, clean profile
3. Frontend: Running at `http://localhost:5175/`
4. Backend: Running at `http://localhost:7860/` or use the HF Space
5. Audio: Enable system audio to capture the built-in sound effects

### Recording Tool

- **OBS Studio** (free, all platforms) -- best for high quality
- **Loom** -- quick and easy, auto-uploads
- **Windows Game Bar** (Win+G) -- built-in, no install needed

### Clips to Record

Follow the demo script in `docs/demo_script.md`. Record each scene as a separate clip:

| Clip | Duration | Content |
|------|----------|---------|
| `clip1-hook.mp4` | 8s | Dashboard hero with molecules, slow scroll |
| `clip2-cast.mp4` | 8s | Hover over tilt cards, show character names |
| `clip3-start.mp4` | 8s | Select ML Benchmark, click Start |
| `clip4-negotiate.mp4` | 14s | Watch negotiation log fill, scroll through messages |
| `clip5-judge.mp4` | 10s | Click Step, judge entrance, gavel, score reveal |
| `clip6-training.mp4` | 8s | Training Results, toggle baseline/trained |
| `clip7-close.mp4` | 4s | Return to dashboard, show URL |

Save raw clips to `docs/video/` (gitignored).

---

## Final Video Edit (DOC 07)

### Editing

1. Import all clips into a video editor (DaVinci Resolve free, CapCut, or iMovie)
2. Trim to fit the 60-second target
3. Add captions from the demo script narration lines
4. Add a title card: "ReplicaLab -- OpenEnv Hackathon"
5. Add an end card with the GitHub URL and HF Space link
6. Export at 1080p, H.264, 30fps

### Upload

1. Upload to YouTube as **Unlisted**
2. Title: `ReplicaLab - Multi-Agent Scientific Replication Environment | OpenEnv Hackathon`
3. Description: Include the GitHub repo URL and HF Space link
4. Copy the YouTube URL for the submission form

### Checklist

- [ ] Video is under 60 seconds
- [ ] Captions are readable
- [ ] Audio (sound effects) is audible but not overpowering
- [ ] All key scenes are covered: hook, cast, episode, judge, training, close
- [ ] YouTube link is accessible (unlisted, not private)
- [ ] Link is added to the submission form
