# ReplicaLab: 50 Scenario Templates and Training Plan

## Domain Distribution

| Domain | Count | Rationale |
|---|---|---|
| Computational ML/DL | 20 | Most relatable to judges, richest compute constraint space |
| Wet-Lab Biology | 16 | Strongest replication crisis narrative, most varied equipment |
| Quantitative Finance | 14 | Broadest appeal, most concrete measurable constraints |

---

## Domain 1: Computational ML/DL (20 Scenarios)

### Cluster A: Training Replication (7 papers)

These are "we trained a model and got results" papers. The core tension is always compute, data, and time.

| # | Paper Title | Claim | Key Technique | Original Resources | Primary Constraint Tension |
|---|---|---|---|---|---|
| 1 | ResNet Depth Scaling on ImageNet | Deeper networks improve accuracy up to 152 layers | ResNet architecture with skip connections | 8xV100, 90 epochs, full ImageNet (1.2M images) | Lab has 1xH100, budget for 30 epochs, only ImageNet-100 subset |
| 2 | BERT Fine-Tuning for Sentiment | BERT-large fine-tuned beats all baselines on SST-2 | BERT-large 340M params, AdamW | 4xA100 80GB, SST-2 full, 3 epochs | Lab has 1x40GB GPU, must use BERT-base or quantized BERT-large |
| 3 | Diffusion Model for Image Synthesis | DDPM generates high-fidelity 256x256 faces | U-Net with 1000 diffusion steps | 8xA100, CelebA-HQ, 500K steps | Lab has 1xH100, budget for 100K steps, only CelebA (not HQ) |
| 4 | RL Agent for Atari Games | PPO agent achieves superhuman on 40/57 Atari games | PPO with frame stacking | 256 CPU actors, 1xGPU learner, 200M frames | Lab has 16 CPU cores, 1xGPU, budget for 10M frames, test on 5 games only |
| 5 | GAN Training Stability | StyleGAN2 produces photorealistic 1024x1024 output | Progressive growing, R1 regularization | 8xV100, FFHQ 70K images, 25M images shown | Lab has 1xH100, only FFHQ 10K subset, budget for 5M images shown |
| 6 | Vision Transformer Pretraining | ViT-Large pretrained on JFT-300M matches CNN | ViT-L/16 with patch embedding | TPUv3 pod, JFT-300M (proprietary), 300 epochs | Lab has 1xH100, only ImageNet-21K (public), ViT-Base budget only |
| 7 | LLM Instruction Tuning | SFT on curated instructions improves helpfulness | LoRA on 7B base model | 4xA100, 50K curated instructions, 3 epochs | Lab has 1xH100, only 10K public instructions (Alpaca), rank-16 LoRA max |

### Cluster B: Evaluation/Benchmark Replication (6 papers)

These are "we evaluated X and found Y" papers. Tension is around evaluation methodology and data access.

| # | Paper Title | Claim | Key Technique | Original Resources | Primary Constraint Tension |
|---|---|---|---|---|---|
| 8 | LLM Benchmark Contamination | GPT-4 performance drops 12% on decontaminated MMLU | Custom decontamination pipeline | Full MMLU, GPT-4 API ($2K budget), custom regex filters | Lab has $200 API budget, must use open-source LLM, no custom decontamination tool |
| 9 | Fairness Audit of Hiring Model | Commercial hiring model shows 23% TPR gap across demographics | Adversarial probing with synthetic candidates | Access to proprietary model API, 10K synthetic resumes, 6 demographic axes | Lab has no API access, must train proxy model, budget for 2K synthetic resumes |
| 10 | Cross-lingual Transfer | mBERT zero-shot works for NER in 40 languages | mBERT with English-only fine-tuning | All 40 CoNLL languages, mBERT-base | Lab has compute for 10 languages, some language datasets have licensing issues |
| 11 | OOD Detection Benchmark | Energy score beats MSP on 6 OOD benchmarks | Energy-based OOD scoring | 6 OOD datasets, ResNet-18 pretrained, custom evaluation suite | Lab missing 2 of 6 datasets (licensing), must justify subset evaluation |
| 12 | Prompt Sensitivity Study | GPT-3.5 accuracy varies 15% across prompt formats | Systematic prompt variation, 50 formats | GPT-3.5 API ($1.5K budget), 50 prompt templates, 5 benchmarks | Lab has $300 budget, can test 15 formats on 3 benchmarks |
| 13 | Model Compression | 4-bit quantized LLaMA-7B retains 95% of quality | GPTQ quantization | Full LLaMA-7B weights, custom GPTQ kernel, 8 benchmarks | Lab has weights but GPTQ kernel incompatible with CUDA version, must use alternative quantizer |

