# Data and evaluation

This project uses **public datasets** under `sample_images/` (plus small demo folders). It does **not** generate a full synthetic degradation pipeline for training. Sampling is **capped** so evaluation stays fast on CPU.

---

## 1. Where data lives

```
sample_images/
  CERTH_ImageBlurDataset/     # blur + undistorted (CERTH)
  SIDD_Small_sRGB_Only/       # noisy / GT pairs
  koniq10k_512x384/           # general photos (exposure via brightness)
  acceptable/ blur/ defect/   # small demo sets for manual UI tests
  noise/ underexposure/ overexposure/
backend/data/
  labels.csv                  # unified index built by sampling scripts
  raw/<label>/                # optional alternate layout for build_dataset.py
backend/model/
  anomaly_detector.joblib
  eval_report.json
```

Paths inside `labels.csv` are relative to `backend/` (for example `../sample_images/CERTH_ImageBlurDataset/...`).

---

## 2. Label sources (`sample_from_public.py`)

| Source | Label | Cap (seed=42) |
|--------|-------|---------------|
| CERTH `TrainingSet/Undistorted` | `normal` | 40 |
| CERTH Naturally + Artificially Blurred | `blur` | 30 |
| SIDD `NOISY_SRGB_*.PNG` | `noise` | 20 |
| SIDD `GT_SRGB_*.PNG` | `normal` | 10 |
| koniq mid brightness | `normal` | 40 |
| koniq dark (brightness &lt; under-low threshold) | `underexposure` | 15 |
| koniq bright (brightness &gt; over-low threshold) | `overexposure` | 15 |
| Small demo folders | matching names | all files present |

Koniq exposure labels reuse the same brightness thresholds as inference — convenient, but **circular** for exposure-only claims (call this out in write-ups).

Alternate path: put images in `backend/data/raw/<label>/` and run `python -m app.training.build_dataset`.

---

## 3. Rebuild labels, fit, evaluate

From an activated project `.venv`, with `backend` as cwd:

```powershell
cd backend
$env:PYTHONPATH = "."

python -m app.training.sample_from_public
python -m app.training.fit_anomaly_detector
python -m app.training.evaluate_model
```

| Script | Output |
|--------|--------|
| `sample_from_public` | `data/labels.csv` (+ per-image CV features) |
| `fit_anomaly_detector` | `model/anomaly_detector.joblib` (normals only) |
| `evaluate_model` | `model/eval_report.json` |

Restart the API after fitting so it reloads the new joblib file.

---

## 4. Reading `eval_report.json`

Evaluation treats every non-`normal`/`clean` row as **anomaly (positive)** and compares IsolationForest `predict` (+ ROC on inverted decision scores).

Typical fields:

| Field | Meaning |
|-------|---------|
| `n_evaluated` | Rows successfully scored |
| `roc_auc` | Ranking quality of anomaly scores |
| `precision` / `recall` / `f1` | At IF’s default decision threshold |
| `confusion_matrix` | `[[TN, FP], [FN, TP]]` for normal vs anomaly |
| `failure_cases_sample` | Misclassified examples |
| `limitations` | Short notes baked into the report |

**Important:** These metrics evaluate the **embedding anomaly head**, not the full hybrid UI score (CV rules still catch blur/exposure at inference even when IF recall is modest).

Example snapshot after a capped CERTH/SIDD/koniq run (numbers change if you re-sample):

- ~205 images evaluated  
- ROC-AUC around **0.64**  
- IF default threshold: high precision, **low recall** (conservative `predict`)

Always cite the file checked into `backend/model/eval_report.json` (or regenerate and refresh the file) for submission numbers.

---

## 5. Known limitations

1. **Capped subsets** — not full CERTH / koniq / SIDD benchmarks.
2. **Exposure circularity** — koniq under/over labels use brightness thresholds shared with CV rules.
3. **Domain shift** — normals mix CERTH / SIDD GT / koniq / demo textures; photographic blur may not look “anomalous” to ImageNet embeddings.
4. **IF vs hybrid** — low IF recall does not mean the product ignores blur; Laplacian rules still fire.
5. **Demo folders** — small synthetic-looking images may remain under `sample_images/` for UI demos; prefer public sets for serious eval claims.
6. **Licenses** — respect CERTH, SIDD, koniq, and (if used) MVTec AD non-commercial research terms; cite sources in your submission.

---

## 6. Sample images for submission demos

Use folders under `sample_images/` that illustrate:

- Acceptable / sharp  
- Blur  
- Underexposure / overexposure  
- Noise  
- Defect / severe degradation  

Upload them through the UI or `POST /analyze` when preparing screenshots for the assessment.

Next: [Setup](setup.md) · [ML pipeline](ml-pipeline.md)
