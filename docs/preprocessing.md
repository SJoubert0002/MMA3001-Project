# Sensor data preprocessing

## Purpose and engineering context

The preprocessing stage in `pre-Processing.ipynb` prepares building environmental-sensor measurements and occupancy events for investigation. It preserves the supplied raw inputs, creates structured derived datasets, and records validation, missingness, transformation, and read-benchmark evidence.

The project brief expects the project to define an engineering problem and its intended use, justify computational decisions, verify implementation, compare credible alternatives, interpret results in context, and state limitations. This document covers preprocessing only. The active occupancy-investigation cells later in the notebook examine semester phases, week-to-week changes, and within-day peaks descriptively. Preprocessing itself does not establish sensor calibration or infer causality; predictive or causal claims would require separate methods and validation.

## Reproducible execution

1. Use the repository's Python environment with Python 3.12 and pandas available.
2. Put complete environmental and occupancy CSV exports in `data/`; nested subdirectories are searched.
3. Keep `Sensor ID and Locations - ENV.csv` in `data/` or at the repository root.
4. Open `pre-Processing.ipynb` and run the pipeline cell with the repository root as the working directory.
5. Review the output messages and the validation, change, missingness, and benchmark reports under `derived/`.

The raw `data/` directory is ignored by Git. It is not committed with the workflow; provide the authorized input exports locally when reproducing a run. The notebook can fall back to legacy raw CSVs at the repository root if no compatible file is found in `data/`.

## Input contract

### Environmental sensor export

The input is a CSV requiring these fields:

| Field | Meaning and use | Validation |
|---|---|---|
| `id` | Source record identifier; copied to `source_record_id`. | Nonblank and unique across the input. |
| `sensorid` | Source sensor identifier. | Numeric and equal to the configured project sensor ID. |
| `devicetype` | Sensor family. | Must equal the currently validated `env` value. |
| `jsondata` | JSON array containing variable metadata and measurement values. | Must match the supported structure described below. |
| `status` | Source processing status. | Must equal the currently validated `Processed` value. |
| `processing_errors` | Source error field. | Must equal the currently validated `NULL` token. |
| `createdate` | Source record creation time. | Must parse as a timestamp. Preserved as supplied. |
| `processdate` | Source processing time. | Must parse as a timestamp. Removed from the reduced table only if every parsed value equals `createdate`. |

Additional CSV columns are ignored. For each record, `jsondata` must decode to a list of variable entries. Each entry must have a variable object with a unique numeric ID. Variable metadata must be consistent for a given ID across all records. `values` must be a list with zero or one point. Present points must contain a valid Unix-seconds `time`; all measurement points in one record must share the same timestamp. A `value` may be null or finite numeric. Invalid JSON, malformed points, duplicate variables, multiple points, inconsistent timestamps, nonnumeric measurements, and non-finite measurements stop the run with an error.

Each measurement's descriptive name and unit are copied into the generated schema. Values are not unit-converted. Measurement timestamps are converted from Unix seconds to UTC; record timestamps remain separately available. Equality between `createdate` and `processdate` does not mean either is equal to the measurement timestamp.

### Occupancy export

The input is a CSV requiring:

| Field | Meaning and use | Validation/handling |
|---|---|---|
| `id` | Source event identifier; retained in the stream. | Preserved as a string. |
| `deviceid` | Occupancy device identifier. | Must equal the currently validated project device ID. |
| `floorspaceid` | Space partition key. | Must be present; determines the output filename and stream partition. |
| `occupancystatus` | Categorical occupancy state. | Omitted from numeric time-series outputs. |
| `headcount` | Numeric people count. | Must be a nonnegative integer or missing. Missing values become `NaN`; rows are retained. |
| `collecteddate` | Timestamp of the occupancy observation. | Must parse; retained in the stream. |
| `occupancystatuschangedate` | State-change timestamp. | Must parse; audited before being omitted from streams. |
| `previousoccupancystatus` | Previous categorical state. | `Unknown` and missing counts are reported; the field is omitted from streams. |

Additional CSV columns are ignored. No physical-capacity limit is imposed on headcounts by this stage.

