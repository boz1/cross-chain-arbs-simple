import os, glob
import pandas as pd
import numpy as np

INPUT_RAW_DIR = "data/raw"
OUTPUT_DIR = "data/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Load and concatenate all raw CSVs ──
raw_df = pd.concat(
    [pd.read_csv(f) for f in glob.glob(os.path.join(INPUT_RAW_DIR, "*.csv"))],
    ignore_index=True,
)


# ── Preprocessing ──
def preprocess(df):
    df["bt1"] = pd.to_datetime(df["bt1"], errors="coerce")
    df["bt2"] = pd.to_datetime(df["bt2"], errors="coerce")
    # Ensure diff_pct column exists
    if "raw_diff_pct_2" not in df.columns:
        df["raw_diff_pct_2"] = np.nan
    for col in ["raw_diff_pct_1", "raw_diff_pct_2", "time_diff"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Choose the smaller diff_pct on ties
    df["diff_pct"] = np.where(
        df["bt1"] == df["bt2"],
        df[["raw_diff_pct_1", "raw_diff_pct_2"]].min(axis=1),
        df["raw_diff_pct_1"],
    )
    return df


raw_df = preprocess(raw_df)

# ── Filter with fixed heuristic ──
MARGIN = 0.005  # 0.5%
MAX_TIME = 3600  # 1 hour in seconds

filtered = raw_df[
    (raw_df["diff_pct"] <= MARGIN) & (raw_df["time_diff"].abs() <= MAX_TIME)
].copy()

# ── Deduplicate by prioritizing margin then time ──
# Identify duplicates
tx_counts = pd.concat([filtered["tx1"], filtered["tx2"]]).value_counts()
dup_hashes = tx_counts[tx_counts > 1].index

unique_matches = filtered[
    ~filtered["tx1"].isin(dup_hashes) & ~filtered["tx2"].isin(dup_hashes)
]
dup_matches = filtered[
    filtered["tx1"].isin(dup_hashes) | filtered["tx2"].isin(dup_hashes)
].copy()

# Priority scoring
dup_matches["priority_margin"] = dup_matches["diff_pct"].apply(
    lambda x: 0 if x <= 0.001 else 1
)
dup_matches["priority_time"] = (
    dup_matches["time_diff"].abs().apply(lambda x: 0 if x <= 240 else 1)
)

dup_matches = dup_matches.sort_values(
    ["priority_margin", "priority_time", "diff_pct", "time_diff"]
)

# Greedy resolve
used, selected = set(), []
for _, row in dup_matches.iterrows():
    t1, t2 = row["tx1"], row["tx2"]
    if t1 in used or t2 in used:
        continue
    selected.append(row)
    used.update([t1, t2])

resolved = (
    pd.DataFrame(selected) if selected else pd.DataFrame(columns=filtered.columns)
)
final_matches = pd.concat([unique_matches, resolved], ignore_index=True)

# ── Save final matches ──
output_path = os.path.join(OUTPUT_DIR, "filtered_cross_chain_swaps.csv")
final_matches.to_csv(output_path, index=False)
print(f"Saved filtered and deduplicated swaps to {output_path}")
