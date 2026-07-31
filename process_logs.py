import os
import re

import pandas as pd
import numpy as np
import generic_funcs as gen
import config as cfg
import glob
from typing import *
from enum import Enum

from generic_funcs import generate_lubm_input_folder_string

config = cfg.config

# WHICH EXPLANATION DISCOVERY TIMES SHOULD BE CONSIDERED
class Mode(Enum):
    ALL_EXPLANATIONS = 0  # every explanation discovery time
    FIRST_EXPLANATION = 1 # only the first discovered explanation time
    LAST_EXPLANATION = 2  # only the last discovered explanation time


# TIMES FOR WHICH THE AVERAGES WILL BE MEASURED
max_time = 7200 # maximal time to be shown in th graph
interval = 0.5  # at what interval should the averages be measured (if alldata happens in a time window shorter than the interval, it can'tbe captured)
time_bins = np.arange(0, max_time + interval, interval)

size_bins = np.arange(1, 6)
size_range = range(1, 6)

def set_logs_path(logs: Optional[str] = None, ontology: Optional[str] = None, input: Optional[str] = None, filename: Optional[str] = None):
    config.update({
        'logs_dir': logs,
        'ontology_dir': ontology,
        'input_dir': input,
        'filename': filename
    })

def ignore_default_path_structure(flag : bool):
    config.ignore_default_path_structure = flag

def set_output_path( outputs_dir : Optional[str]=None, file_prefix : Optional[str]=None, file_postfix : Optional[str]=None):

    config.update({
        'output_dir': outputs_dir,
        'output_filename_prefix': file_prefix,
        'output_filename_postfix': file_postfix
    })

def set_algs(alg_list : Sequence[str]):
    config.algs = alg_list

