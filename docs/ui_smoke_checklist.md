# UI Smoke Test Checklist (UI 12 + TST 08 + TST 12)

Run through this checklist before every demo or merge to main. Target: under 5 minutes.

---

## Pre-requisites

- [ ] Backend server is running on `localhost:7860` (or HF Space is live)
- [ ] Frontend dev server is running on `localhost:5173` (or built and served from Docker)

---

## Dashboard Page

- [ ] Page loads without console errors
- [ ] 3D molecule scene renders in hero background (subtle, low opacity)
- [ ] All three characters visible: Dr. Elara, Takuma, Aldric
- [ ] Character tilt cards respond to mouse hover with 3D effect
- [ ] "Run Episode" button navigates to `/episode`
- [ ] "Training Results" anchor scrolls to the chart section
- [ ] Scenario card links navigate to `/episode?template=ml_benchmark`
- [ ] Training Results chart renders with baseline and trained lines
- [ ] Before/after toggle switches between baseline and trained views
- [ ] Metric cards show Avg Reward, Agreement, Avg Rounds, Invalid Rate

---

## Episode Page -- Pre-game

- [ ] All three characters display with names (Dr. Elara, Takuma, Aldric)
- [ ] Controls panel shows: Scenario selector, Difficulty buttons, Seed input, Dice button
- [ ] Default scenario is "ML Benchmark"
- [ ] Start Episode button is enabled

---

## Episode Page -- Running Episode

- [ ] Clicking "Start Episode" plays episode start sound
- [ ] CharacterStage appears with Scientist and Lab Manager
- [ ] Judge observer icon appears in top-right corner with "Observing" label
- [ ] Paper panel shows ViT paper title, hypothesis, method, key finding
- [ ] Episode ID is displayed and copyable in the Episode Info section
- [ ] Negotiation log shows messages with animated character avatars
- [ ] Each message entry has a slide-in animation
- [ ] Protocol panel updates with current plan
- [ ] Lab Inventory panel shows GPU, budget, and staff constraints
- [ ] Round progress bar fills proportionally
- [ ] "Step" button is visible and enabled

---

## Episode Page -- Judging Phase

- [ ] Clicking "Step" triggers negotiate sound
- [ ] Judge character appears center-stage with dramatic entrance animation
- [ ] Judge appear sound plays, followed by gavel sound
- [ ] Phase indicator shows "Judging" with pulsing dot
- [ ] Judging phase lasts approximately 4 seconds

---

## Episode Page -- Complete Phase

- [ ] Score reveal sound plays
- [ ] Success/failure sound plays based on verdict
- [ ] Judge stays center-stage with verdict action
- [ ] Score card shows total reward (8.12) with R/F/D breakdown
- [ ] JudgeAuditPanel appears below the negotiation log
- [ ] Judge audit shows verdict, notes, and score details
- [ ] Replay viewer appears in the right panel
- [ ] Score panel shows component scores

---

## Replay Viewer

- [ ] Forward/back buttons step through messages
- [ ] Skip-to-start and skip-to-end buttons work
- [ ] Scrubber slider moves to the correct message
- [ ] Character avatars display for each replayed message
- [ ] Message content matches the original negotiation

---

## Fallback Path

- [ ] Navigate to `{server_url}/web` -- OpenEnv fallback UI loads
- [ ] Fallback UI can start a seeded episode
- [ ] Fallback UI shows step results

---

## Audio

- [ ] Button clicks produce click sound
- [ ] Episode start plays ascending chime
- [ ] Scientist messages play triangle-wave blips
- [ ] Lab Manager messages play square-wave blips
- [ ] Judge appearance plays dramatic chord
- [ ] Gavel sound plays during judging
- [ ] Score reveal plays ascending arpeggio

---

## Responsiveness

- [ ] Layout is usable at 1280px width (typical demo screen)
- [ ] No horizontal scroll at 1024px width
- [ ] Three-panel layout stacks on narrow viewports

---

## Sign-off

| Tester | Date | Pass/Fail | Notes |
|--------|------|-----------|-------|
| | | | |
