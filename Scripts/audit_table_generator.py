"""
Build the data audit table for rs-fMRI/timeseries.

Final table columns (in this order):
  Subject ID | Condition | Format | Dimensions | TR | Timepoints | Notes

Notes:
  - Condition is derived by checking which of the two expected fields
    (target_meants_pre / target_meants_post) exist inside each .mat file:
    "Pre/Post", "Pre", "Post", or "None found".
  - Dimensions and Timepoints are derived from the shapes of those same
    fields (whichever are present).
  - TR is set to "NA" for every row, since it cannot be derived from these
    files -- it must come from the paper's Supplementary Information or
    the scanner protocol.
  - Target (VIM/ZI) is recorded in the Notes column, not as its own column.

Filename pattern expected: sub-fuspd01_ses-2_roi-vim_meants.mat

USAGE:
  1. Update TIMESERIES_DIR to point to your local copy of rs-fMRI/timeseries
  2. Confirm TARGET_PRE_KEY / TARGET_POST_KEY match your actual field names
     (run inspect_one_file() on a sample file first if unsure)
  3. Run: python build_audit_table.py
  4. Check audit_table.csv for the result
"""

import os
import re
import glob
import scipy.io as sio
import pandas as pd

# ---- CONFIG: update this path to your local copy ----
TIMESERIES_DIR = "../Data/rsfMRI/timeseries"

# Best-guess field names -- confirm these against your actual files
TARGET_PRE_KEY = "target_meants_pre"
TARGET_POST_KEY = "target_meants_post"

FNAME_PATTERN = re.compile(
    r"sub-(?P<subject>\w+?)_ses-(?P<session>\d+)_roi-(?P<target>\w+)_meants\.mat"
)


def inspect_one_file(filepath):
    """Utility: print all fields/shapes in a single file to confirm key names."""
    data = sio.loadmat(filepath)
    print(f"\n--- {filepath} ---")
    for k, v in data.items():
        if not k.startswith("__"):
            print(f"  {k}: shape={getattr(v, 'shape', None)}")
    return data


def get_condition(data):
    """Return 'Pre/Post', 'Pre', 'Post', or 'None found' based on which
    fields are actually present in the loaded .mat file."""
    has_pre = TARGET_PRE_KEY in data
    has_post = TARGET_POST_KEY in data

    if has_pre and has_post:
        return "Pre/Post"
    elif has_pre:
        return "Pre"
    elif has_post:
        return "Post"
    else:
        return "None found"


def get_shape(array):
    return getattr(array, "shape", None)


def get_timepoints(array):
    """Number of timepoints = largest dimension of the array
    (handles both row and column vector orientations)."""
    shape = get_shape(array)
    if not shape:
        return None
    return max(shape)


def get_dimensions_and_timepoints(data):
    """Return (Dimensions string, Timepoints string) built from whichever
    of the pre/post fields are present, e.g.
    Dimensions: 'Pre: (1, 210), Post: (1, 205)'
    Timepoints: 'Pre: 210, Post: 205'
    """
    dim_parts = []
    tp_parts = []

    if TARGET_PRE_KEY in data:
        pre_arr = data[TARGET_PRE_KEY]
        dim_parts.append(f"Pre: {get_shape(pre_arr)}")
        tp_parts.append(f"Pre: {get_timepoints(pre_arr)}")

    if TARGET_POST_KEY in data:
        post_arr = data[TARGET_POST_KEY]
        dim_parts.append(f"Post: {get_shape(post_arr)}")
        tp_parts.append(f"Post: {get_timepoints(post_arr)}")

    dimensions = ", ".join(dim_parts) if dim_parts else None
    timepoints = ", ".join(tp_parts) if tp_parts else None
    return dimensions, timepoints


def build_table(timeseries_dir):
    rows = []
    files = sorted(glob.glob(os.path.join(timeseries_dir, "*.mat")))

    if not files:
        print(f"WARNING: no .mat files found in {timeseries_dir}. Check the path.")
        return pd.DataFrame()

    for filepath in files:
        fname = os.path.basename(filepath)
        match = FNAME_PATTERN.match(fname)

        row = {
            "Subject ID": None,
            "Condition": None,
            "Format": os.path.splitext(fname)[1],
            "Dimensions": None,
            "TR": "NA",
            "Timepoints": None,
            "Notes": "",
        }

        if not match:
            row["Notes"] = f"Filename '{fname}' did not match expected pattern"
            rows.append(row)
            continue

        subject = match.group("subject")
        target = match.group("target").upper()
        row["Subject ID"] = subject

        try:
            data = sio.loadmat(filepath)
        except Exception as e:
            row["Notes"] = f"Target: {target}; failed to load file: {e}"
            rows.append(row)
            continue

        row["Condition"] = get_condition(data)
        dimensions, timepoints = get_dimensions_and_timepoints(data)
        row["Dimensions"] = dimensions
        row["Timepoints"] = timepoints
        row["Notes"] = f"Target: {target}; filename: {fname}"

        rows.append(row)

    df = pd.DataFrame(rows, columns=[
        "Subject ID", "Condition", "Format", "Dimensions",
        "TR", "Timepoints", "Notes"
    ])
    return df


def check_completeness(df):
    """Flag any row missing pre or post data, based on the Condition column."""
    issues = []
    for _, r in df.iterrows():
        if r["Condition"] in (None, "Pre", "Post", "None found"):
            issues.append(f"{r['Subject ID']} ({r['Notes']}): Condition = {r['Condition']}")
    return issues


if __name__ == "__main__":
    df = build_table(TIMESERIES_DIR)

    if not df.empty:
        output_path = "../Results/audit_table_with_filename.csv"
        df.to_csv(output_path, index=False)
        print(f"Saved {len(df)} rows to {output_path}\n")
        print(df)

        print(f"\nUnique subjects found: {df['Subject ID'].nunique()}")

        print("\n--- Rows NOT showing both Pre and Post ---")
        issues = check_completeness(df)
        if issues:
            for issue in issues:
                print(" -", issue)
        else:
            print("Every file contains both Pre and Post data.")