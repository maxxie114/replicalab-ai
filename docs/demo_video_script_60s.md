# ReplicaLab 60s Demo Script

## Voiceover

ReplicaLab starts from a research paper and turns it into a seeded replication benchmark. The Scientist proposes a protocol, the Lab Manager enforces budget, tools, and scheduling, and a deterministic Judge scores rigor, feasibility, and fidelity. In our first scenario, the agents agree immediately, so the paper looks replicable in this lab. In the second scenario, they negotiate across all six rounds, which creates a rich reinforcement learning signal. In the third, they never resolve the blockers, so the system rejects the paper for the current setup. Because every outcome is scored deterministically, we can train the Scientist with Unsloth and TRL, compare baseline versus trained runs, inspect real logs, and see exactly where more learning is still needed. The training page is intentionally honest: the live run reached positive rewards, but the held-out compare still shows that the trained Scientist has not beaten the deterministic baseline yet.

## Shot List

1. Dashboard hero: introduce ReplicaLab and the paper-to-training loop.
2. First-round agreement: show a clean acceptance and high replicability score.
3. Multi-round learning: show six-round negotiation and the learning-opportunity results panel.
4. No agreement: show the timeout / rejection outcome and low reliability signal.
5. Training page: show artifact-backed logs, checkpoints, baseline-vs-trained compare, and the explicit note that more training is still required.