### Input discovery and missing tokens

Environmental and occupancy inputs are selected independently. A CSV is a candidate when it contains the identifying signature columns for that dataset; a candidate missing any required field is treated as an unsupported input and causes a clear error. Among complete candidates, the file with the newest filesystem modification time is selected. Files are not concatenated: the selected export is assumed to be a complete replacement snapshot, not an incremental addition. A tie for the newest modification time is an error requiring the user to resolve the ambiguity.

File modification time is not proof of export recency or completeness. Confirm that the newest file is the intended full export. Changes to sensor/device identifiers, status constants, required columns, timestamp representation, or the supported JSON contract require review of the checks before accepting the data.

Missing text tokens are blank, `nan`, `null`, and `none`, after trimming and case folding. Environmental JSON `null`, an empty values list, or an absent variable in a record produces a numeric `NaN`; it does not remove the raw JSON or its source row. Unknown occupancy history is counted but excluded with the history column. Missing rows are not dropped and no value is imputed.

## Processing sequence and rationale

1. **Discover sources and validate schemas.** The pipeline inspects headers before processing and uses only required columns. It reads CSV data in chunks as strings to preserve identifiers and make missing-token handling explicit.
2. **Validate the environmental lookup.** The lookup must contain the expected environmental sensor and configured ID. The known occupancy location mapping is not used because its floorspace IDs have been identified as invalid.
3. **Parse and expand environmental JSON.** The pipeline first gathers stable variable metadata, then writes one wide row for each source event. A feature column is generated from each variable ID and normalized variable name. The raw JSON remains unchanged.
4. **Represent missing measurements as `NaN`.** Empty value lists, explicit JSON nulls, and variables absent from a record become non-numeric missing values. This prevents missing measurements from being mistaken for zero while preserving row alignment.
5. **Create the reduced environmental table.** The full table retains traceability and source fields. The reduced table excludes `sensor_id` and `devicetype` only after they have been validated as constant. `processdate` is excluded only when parsed equality with `createdate` holds for every row. The measurement timestamp is retained independently.
6. **Partition occupancy observations.** All source rows are written to one stream per floorspace, retaining `id`, `floorspaceid`, `headcount`, and `collecteddate`. Device identity and categorical state/history are omitted from these numeric series after validation/counting.
7. **Audit before exclusion.** The change-date pattern audit is computed using occupancy count, collected time, and state-change time before that state-change time is dropped from the analytical stream.
8. **Validate and report.** Output schemas, record IDs, parsed measurement values, timestamps, row totals, and stream partitions are checked. Transformation, missingness, validation, and benchmark results are written to CSV reports.

The pipeline does not perform location joins, cross-sensor time alignment, timezone harmonization of all source dates, resampling, aggregation, interpolation, outlier removal, capacity checks, or target selection. These operations are intentionally deferred until the investigation question and required temporal/spatial resolution are defined.

## Outputs and interpretation

| Output | Purpose |
|---|---|
| `derived/environmental_measurements/environmental_measurements_wide.csv` | Full parsed environmental table: source record ID, sensor/device fields, source record timestamps, UTC measurement timestamp, and all measurement columns. |
| `derived/environmental_measurements/environmental_measurements_wide_reduced.csv` | Environmental analysis candidate with verified redundant fields excluded. It is not yet joined to locations or aligned to occupancy data. |
| `derived/environmental_measurements/environmental_measurements_wide_schema.csv` | Mapping of variable ID, name, unit, source, structure, and generated feature name. Consult this to interpret `var_<id>_<name>` columns. |
| `derived/environmental_measurements/environmental_measurements_wide_validation.csv` | Validation outcomes specific to the environmental outputs. |
| `derived/environmental_measurements/environmental_measurements_wide_benchmark.csv` | Full/reduced-column read benchmarks for the two wide environmental outputs. |
| `derived/occupancy_streams_by_floorspace/<floorspaceid>.csv` | One numeric occupancy time series per floorspace. |
| `derived/occupancy_streams_by_floorspace/stream_row_counts.csv` | Source/output row count by floorspace. |
| `derived/occupancy_streams_by_floorspace/occupancystatuschangedate_audit.csv` | Timestamp pattern counts by floorspace, calculated before dropping the state-change timestamp. |
| `derived/preprocessing/preprocessing_validation.csv` | Overall source selection and pipeline validation results. `PASS` indicates the stated check held; `INFO` records an observation, not a failed check. |
| `derived/preprocessing/preprocessing_changes.csv` | Transformation name, input/output paths, affected rows, before/after counts, and rationale. |
| `derived/preprocessing/preprocessing_missing_data_report.csv` | Missing environmental measurements and occupancy unknown/missing counts, with treatment. |
| `derived/preprocessing/preprocessing_benchmark.csv` | Repeated full/reduced CSV read timings and chunk memory measurements. |
| `derived/preprocessing/preprocessing_raw_vs_processed_benchmark.csv` | Raw-versus-processed read comparison for environmental and occupancy data. |