### Cluster C: Method/Architecture Replication (7 papers)

These are "we propose method X and it outperforms baselines" papers. Tension is around implementation fidelity and baseline reproduction.

| # | Paper Title | Claim | Key Technique | Original Resources | Primary Constraint Tension |
|---|---|---|---|---|---|
| 14 | Attention Mechanism Ablation | Multi-head attention outperforms single-head by 2.1 BLEU | Transformer encoder-decoder | 4xV100, WMT14 En-De (4.5M pairs), custom tokenizer | Lab has 1xH100, WMT14 subset (1M pairs), must use HuggingFace tokenizer |
| 15 | Contrastive Learning for Vision | SimCLR outperforms supervised pretraining with 1% labels | SimCLR with large batch (4096) | 128 TPU cores, ImageNet, batch size 4096 | Lab has 1xH100, max batch 256 (need gradient accumulation), memory constraints |
| 16 | Graph Neural Network for Molecules | GIN outperforms GCN on molecular property prediction | Graph Isomorphism Network | 8 molecular datasets, custom data pipeline, RDKit preprocessing | Lab missing RDKit (incompatible Python version), 5 of 8 datasets available |
| 17 | Knowledge Distillation | DistilBERT retains 97% of BERT performance at 60% size | Task-agnostic distillation | BERT-base teacher, BookCorpus+Wikipedia, 3 days training | Lab has BERT-base but BookCorpus no longer publicly available, Wikipedia only |
| 18 | Neural Architecture Search | DARTS finds architecture matching hand-designed on CIFAR-10 | Differentiable architecture search | 1xV100 for search (1.5 days), 1xV100 for evaluation | Lab has 1xH100 (faster) but only 8 hours allocated, must reduce search space |
| 19 | Data Augmentation | RandAugment matches AutoAugment without search cost | Random augmentation policy | ResNet-50, ImageNet, 270 epochs, grid search over N and M | Lab has compute for 90 epochs, budget for partial grid search (5 of 15 configs) |
| 20 | Federated Learning | FedAvg converges with 100 non-IID clients | Federated averaging | 100 simulated clients, CIFAR-10, 500 communication rounds | Lab can simulate 20 clients, budget for 200 rounds, must argue this is sufficient |

---

## Domain 2: Wet-Lab Biology (16 Scenarios)

### Cluster D: Cell Biology and Biochemistry (8 papers)