def avg_exps_over_time():

    def get_final_time(file_path):
        final_path = file_path.replace("_explanation-times", "_final")

        if not os.path.isfile(final_path):
            print(f"⚠️ Final file not found: {final_path}")
            return None

        with open(final_path, 'r') as f:
            for line in reversed(f.readlines()):  # prechádzame súbor odzadu
                line = line.strip()
                match = re.search(r'Time:\s*([0-9.]+)', line)
                if match:
                    return float(match.group(1))

        print(f"⚠️ Time pattern not found in final file: {final_path}")
        return None


    all_results = {}

    for alg in config.algs:

        print(f"ALGORITHM: {alg}")

        if config.ignore_default_path_structure:
            regex = f"{config.logs_dir}/{alg}/{config.filename}_explanation-times.log"
        else:
            regex = f"{config.logs_dir}/{alg}/{config.ontology_dir}/{config.input_dir}/{config.filename}_explanation-times.log"
        files = glob.glob(regex)

        if not files:
            print(f"{regex}: EMPTY OR NONEXISTENT!")
            continue

        helper_tables = []
        alg_max_time = 0.0

        for file in files:
            print(f"Processing file: {file}")

            df = pd.read_csv(file, sep=';', names=['time', 'length', 'explanation'])
            df = df.sort_values('time')  # should already be sorted but safe

            log_max_time = get_final_time(file)
            if log_max_time is None:
                continue

            # Convert time to bin index
            log_max_index = int(log_max_time // interval)
            alg_max_time = max(alg_max_time, log_max_index)

            # For each bin: how many explanations have been found up to that time
            counts = np.searchsorted(df['time'].values, time_bins, side='right')

            # Store as DataFrame
            helper_df = pd.DataFrame({'time': time_bins, 'count': counts})
            helper_tables.append(helper_df)

        if helper_tables:
            merged = pd.concat(helper_tables)
            avg_result = merged.groupby('time')['count'].mean().reset_index()

            try:
                count_values = avg_result['count'].values[:int(alg_max_time)+1]
            except ValueError:
                count_values = avg_result['count'].values[:3]

            padded_values = np.pad(count_values, (0, len(time_bins) - len(count_values)), mode='constant',
                                   constant_values=np.nan)
            all_results[alg] = padded_values

        else:
            print(f"No files found for {alg}. Filling with NaN.")
            all_results[alg] = [np.nan]

    # Combine into one big DataFrame
    final_df = pd.DataFrame({'time': time_bins})

    for alg in config.algs:
        if alg not in all_results:
            continue
        final_df[alg] = all_results[alg]

    # Export to single CSV
    export_data(final_df)

def avg_time_by_size(negations : bool=None, mode : Mode=Mode.ALL_EXPLANATIONS):

    final_df = pd.DataFrame({'size': size_bins})

    for alg in config.algs:

        print(f"ALGORITHM: {alg}")

        rows = []

        for size in size_range:

            print(f"SIZE: {size}")

            files = glob.glob(
                f"{config.logs_dir}/{alg}/{config.ontology_dir}/" +
                f"{generate_lubm_input_folder_string(negations=negations, level=size)}" +
                f"/{config.filename}explanation-times.log")

            if not files:
                continue

            for file in files:

                print(f"Processing file: {file}")

                df = pd.read_csv(file, sep=';', names=['time', 'length', 'explanation'])
                df = df.sort_values('time')

                if mode == Mode.ALL_EXPLANATIONS:
                    for time in df['time']:
                        rows.append({'size': size, 'time': time})

                else:

                   if not df.empty:
                        time = None
                        if mode == Mode.FIRST_EXPLANATION:
                            time=df.iloc[0]['time']
                        elif mode == Mode.LAST_EXPLANATION:
                            time=df.iloc[-1]['time']
                        rows.append({'size':size, 'time':time})

        if len(rows) == 0:
            final_df[alg] = pd.DataFrame(None for _ in size_range)
            continue

        helper_df = pd.DataFrame(rows)

        try:
            helper_df = helper_df.groupby('size')['time'].mean().reset_index()
        except KeyError:
            print(helper_df)
        helper_df = helper_df.set_index('size').reindex(size_range).reset_index()

        final_df[alg] = helper_df['time'].values

    # Export to single CSV
    export_data(final_df)

def count_by_size(negations : bool=None, average : bool=False):

    final_df = pd.DataFrame({'size': size_bins})

    for alg in config.algs:

        print(f"ALGORITHM: {alg}")

        alg_counts = []

        for size in size_range:

            total_count = 0
            file_count = 0

            print(f"SIZE: {size}")

            files = glob.glob(
                f"{config.logs_dir}/{alg}/{config.ontology_dir}/" +
                f"{generate_lubm_input_folder_string(negations=negations, level=size)}" +
                "/*explanation-times.log")

            if not files:
                continue

            for file in files:

                print(f"Processing file: {file}")

                with open(file) as f:
                    row_count = sum(1 for line in f if line.strip()) #row_count = sum(1 for _ in f) - 1 TODO check
                total_count += row_count

                if average:
                    file_count += 1

            if average:
                total_count /= file_count

            alg_counts.append(total_count)

        final_df[alg] = alg_counts

    # Export to single CSV
    export_data(final_df)

def scatter_expl_time_by_size(negations : bool=None, mode : Mode=Mode.ALL_EXPLANATIONS):

    all_points = []

    for alg in config.algs:

        print(f"ALGORITHM: {alg}")

        rows = []

        for size in size_range:

            print(f"SIZE: {size}")

            files = glob.glob(
                f"{config.logs_dir}/{alg}/{config.ontology_dir}/" +
                f"{generate_lubm_input_folder_string(negations=negations, level=size)}" +
                "/*explanation-times.log")

            if not files:
                continue

            for file in files:

                print(f"Processing file: {file}")

                df = pd.read_csv(file, sep=';', names=['time', 'length', 'explanation'])
                df = df.sort_values('time')

                if mode == Mode.ALL_EXPLANATIONS:
                    for time in df['time']:
                        rows.append({'size': size, 'time': time})

                else:

                   if not df.empty:
                        time = None
                        if mode == Mode.FIRST_EXPLANATION:
                            time=df.iloc[0]['time']
                        elif mode == Mode.LAST_EXPLANATION:
                            time=df.iloc[-1]['time']
                        rows.append({'size':size, 'time':time})

        helper_df = pd.DataFrame(rows)

        helper_df['algorithm'] = alg
        all_points.append(helper_df)

    # Concatenate all collected points into one DataFrame
    final_df = pd.concat(all_points)
    export_data(final_df)

def scatter_stat_by_size(stat : str='finish time'):

    all_points = []

    for alg in config.algs:

        print(f"ALGORITHM: {alg}")

        rows = []

        for size in size_range:

            print(f"SIZE: {size}")

            files = glob.glob(
                f"{config.logs_dir}/{alg}/{config.ontology_dir}/" +
                f"{config.input_dir}" +
                "/*neg_level.log")

            if not files:
                continue

            for file in files:

                print(f"Processing file: {file}")

                df = pd.read_csv(file, sep=';')[stat]

                if not df.empty:
                    # new, TODO check
                    final_row = df[df['level'] == 'f']
                    if not final_row.empty:
                        time = final_row.iloc[0][stat]

                    #time = df.iloc[-1]
                    rows.append({'size': size, 'time': time})

        helper_df = pd.DataFrame(rows)

        helper_df['algorithm'] = alg
        all_points.append(helper_df)

    # Concatenate all collected points into one DataFrame
    final_df = pd.concat(all_points)
    export_data(final_df)

def scatter_level_stat(y_axis_stat : str, x_axis_stat : str= 'finish time'):

    all_points = []

    # Process each algorithm
    for alg in config.algs:

        if config.ignore_default_path_structure:
            regex = f"{config.logs_dir}/{alg}/{config.filename}neg_level.log"
        else:
            regex = f"{config.logs_dir}/{alg}/{config.ontology_dir}/{config.input_dir}/{config.filename}neg_level.log"
        files = glob.glob(regex)

        if not files:
            print(f"{regex}: EMPTY OR NONEXISTENT!")
            continue

        rows = []

        for file in files:

            print(f"Processing file: {file}")

            df = pd.read_csv(file, delimiter=';')[[y_axis_stat,x_axis_stat]]
            df = df[df['level'] != 'f'] #df = df.iloc[:-1] TODO check

            rows.append(df)

        helper_df = pd.concat(rows)
        helper_df['algorithm'] = alg
        all_points.append(helper_df)

    # Concatenate all collected points into one DataFrame
    final_df = pd.concat(all_points)
    export_data(final_df)

def interpolate_level_stats_over_time(y_axis_stat : str, cumulative : bool=False):

    final_df = pd.DataFrame({'time':time_bins})

    # Process each algorithm
    for alg in config.algs:

        if config.ignore_default_path_structure:
            regex = f"{config.logs_dir}/{alg}/{config.filename}neg_level.log"
        else:
            regex = f"{config.logs_dir}/{alg}/{config.ontology_dir}/{config.input_dir}/{config.filename}neg_level.log"
        files = glob.glob(regex)

        if not files:
            print(f"{regex}: EMPTY OR NONEXISTENT!")
            continue

        helper_table = []

        for file in files:

            print(f"Processing file: {file}")

            df = pd.read_csv(file, delimiter=';')
            df = df[df['level'] != 'f'] #df = df.iloc[:-1]

            # Skip invalid or empty files
            if 'finish time' not in df.columns or y_axis_stat not in df.columns or df.empty:
                print(f"{file}: DATA MISSING!")
                continue

            df = df.sort_values('finish time')
            if cumulative:
                df[y_axis_stat] = df[y_axis_stat].cumsum()

            # Interpolation only up to the last time value in this run
            last_time = df['finish time'].max()
            trimmed_time_bins = time_bins[time_bins <= last_time]

            # Interpolate memory values
            interp = np.interp(trimmed_time_bins, df['finish time'], df[y_axis_stat])

            # Pad with NaNs so all arrays are of equal length
            #padded = np.full_like(time_bins, np.nan, dtype=float)
            #padded[:len(interp)] = interp
            series = pd.Series(interp)
            if cumulative and not series.is_monotonic_increasing:
                interp = series.cumsum()

            helper_table.append(interp)

        if helper_table:
            memory_df = pd.DataFrame(helper_table).T  # transpose so rows = time steps
            final_df[alg] = memory_df.mean(axis=1)

    # Export to single CSV
    export_data(final_df)

def check_timeout(negations : bool=None):
    # Initialize final dataframe with 'size' column
    final_df = pd.DataFrame({'size': list(size_range)})

    for alg in config.algs:

        timeout_counts = []

        for size in size_range:

            print(f"SIZE: {size}")

            files = glob.glob(
                f"{config.logs_dir}/{alg}/{config.ontology_dir}/" +
                f"{generate_lubm_input_folder_string(negations=negations, level=size)}" +
                "/*neg_level.log"
            )

            timeout_file_count = 0

            for file in files:
                try:
                    df = pd.read_csv(file, sep=';')

                    # Check if any 'message' cell contains "time-out"
                    if 'message' in df.columns and df['message'].astype(str).str.contains("time-out").any():
                        timeout_file_count += 1

                except Exception as e:
                    print(f"!!! Error reading {file}: {e}")

            timeout_counts.append(timeout_file_count)

        # Add this algorithm's results to the final dataframe
        final_df[alg] = timeout_counts

    export_data(final_df)

def avg_time_without_timeout(negations : bool=None):
    # Initialize final dataframe with 'size' column
    final_df = pd.DataFrame({'size': list(size_range)})

    for alg in config.algs:

        rows = []

        for size in size_range:

            print(f"SIZE: {size}")

            files = glob.glob(
                f"{config.logs_dir}/{alg}/{config.ontology_dir}/" +
                f"{generate_lubm_input_folder_string(negations=negations, level=size)}" +
                "/*neg_level.log"
            )

            if not files:
                continue

            for file in files:

                print(f"Processing file: {file}")

                try:
                    df = pd.read_csv(file, sep=';')

                    # Check if any 'message' cell contains "time-out"
                    if 'message' in df.columns and ~df['message'].astype(str).str.contains("time-out").any():
                        time = df.iloc[-1]['finish time']
                        rows.append({'size': size, 'time': time})

                except Exception as e:
                    print(f"!!! Error reading {file}: {e}")

        if len(rows) == 0:
            final_df[alg] = pd.DataFrame(None for _ in size_range)
            continue

        helper_df = pd.DataFrame(rows)

        try:
            helper_df = helper_df.groupby('size')['time'].mean().reset_index()
        except KeyError:
            print(helper_df)
        helper_df = helper_df.set_index('size').reindex(size_range).reset_index()

        final_df[alg] = helper_df['time'].values

    export_data(final_df)

def export_data(df : pd.DataFrame):
    gen.create_dir_if_not_exists(config.output_dir)
    path = f"{config.output_dir}/{gen.sanitize_filename(config.output_filename_prefix)}{gen.sanitize_filename(config.output_filename_postfix)}.csv"
    df.to_csv(path,sep=';', index=False)

