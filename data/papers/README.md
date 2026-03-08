# Paper Corpus

This folder contains a 50-paper local corpus built from the scenario list in
`ReplicaLab_50_Scenarios_Training_Plan.md`.

Layout:

- `data/papers/<field>/<paper-name>/paper.pdf`
- `data/papers/<field>/<paper-name>/metadata.json`
- `data/papers/manifest.json`

Fields used:

- `computational_ml_dl`
- `wet_lab_biology`
- `behavioral_cognitive`
- `environmental_ecological`
- `quantitative_finance`

Notes:

- The folder name uses the scenario title slug from the training plan.
- `metadata.json` records the source URL, chosen paper title, match type, and
  file hash.
- When an exact paper title from the training plan was synthetic or not
  practically retrievable as an open PDF, an alternative open-access paper was
  used and marked as `alternative` in metadata.