| # | Paper Title | Claim | Key Technique | Original Resources | Primary Constraint Tension |
|---|---|---|---|---|---|
| 21 | Drug Cytotoxicity Dose-Response | Compound X has IC50 of 2.3 uM against HeLa cells | MTT assay, 8-point dose-response | Plate reader, MTT reagent, HeLa cells, 96-well plates, n=6 replicates | Lab plate reader booked Mon-Wed, MTT backordered (WST-1 available), budget for n=4 |
| 22 | siRNA Knockdown Efficiency | siRNA targeting BRCA1 achieves 85% knockdown | qPCR quantification, lipofection | Real-time PCR machine, lipofectamine, BRCA1 primers, Western blot validation | qPCR machine shared (available Thu-Fri only), no Western blot antibody in stock |
| 23 | Protein Expression and Purification | Recombinant GFP-tagged protein expressed in E. coli at 50 mg/L | IPTG induction, Ni-NTA purification | Shaker incubator, FPLC, Ni-NTA resin, IPTG, competent cells | FPLC needs maintenance (2 days), can use gravity column instead, slower but cheaper |
| 24 | Flow Cytometry Apoptosis | Drug Y induces 60% apoptosis via Annexin V/PI staining | Flow cytometry with dual staining | Flow cytometer, Annexin V kit, PI, cell culture facility | Flow cytometer calibration expired, Annexin V kit expires in 5 days (cutting it close) |
| 25 | Wound Healing Migration | Compound Z accelerates wound closure by 40% in 24h | Scratch assay with time-lapse imaging | Inverted microscope with camera, cell culture hood, 6-well plates, n=5 | Microscope camera resolution lower than paper (can we still quantify?), n=3 budget |
| 26 | CRISPR Gene Editing | CRISPR-Cas9 knockout of TP53 in MCF-7 cells | CRISPR with guide RNA, Sanger sequencing | Electroporation system, guide RNA, Cas9 protein, sequencing service | Electroporation system unavailable, must use lipofection (lower efficiency expected) |
| 27 | Enzyme Kinetics | Km of novel enzyme variant is 15 uM | Michaelis-Menten kinetics, spectrophotometric assay | UV-Vis spectrophotometer, substrate concentrations (10 points), purified enzyme | Spectrophotometer wavelength range limited, 6 concentration points max (budget) |
| 28 | Bacterial Growth Curve | Antibiotic resistance mutation confers 3x MIC increase | Broth microdilution, OD600 measurement | Plate reader (kinetic mode), Mueller-Hinton broth, antibiotic stock, 12h monitoring | Plate reader does not support kinetic mode, must do manual timepoint readings |

### Cluster E: Behavioral and Cognitive (4 papers)

| # | Paper Title | Claim | Key Technique | Original Resources | Primary Constraint Tension |
|---|---|---|---|---|---|
| 29 | Ego Depletion Replication | Self-control depletion reduces performance on Stroop task | Sequential task paradigm | n=200 participants, Stroop software, two-room setup, 4 experimenters | IRB timeline 3 weeks, budget for n=80, 1 experimenter available, one room |
| 30 | Priming Effect on Behavior | Exposure to achievement words improves puzzle performance | Scrambled sentence priming | n=150, computerized tasks, between-subjects design, debriefing protocol | n=60 budget, online-only (no in-person), must address demand characteristics |
| 31 | Sleep and Memory Consolidation | 8h sleep improves word-pair recall by 25% vs sleep deprivation | Within-subjects, polysomnography | Sleep lab, PSG equipment, n=30, 2 sessions per participant | No sleep lab access, must use actigraphy (wrist device) as proxy, n=15 |
| 32 | Social Conformity in Groups | Group pressure changes individual opinions 35% of the time | Asch-style paradigm with confederates | 4 trained confederates, n=100 naive participants, recording equipment | Budget for 2 confederates, n=40, must justify reduced group size |

### Cluster F: Environmental and Ecological (4 papers)

| # | Paper Title | Claim | Key Technique | Original Resources | Primary Constraint Tension |
|---|---|---|---|---|---|
| 33 | Soil Microbiome Diversity | Fertilizer reduces bacterial diversity by 30% | 16S rRNA sequencing, alpha diversity | Sequencing service, soil sampling kit, 20 sites, triplicate | Sequencing budget for 10 sites only, duplicate instead of triplicate |
| 34 | Water Pollutant Detection | Novel biosensor detects lead at 5 ppb sensitivity | Electrochemical impedance spectroscopy | Potentiostat, custom electrode, calibration standards, DI water system | Potentiostat model different from paper (lower frequency range), must validate equivalence |
| 35 | Plant Growth Under LED Spectra | Blue-enriched LED increases lettuce biomass 20% | Controlled growth chamber, spectral analysis | Growth chamber (4 compartments), LED panels, 30-day trial, 20 plants per group | Growth chamber has 2 compartments (not 4), must run sequential instead of parallel |
| 36 | Algal Bloom Prediction | Phosphorus concentration predicts bloom onset within 5 days | Spectrophotometric phosphorus assay, regression model | Lake access permit, sampling boat, reagents for 100 samples, 6-month dataset | Permit pending (2 weeks), budget for 50 samples, 3-month window only |

---

## Domain 3: Quantitative Finance (14 Scenarios)

### Cluster G: Trading Strategy Replication (6 papers)

