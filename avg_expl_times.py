import pandas as pd
import numpy as np
import glob
import re

def sanitize_filename(name, replacement="-"):
    return re.sub(r'[\\/*?:"<>|]', replacement, name)

# CONSTANT ALGORITHM GROUPS
_INCOMPLETE_ALGS = ['QXP', 'MXP']
_BASE_ALGS = ['MHS', 'HST', 'RCT']
_HYBRID_ALGS = [f'{alg}_MXP' for alg in _BASE_ALGS]
_COMPLETE_ALGS = [*_BASE_ALGS, *_HYBRID_ALGS]
_ALL_ALGS = [*_INCOMPLETE_ALGS, *_COMPLETE_ALGS]

# FILEPATHS WHERE TO SEARCH FOR LOGS
# (use * for 'any folder')
folder = "logs" #e.g. logs, ., ...
ontology_folder = "lubm-0" #e.g. *, lubm-0, family, ...
input_folder = "*" # e.g. *_noneg, lubm-0_1*, lubm-0_5*_neg, ...

# TIMES FOR WHICH THE AVERAGES WILL BE MEASURED
max_time = 7200 # maximal time to be shown in th graph
interval = 0.5  # at what interval should the averages be measured
time_bins = np.arange(0, max_time + interval, interval)

# THE SET OF ALGORITHMS CHOSEN FOR THE MEASURING
# each algorithm will have its own column in the resulting file
algs = _COMPLETE_ALGS

def main():

    all_results = {}

    for alg in algs:

        print(f"ALGORITHM: {alg}")

        helper_tables = []

        files = glob.glob(f"{folder}/{alg}/{ontology_folder}/{input_folder}/*explanation_times.log")

        if not files:
            continue

        for file in files:

            print(f"Processing file: {file}")

            df = pd.read_csv(file, sep=';', names=['time', 'explanation'])
            df = df.sort_values('time')  # should already be sorted but safe

            # For each bin: how many explanations have been found up to that time
            counts = np.searchsorted(df['time'].values, time_bins, side='right')

            # Store as DataFrame
            helper_df = pd.DataFrame({'time': time_bins, 'count': counts})
            helper_tables.append(helper_df)

        if helper_tables:
            merged = pd.concat(helper_tables)
            avg_result = merged.groupby('time')['count'].mean().reset_index()
            all_results[alg] = avg_result['count'].values  # save just the values

        else:
            print(f"No files found for {alg}. Filling with NaN.")
            all_results[alg] = [np.nan] * len(time_bins)

    # Combine into one big DataFrame
    final_df = pd.DataFrame({'time': time_bins})

    for alg in _COMPLETE_ALGS:
        final_df[alg] = all_results[alg]

    # Export to single CSV
    final_df.to_csv(
        f"results/avg_expl_times_{sanitize_filename(input_folder)}.csv",
        sep=';', index=False
    )

if __name__ == '__main__':
    for i in range(5):
        input_folder = f"lubm-0_{i+1}*_noneg"
        main()
