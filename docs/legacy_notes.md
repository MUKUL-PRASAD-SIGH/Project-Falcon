# Legacy Compatibility Notes

This project keeps its prior demo and offline behavior intact while correcting
the current runnable path.

- `VITE_API_BASE` is still accepted by the frontend as a legacy alias. New
  configuration should use `VITE_API_BASE_URL`.
- The prior hard-coded QuickML endpoint key was removed from source because
  credentials must be supplied through `QUICKML_RISK_KEY`. The local
  precomputed-risk fallback remains unchanged when no key is configured.
- Earlier README commands referenced data-validation and model scripts that do
  not exist in this repository. The documented current workflow is the
  generated synthetic data plus `python ml/run_pipeline.py`.
- Offline demo inputs and ML outputs were previously ignored despite being
  required for the local experience. They are now explicitly versionable;
  caches, environments, secrets, and unrelated generated files stay ignored.