| # | Paper Title | Claim | Key Technique | Original Resources | Primary Constraint Tension |
|---|---|---|---|---|---|
| 37 | Momentum Factor Premium | 10-day/50-day MA crossover generates 12% annual excess return | Moving average crossover, Fama-French regression | Tick-level data, S&P 500 (20 years), Bloomberg terminal | Daily OHLCV only, 10-year window, no Bloomberg (use yfinance), survivorship bias |
| 38 | Pairs Trading Mean Reversion | Cointegrated equity pairs yield 8% annual Sharpe 1.5 | Engle-Granger cointegration, Kalman filter | Intraday data, 200 pairs, $0.005/share commission model | Daily data, budget to test 50 pairs, commission model is $0.01/share |
| 39 | Volatility Risk Premium | Selling VIX puts captures 4% monthly premium | Options pricing, delta hedging | Options chain data (CBOE), VIX futures, real-time Greeks | No options data subscription, must use delayed data, no real-time Greeks |
| 40 | Earnings Momentum | Post-earnings drift persists for 60 days | Event study, CAR calculation | Earnings calendar (10 years), intraday returns around announcements | Only daily returns, 5-year earnings calendar (free source), must use wider event window |
| 41 | Crypto Market Microstructure | Bitcoin bid-ask spread predicts 1h returns | Order book analysis, microstructure model | L2 order book data (Binance), 1-second resolution, 6 months | No L2 data, only L1 (best bid/ask) from free API, 3-month window |
| 42 | Factor Timing with Macro Signals | Yield curve slope predicts value/growth rotation | Multi-factor model with macro overlay | Factor returns (AQR), yield curve data (FRED), 30 years | AQR data has 3-month publication lag, 20-year window from FRED, must handle shorter overlap |

### Cluster H: Risk and Valuation Replication (4 papers)

| # | Paper Title | Claim | Key Technique | Original Resources | Primary Constraint Tension |
|---|---|---|---|---|---|
| 43 | VaR Model Backtesting | Historical VaR at 99% underestimates tail risk by 40% | Historical simulation, 10K scenarios | 20 years of daily portfolio returns, Monte Carlo (100K paths) | 10-year data window, compute budget for 10K Monte Carlo paths, must justify reduced sample |
| 44 | Credit Risk Transition Matrix | BBB-to-default probability is 0.3% annual (S&P estimate) | Cohort analysis of rating transitions | S&P rating database (proprietary, 30 years), 5K issuers | No S&P database, must use Moody's public reports (summary statistics only), reconstruct from aggregated data |
| 45 | Real Estate Cap Rate Model | Cap rate spread over 10Y treasury predicts REIT returns | Regression model with macro factors | NCREIF property index, 10Y treasury (FRED), REIT returns (CRSP) | NCREIF is proprietary, must use publicly available REIT index as proxy, shorter time series |
| 46 | Portfolio Optimization | Black-Litterman outperforms mean-variance by 200bps | Black-Litterman with investor views | Covariance matrix (60 assets, 10 years daily), equilibrium returns | Only 30 assets available (data cost), weekly instead of daily data, must address estimation error |

### Cluster I: Behavioral Finance and Market Anomalies (4 papers)

| # | Paper Title | Claim | Key Technique | Original Resources | Primary Constraint Tension |
|---|---|---|---|---|---|
| 47 | Disposition Effect in Retail Trading | Retail traders sell winners 1.5x faster than losers | Trade-level analysis of brokerage accounts | Proprietary brokerage dataset (100K accounts, 5 years) | No brokerage data, must use public datasets (Robinhood 2021 leak or academic dataset) |
| 48 | Sentiment and Returns | Twitter sentiment predicts next-day S&P 500 direction | NLP sentiment analysis, Granger causality | Twitter firehose (1M tweets/day), FinBERT, 3 years | No Twitter firehose (API deprecated), must use Reddit or news headlines, smaller sample |
| 49 | January Effect Persistence | Small-cap excess returns in January have declined since 1990 | Calendar anomaly study, size-sorted portfolios | CRSP daily returns (60 years), size quintile breakpoints | Only 20 years of free data (Yahoo), must construct size portfolios from available universe |
| 50 | IPO Underpricing | Average first-day IPO return is 18% with high variance | Event study of IPO first-day returns | SEC EDGAR filings, IPO database (30 years, 5K IPOs) | Free IPO data covers 10 years only (1.5K IPOs), missing some small IPOs, survivorship concern |

