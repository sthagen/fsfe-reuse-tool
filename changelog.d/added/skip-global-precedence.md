- Added `--skip-global` and `--skip-precedence` to `reuse annotate`. These
  options allow skipping the annotation of files when they are already covered
  by REUSE.toml (dependent on precedence of the annotation in the case of
  `--skip-precedence`). (#1303)
