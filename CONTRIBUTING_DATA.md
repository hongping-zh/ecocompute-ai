# Community Benchmark Data Contribution Protocol

Protocol version: v1.0

EcoCompute welcomes community benchmark data, but contributed results must be labeled and reviewed carefully so that the main leaderboard remains comparable.

Submissions are evaluated against the protocol version in effect at the time of submission. Future protocol updates will not automatically invalidate accepted historical submissions, but maintainers may relabel older rows if comparability changes.

## Contribution Tracks

### Track A: Main Benchmark Candidate

Use this track only when your run follows the standard EcoCompute methodology closely enough to be compared with the main leaderboard.

Required conditions:

- NVIDIA GPU with NVML power telemetry available.
- End-to-end generation energy measured in `J/1k generated tokens`.
- NVML power sampling at 10 Hz unless otherwise justified.
- 3 warmup runs discarded before measurement.
- 10 measured repetitions per configuration.
- Fixed prompt, fixed generation length, and deterministic generation settings where possible.
- Report mean, standard deviation, and coefficient of variation for energy, throughput, and power.
- Energy CV should be below 3% for inclusion in the main benchmark table.
- Include FP16 baseline for every submitted model, GPU, batch size, and generation length.

Non-NVIDIA GPUs are not eligible for Track A in v1.0 because the main methodology is based on NVML telemetry. They may be submitted as Track B supplementary data if a comparable power measurement interface is available and documented.

### Track B: Supplementary Case Study

Use this track for valuable measurements that do not fully match the main protocol.

Examples:

- Different sampling rate, such as 100 Hz.
- Phase-separated prefill/decode measurements.
- Nonstandard generation length.
- Backend diagnostic or compatibility experiments.
- Energy CV above the main benchmark threshold.
- Missing FP16 baseline.
- Non-NVIDIA GPUs measured with documented alternatives such as `rocm-smi`, Apple power telemetry, wall-power meters, or external power sensors.

Supplementary results may still be accepted, archived, and linked from update pages, but they are not automatically counted in the main benchmark configuration total.

## Standard Measurement Protocol

### Hardware Metadata

Report:

- GPU name.
- GPU architecture, if known.
- VRAM size.
- TDP or power limit used during measurement.
- Driver version.
- CUDA version.
- Operating system.
- CPU model, if available.
- Number of GPUs visible and the GPU index used.

### Software Metadata

Report:

- Python version.
- PyTorch version.
- Transformers version.
- bitsandbytes version, if used.
- CUDA toolkit or runtime version.
- Model source and exact model identifier.
- Any quantization backend and settings.

Contributions using quantization backends other than bitsandbytes are welcome. Examples include GPTQ, AWQ, GGUF/llama.cpp, FP8 via Transformer Engine, torchao, vendor runtimes, or custom kernels. Specify the backend name, version, and relevant settings in `quantization_backend`, and use `N/A` for `bitsandbytes_version` when bitsandbytes is not used.

### Runtime Settings

Report:

- Model identifier.
- Precision or quantization mode: `fp16`, `nf4`, `int8`, `fp8`, or another explicit label.
- Batch size.
- Prompt length in tokens.
- Generated tokens.
- Number of warmup runs.
- Number of measured runs.
- Sampling rate in Hz.
- Decoding parameters, including `do_sample`, `temperature`, `top_p`, and `max_new_tokens`.

## Result CSV Schema

Community result CSV files should use the schema in `data/community_submission_template.csv`.

Keep all template columns in the CSV so submissions remain machine-readable. Some values may be `N/A` or empty when they do not apply. Required fields are needed for any interpretable submission; optional fields improve reproducibility but should not block a useful supplementary contribution.

Required fields:

- `submission_id`
- `track`
- `submitter_name`
- `date_utc`
- `gpu_name`
- `gpu_vram_gb`
- `driver_version`
- `cuda_version`
- `python_version`
- `pytorch_version`
- `transformers_version`
- `model_id`
- `precision`
- `quantization_backend`
- `batch_size`
- `prompt_tokens`
- `generated_tokens`
- `warmup_runs`
- `measured_runs`
- `sampling_rate_hz`
- `energy_j_per_1k_tok_mean`
- `energy_j_per_1k_tok_std`
- `energy_cv_percent`
- `throughput_tok_s_mean`
- `avg_power_w_mean`
- `notes`

Optional or `N/A` fields:

- `submitter_contact`
- `gpu_architecture`
- `gpu_tdp_w`
- `bitsandbytes_version`
- `model_parameters_b`
- `throughput_tok_s_std`
- `avg_power_w_std`
- `peak_power_w_mean`
- `raw_archive_path`

For Track A, `raw_archive_path` is strongly recommended. For Track B, it may be omitted if the PR includes enough summary data and metadata to interpret the result.

## Raw Data Requirements

Each submission should include a compressed archive when possible.

Recommended archive contents:

- Per-run result CSV or JSON.
- Power trace files with timestamps and watts.
- Environment capture such as `pip freeze` or `conda env export`.
- Benchmark command or script used.
- Short README explaining how to reproduce the run.

Large archives may be uploaded through GitHub Releases, Hugging Face Datasets, Zenodo, or another persistent location. Put the URL in `raw_archive_path`.

## Quality Rules

A result can be considered for the main benchmark only if:

- The FP16 baseline is present for the same model, GPU, batch size, prompt length, and generation length.
- Energy CV is below 3%.
- Measured runs are at least 10.
- Warmup runs are at least 3.
- Sampling rate and integration method are documented.
- No other heavy GPU process was running during measurement.
- The result includes enough metadata to reproduce the run.

Results that fail one or more rules should be submitted as supplementary data.

## Review Labels

Maintainers may classify incoming data as:

- `main-benchmark-candidate`: comparable with the main leaderboard after review.
- `supplementary-case-study`: useful but not directly comparable.
- `needs-reproduction`: promising but missing metadata or raw traces.
- `rejected-for-now`: not enough information to interpret reliably.

## Submission Workflow

1. Copy `data/community_submission_template.csv` and fill one row per measured configuration.
2. Copy `data/community_metadata_template.json` and fill the environment and protocol details.
3. Add raw traces or provide a persistent archive URL.
4. Open a pull request.
5. In the PR description, state whether the submission is Track A or Track B.
6. Include any known caveats, especially CV above 3%, nonstandard sampling rate, or backend-specific behavior.

## Interpretation Policy

EcoCompute treats energy measurements as hardware-software-stack-specific observations. Do not claim that a precision format is universally better or worse from one GPU/backend result. Main benchmark entries support cross-configuration comparisons only when the protocol is sufficiently matched. Supplementary case studies should be interpreted as diagnostic evidence or external validity checks, not direct leaderboard entries.