---

## Difficulty Calibration

Each scenario gets tagged with a difficulty. The Oracle uses this to adjust how severe the constraints are, but the base template defines the core tension.

| Difficulty | Constraint Profile | Target Reward Range |
|---|---|---|
| Easy | 1-2 conflicts, clear substitutions exist, budget is 80% of needed | 6.0-8.5 |
| Medium | 3-4 conflicts, substitutions require tradeoffs, budget is 50-70% of needed | 3.5-6.5 |
| Hard | 5+ conflicts, substitutions are risky, budget is 30-50% of needed, time pressure | 1.5-4.5 |

Distribution across 50 scenarios:
- Easy: 15 (30%)
- Medium: 20 (40%)
- Hard: 15 (30%)

During training, use curriculum learning: start with easy, shift to medium by iteration 5, introduce hard by iteration 10.

---

## What Each Scenario Template Must Define

The Oracle generates the full scenario, but your template gives it guardrails. Each template is a compact JSON/Python dict:

```python
SCENARIO_TEMPLATES = {
    "ml_resnet_depth": {
        "id": 1,
        "domain": "computational_ml",
        "difficulty_range": ["easy", "medium", "hard"],
        "paper_seed": {
            "title": "ResNet Depth Scaling on ImageNet",
            "claim": "Deeper networks improve accuracy up to 152 layers",
            "technique": "ResNet with skip connections",
            "original_compute": "8xV100, 90 epochs, full ImageNet",
            "original_sample_size": 1281167,  # ImageNet train size
            "original_duration": "72 hours",
            "statistical_test": "top-1/top-5 accuracy, t-test across 3 seeds",
            "required_controls": [
                "baseline_shallow_model",
                "learning_rate_schedule",
                "data_augmentation_pipeline"
            ],
        },
        "constraint_seed": {
            "equipment_pool": ["gpu_h100", "gpu_a100_40gb", "gpu_v100", "cpu_cluster"],
            "data_pool": ["imagenet_full", "imagenet_100", "imagenet_10pct", "cifar100_proxy"],
            "typical_budget_range": [500, 5000],  # USD compute cost
            "time_range_hours": [8, 72],
            "common_bottlenecks": [
                "gpu_memory_for_batch_size",
                "dataset_download_time",
                "library_version_incompatibility",
                "checkpoint_storage"
            ],
            "valid_substitutions": [
                {"original": "imagenet_full", "substitute": "imagenet_100", "validity": "acceptable_with_caveats", "caveat": "must acknowledge reduced class diversity"},
                {"original": "8xV100", "substitute": "1xH100", "validity": "equivalent", "caveat": "adjust batch size, use gradient accumulation"},
                {"original": "90_epochs", "substitute": "30_epochs", "validity": "inferior_but_usable", "caveat": "may not reach full convergence, report learning curve"},
            ],
        },
        "scoring_hints": {
            "critical_controls": ["baseline_shallow_model", "learning_rate_schedule"],
            "flexible_controls": ["data_augmentation_pipeline"],
            "min_sample_fraction": 0.1,  # at least 10% of original data
            "power_notes": "accuracy differences < 0.5% require large n to detect",
        },
    },
    # ... 49 more templates
}
```

You do NOT write all 50 as fully fleshed-out dicts before the hackathon. You write 5-6 detailed templates (2 per domain) and let the Oracle interpolate the rest. The template gives the Oracle enough domain knowledge to generate a consistent scenario.

---

## Training Plan for 3 Hours on H100

### The Math

**Model:** Qwen2.5-7B-Instruct or LLaMA-3-8B-Instruct with LoRA (rank 16)
**Method:** GRPO via TRL or Unsloth
**GPU:** 1xH100 80GB

**Time budget breakdown:**

| Phase | Time | What Happens |
|---|---|---|
| Setup and warmup | 15 min | Load model, verify env loop, run 2 test episodes |
| Pre-generate scenarios | 15 min | Call Oracle World Architect for all seeds, cache to disk |
| Training | 2 hr 15 min | GRPO iterations |
| Final evaluation | 15 min | Run eval episodes, generate reward curve |