Raw files are treated as read-only inputs. Output rows are retained unless a validation error stops the run. CSV floating-point missing values are written as `NaN`.

## Validation and testing

The cell runs focused tests that verify:

- blank/null/nan numeric tokens become `NaN`, while valid numbers remain numeric;
- nonnumeric headcounts are rejected;
- feature names normalize predictably; and
- the newest compatible export is selected when multiple versions are present.

The data checks additionally verify environmental source IDs are unique and nonblank; sensor/status constants match the current source contract; environmental JSON parses and feature metadata is stable; output row counts and IDs match the source; measurements are numeric or missing; occupancy timestamps parse; headcounts are valid; and per-space stream row totals equal source totals. The location lookup, timestamp relationships, and change-date patterns are separately reported. A successful run establishes these code-level conditions for the selected files; it does not prove that the original measurements are calibrated, complete, semantically correct, or physically accurate.

The tests are embedded in the notebook pipeline cell so they run before output generation. They are focused regression tests rather than an exhaustive independent test suite; the source checks and audits provide additional dataset-specific evidence.

## Performance benchmark method

The read benchmark runs full-column and selected-column reads for three repetitions, alternating which read configuration runs first. It processes CSV files in chunks and records row count, column count, median/minimum/maximum elapsed time, repeat count, and the largest individual chunk's pandas DataFrame memory estimate. Before reporting, it verifies row counts are stable across repeats and match between full and reduced reads. The raw-versus-processed report compares the full raw table to the derived dataset/combined floorspace streams and requires matching row totals.

The selected-column comparisons measure read throughput and the largest chunk's DataFrame memory footprint. They do not measure total preprocessing runtime, process peak RAM, disk usage, I/O-independent CPU cost, or model performance. Filesystem caching, disk speed, background load, and pandas/runtime versions affect results. Treat a single run as indicative, not as a formal speedup guarantee; compare repeated runs under similar conditions before making a performance claim. Any speed improvement is a trade-off only if the reduced representation retains every field required by the later investigation.

## Known limitations and future-stage decisions

- The newest-file rule assumes complete replacement exports. Incremental files are not merged, deduplicated, or ordered by event timestamp.
- Expected sensor/device IDs and environmental status constants are project-specific and intentionally strict. New IDs or altered source-system conventions stop processing until reviewed.
- Only the currently supported JSON list/variable/values shape is accepted, with at most one point per variable per record.
- The variable schema is derived from observed metadata. New or renamed variables can change the generated columns and should be checked against the schema report.
- The reduction of `processdate` is conditional on equality with `createdate`; measurement time remains a distinct field and can lag record time.
- `NaN` is retained for later analysis decisions. Interpolation, other imputation, deletion, and analysis suitability are not determined here.
- The occupancy location mapping is not joined because its floorspace IDs are known to be invalid. A verified mapping is needed before spatial analysis.
- No alignment of environmental and occupancy time ranges, measurement lag correction, time aggregation, or interpolation is performed.
- Benchmark timings are machine- and cache-dependent estimates; they do not describe the accuracy or engineering value of downstream methods.

The final project report must separately explain the engineering problem, computational model, chosen target, alternatives, model validation, engineering interpretation, and lessons learned required by the project brief.
