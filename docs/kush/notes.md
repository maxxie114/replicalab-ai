# Person D Notes

Use this file for working notes and short-term reminders.

Durable deviations belong in `docs/changes.md`.

---

## 2026-03-08 demo-flow refinement

- Dashboard now frames the product as `paper -> brief -> negotiate -> judge -> train`.
- Episode page now foregrounds the source paper and explicitly connects the terminal judge result to the training loop.
- Controls now read as replication setup instead of generic episode controls.
- Compare page is positioned as a seeded evaluation bench rather than the primary training-results story.
- The frontend default step action is now scenario-aware, so the live episode path produces valid judged runs instead of immediate invalid-action penalties on ML cases.
- The negotiation panel now shows an explicit `Advance First Round` CTA so a newly reset episode no longer looks frozen at `0 messages`.
- The dashboard `Replicate a Paper` CTA now launches a seeded live demo automatically: reset, first proposal, autoplay, and judged completion all happen without extra clicks.
- The replication setup card now performs a backend health check up front and surfaces a concrete startup command instead of the opaque browser-level `Failed to fetch` message when the API server is down.