### Pre-Generation Phase (Critical)

Before training starts, pre-generate and cache all scenarios you will use. This removes the Oracle API bottleneck from the training loop entirely.

```
50 scenario templates × 3 difficulty variants = 150 unique scenarios
Oracle World Architect call: ~4 sec each
Total: 150 × 4 = 600 sec = 10 minutes

Cache all 150 to disk as JSON.
```

During training, `reset()` loads from cache. Zero API latency.

### The Bottleneck Shift

With cached scenarios, the per-episode bottleneck becomes the **Lab Manager LLM calls** (one per round). Two options:

**Option A: LLM Lab Manager (richer but slower)**
- 6 rounds × ~2.5 sec per LM call = 15 sec per episode for LM
- Plus Adjudicator calls: 6 × 2.5 sec = 15 sec
- Total API time per episode: ~30 sec
- GPU time per episode (Scientist inference): ~2 sec
- Wall time per episode: ~32 sec

**Option B: Rule-based Lab Manager for training, LLM for demo (faster)**
- 6 rounds × 0 sec API = 0 sec for LM
- Adjudicator: can also be made deterministic for training
- Total API time per episode: 0 sec
- GPU time per episode: ~2 sec + ~1 sec overhead
- Wall time per episode: ~3 sec

**I strongly recommend Option B for training.** Use the rule-based Lab Manager and deterministic Adjudicator during RL training for speed, then switch to LLM Lab Manager and Oracle Adjudicator for demo and evaluation. The Scientist does not know the difference, it still sees the same observation schema.

### Episodes per Hour with Option B

| Parallel Rollouts | Episode Time | Episodes/Hour |
|---|---|---|
| 1 | ~3 sec | ~1,200 |
| 4 (batch) | ~3 sec (batched inference) | ~4,800 |
| 8 (batch) | ~3.5 sec | ~8,200 |

With batched inference (8 parallel rollouts), you get roughly **8,000 episodes per hour**.

### GRPO Training Schedule

GRPO collects a batch of rollouts, computes advantages, and updates the model. Here is the schedule:

```
GRPO config:
  rollout_batch_size: 32 episodes per update
  num_iterations: 40
  total_episodes: 32 × 40 = 1,280
  
  Per iteration:
    Rollout collection (32 episodes, 8 parallel): ~12 sec
    Advantage computation: ~2 sec
    Gradient update (LoRA rank 16, 7B model): ~45 sec
    Logging and checkpoint: ~5 sec
    Total per iteration: ~64 sec ≈ ~1 min

  40 iterations × 1 min = 40 minutes
```

Wait. That is only 40 minutes. You have 2 hours 15 minutes of training time. So you can do much more:

```
Revised GRPO config:
  rollout_batch_size: 64 episodes per update
  num_iterations: 80
  total_episodes: 64 × 80 = 5,120
  
  Per iteration:
    Rollout collection (64 episodes, 8 parallel): ~24 sec
    Advantage computation: ~3 sec
    Gradient update: ~55 sec
    Logging: ~5 sec
    Total per iteration: ~87 sec ≈ ~1.5 min

  80 iterations × 1.5 min = 120 min = 2 hours
```

**Final training plan: 5,120 episodes across 80 GRPO iterations in ~2 hours.**

### Curriculum Schedule

| Iterations | Difficulty Mix | Domains |
|---|---|---|
| 1-20 | 80% easy, 20% medium | ML/DL only (most constrained, clearest signal) |
| 21-40 | 40% easy, 50% medium, 10% hard | ML/DL + Biology |
| 41-60 | 10% easy, 50% medium, 40% hard | All three domains |
| 61-80 | 0% easy, 30% medium, 70% hard | All three domains, hardest scenarios |

### Scenario Sampling During Training

With 150 cached scenarios and 5,120 episodes, each scenario gets used ~34 times on average. But you seed the randomness, so:

