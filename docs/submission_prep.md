# Submission Preparation Checklist (DOC 09)

## Required Links

| Field | Link | Status |
|-------|------|--------|
| GitHub repo | https://github.com/Ayush10/replicalab-ai | Ready |
| HF Space | https://ayushozha-replicalab.hf.space | Live |
| Demo video (YouTube) | _pending upload_ | DOC 07 |
| Colab notebook | `notebooks/train_colab.ipynb` (link after push) | Ready |
| Fallback demo | https://ayushozha-replicalab.hf.space/web | Ready |

## Partner Track Selections

| Track | Justification |
|-------|---------------|
| **Multi-Agent Interactions** | Two roles (Scientist + Lab Manager) with private information negotiate toward consensus |
| **World Modeling (Professional)** | Agent reasons inside a professional world with hidden constraints and resource limits |
| **Long-Horizon Planning** | Multi-round ask-revise-recover-converge cycle over up to 6 negotiation rounds |
| **Self-Improvement** | Scientist measurably improves over repeated RL training episodes |

## Pre-submission Verification

- [ ] GitHub repo is public (`gh repo view --json isPrivate`)
- [ ] HF Space is live and `/health` returns 200
- [ ] `/web` fallback works on HF Space
- [ ] Demo video is uploaded and accessible (unlisted YouTube)
- [ ] README has results table, setup instructions, and architecture diagram
- [ ] No API keys or secrets in tracked files
- [ ] All team members listed in README

## Submission Form Fields

Fill in the submission form with the links above. Double-check:

- Project name: **ReplicaLab**
- Team members: Ayush, Kian, Max, Kush
- One-line summary: _Multi-agent constraint-aware negotiation environment that trains an AI Scientist to negotiate feasible replication plans under real-world resource constraints._
- Tracks: Multi-Agent Interactions, World Modeling, Long-Horizon Planning, Self-Improvement
