Place public dataset images here (no synthetic generation in this project).

Suggested layout:
  normal/          clean / acceptable photos (used to fit IsolationForest)
  blur/            e.g. CERTH blurred images
  defect/          e.g. MVTec AD anomalous images
  underexposure/
  overexposure/
  noise/           optional (SIDD); otherwise CV noise estimate still runs at inference

Sources (document license in project README):
- CERTH Image Blur Dataset
- MVTec AD (non-commercial research/evaluation)
- General photo subset for exposure labeling via brightness thresholds