- Iteration 1-20: sample from ML easy/medium scenarios (templates 1-20, easy+medium variants = ~40 scenarios)
- Iteration 21-40: add Biology (templates 21-36 = ~32 more scenarios)
- Iteration 41-80: add Finance (templates 37-50 = ~28 more scenarios), shift to harder variants

The Scientist sees enough variety to generalize while getting repeated exposure to learn each domain.

---

## Evaluation Plan (Final 15 Minutes)

### Held-Out Evaluation Set

Reserve 10 scenarios per domain (30 total) that are NEVER used during training. Different seeds, same templates but with constraint variations the Scientist has not seen.

### Evaluation Runs

```
30 held-out scenarios × 1 run each = 30 episodes
Wall time: 30 × 3 sec = 90 sec (with rule-based LM)

Then run 5 showcase episodes with LLM Lab Manager + Oracle:
5 × 50 sec = 250 sec ≈ 4 min

Total eval time: ~6 minutes (well within 15 min budget)
```

### Metrics to Report

| Metric | Untrained (Baseline) | Trained (Post-GRPO) |
|---|---|---|
| Mean total reward | Measure in Phase 2 | Measure here |
| Mean rigor score | | |
| Mean feasibility score | | |
| Mean fidelity score | | |
| Rounds to agreement | | |
| Invalid action rate | | |
| Contradiction rate | | |
| Agreement rate (vs timeout) | | |

### The Reward Curve

Plot every 5 iterations:
- X axis: GRPO iteration (0 to 80)
- Y axis: mean reward over last batch
- Include error bars (std across batch)
- Overlay the difficulty curriculum as background color

This is the single most important artifact for judges. It must show a clear upward trend.

---

## What You Actually Build Before Training

### Day-of Priority Order

1. **`models.py`** (30 min)
   All Pydantic models from the Oracle guide. These are your contract.

2. **`oracle.py`** with World Architect mode only (45 min)
   Get scenario generation working. Test with 3 seeds. Cache results.

3. **`replicalab_env.py`** with rule-based Lab Manager (1 hour)
   The fast training loop. No LLM Lab Manager. Deterministic adjudicator.
   Must pass: reset returns observation, step returns observation + reward, episode terminates.

4. **`scoring/reward.py`** deterministic reward computation (30 min)
   The arithmetic layer. Takes protocol + hidden spec, outputs scores.

5. **6 detailed scenario templates** (30 min)
   2 per domain. These seed the Oracle and serve as rule-based fallbacks.

6. **GRPO training script** (1 hour)
   Connect TRL/Unsloth to the env. Verify one iteration works.

7. **Pre-generate 150 scenarios** (15 min)
   Run the Oracle, cache everything.

8. **Start training** (2 hours, runs while you build the demo)

9. **`lab_manager_agent.py`** LLM version (30 min, while training runs)
   Only used for demo. Not needed for training.

10. **Oracle Adjudicator + Post-Mortem** (30 min, while training runs)
    Only used for demo and eval showcase episodes.

### What Can Run in Parallel

While the H100 is training (2 hours), your team builds:
- LLM Lab Manager (Person 2)
- Oracle Adjudicator + Post-Mortem (Person 2)
- React UI (Person 4)
- Demo script and YouTube recording prep (Person 4)
- FastAPI + WebSocket server (Person 3)
- HF Space Dockerfile (Person 3)

The H100 only needs ~30% utilization for GRPO training with LoRA. The remaining GPU capacity can run the Scientist inference for evaluation episodes simultaneously if you architect the training script to do periodic eval checkpoints.

---

## Summary

| Item | Number |
|---|---|
| Total scenario templates | 50 |
| ML/DL | 20 |
| Biology | 16 |
| Finance | 14 |
| Cached scenario variants (with difficulty) | 150 |
| Training episodes | 5,120 |
| GRPO iterations | 80 |
| Training wall time | ~2 hours |
| Eval episodes | 30 (fast) + 5 (showcase) |
| Total H100 time | ~2.5 hours (within 3-hour budget) |
| Scientist model | 7B-8B with LoRA rank 16 |
| Lab Manager (training) | Rule-based (fast) |
| Lab Manager (demo) | LLM (rich) |
| Oracle calls during training | 0 (all cached) |
| Oracle calls during demo | Full (all 4 modes live) |
