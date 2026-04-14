import glob
import config as cfg
import pandas as pd
import matplotlib.pyplot as plt
import generic_funcs as generic
import numpy as np
from typing import *

config = cfg.config

def set_data_path(data_path):
    config.data_dir = data_path

def set_export_path(export_path):
    config.export_dir = export_path

def set_plot_labels(x : Optional[str]=None, y : Optional[str]=None, title : Optional[str]=None):
    config.update({
        'x_label': x,
        'y_label': y,
        'title': title
    })

def set_export_image_settings(width : Optional[float]=None, height : Optional[float]=None):
    config.update({
        'export_width': width,
        'export_height': height
    })

def set_limits_plt(xlim=None, ylim=None):
    if xlim is not None:
        plt.xlim(*xlim)
    if ylim is not None:
        plt.ylim(*ylim)

def set_limits_ax(ax, xlim=None, ylim=None):
    if xlim is not None:
        ax.set_xlim(*xlim)
    if ylim is not None:
        ax.set_ylim(*ylim)

def add_export_image_extension(extension : str):
    config.export_extensions.append(extension)

def remove_export_image_extension(extension : str):
    config.export_extensions.remove(extension)

def set_export_image_extensions(extensions : set[str]):
    config.export_extensions = extensions

def create_figure():
    plt.figure(figsize=(config.export_width, config.export_height))
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Cambria'],  # or 'Times New Roman', etc.
        'font.size': 13
    })

def save_figure(filename):
    generic.create_dir_if_not_exists(config.export_dir)
    for extension in config.export_extensions:
        plt.savefig(f"{config.export_dir}/{generic.sanitize_filename(filename)}.{extension}")

def show_figure():
    plt.show()

thresholds = [item for sublist in [[0.1*(10**i),0.25*(10**i),0.5*(10**i)] for i in range(10)] for item in sublist]

def calculate_tick_frequency(max_value : float) -> float:

    for threshold in thresholds:
        if max_value <= threshold:
            return threshold / 10
    return 0

def trim_line_graph(df):
    # Detect when each column reaches its final value
    global_last_change = 0
    for col in df.columns[1:]:  # skip 'time_bin'
        if col == 'QXP':
            pass
        final_val = df[col].iloc[-1]
        changes = (df[col] != final_val) & (~df[col].isna())
        last_non_final_index = changes[changes].index.max()
        if np.isnan(last_non_final_index):
            continue
        global_last_change = max(global_last_change, last_non_final_index)

    # Trim the dataframe up to that point (add 1 to include the row just before plateau)
    return df.iloc[:min(global_last_change + 1, df.size)]

def get_end_values(df):
    newDf = {}
    # Detect when each column reaches its final value
    for col in df.columns[1:]:  # skip 'time'
        final_val = df[col].iloc[-1]
        changes = (df[col] != final_val) & (~df[col].isna())
        last_non_final_index = changes[changes].index.max()
        if np.isnan(last_non_final_index):
            continue
        end_index = min(last_non_final_index + 1, df.size)

        newDf[col] = [0,0]
        newDf[col][0] = df['time'].iloc[end_index - 1]
        newDf[col][1] = df[col].iloc[end_index - 1]

    return newDf

def clip_df_by_xlim(df: pd.DataFrame, x_col: str, xlim):
    if xlim is None:
        return df

    xmin, xmax = xlim
    return df[(df[x_col] >= xmin) & (df[x_col] <= xmax)]


def scatter_line_graphs(x_axis_name : str, y_axis_name : str, discrete : bool, regex : str='/*.csv'):
    for file in glob.glob(f"{config.data_dir}{regex}"):
        scatter_line_graph(file, x_axis_name, y_axis_name, discrete)

def plot_line_graphs(x_axis_name : str, discrete : bool, regex : str='/*.csv'):
    for file in glob.glob(f"{config.data_dir}{regex}"):
        plot_line_graph(file, x_axis_name, discrete)


def plot_line_graph(file: str, x_axis_name: str, discrete: bool, logarithmic: bool = False,
                    xlim: Optional[Tuple[float, float]] = None, ylim: Optional[Tuple[float, float]] = None):
    file = config.data_dir + '/' + file

    print(f"Ploting file: {file}")

    create_figure()

    # Load your result table
    df = pd.read_csv(file, sep=';')
    #df = trim_line_graph(df)
    end_values = get_end_values(df)

    df = clip_df_by_xlim(df, x_axis_name, xlim) #new
    x = df[x_axis_name]
    #TODO orezat dataframe aby to bolo po urcite cislo a nie cely csv timeout (pridat ako dalsi nepovinny argument)

    #if limity:
        #plt.set_ylim(miny, maxy)
    #set_axis_limits(plt, xlim=xlim, ylim=ylim)
    set_limits_plt(xlim=xlim, ylim=ylim)


    if logarithmic:
        plt.set_yscale('symlog')


    if xlim is not None:
        min_x, max_x = xlim
    else:
        min_x, max_x = min(x), max(x)

    tick_freq = 0

    if discrete:
        plt.xticks(np.arange(min_x, max_x + 1, 1))
    else:
        tick_freq = calculate_tick_frequency(max_x)
        plt.xticks(np.arange(min_x, max_x, tick_freq))

    # Plot each algorithm as a separate line
    for alg in df.columns[1:]:
        if discrete:
            plt.plot(x, df[alg], label=alg, linewidth=config.plot_line_width,
                     color=config.get_plot_color(alg), marker=config.get_plot_marker(alg), alpha=0.75)
        else:
            plt.plot(x, df[alg], label='_nolegend_', linewidth=config.plot_line_width,
                     color=config.get_plot_color(alg), alpha=0.75)

            plt.plot([], [], label=alg, linewidth=config.plot_line_width,
                     color=config.get_plot_color(alg), alpha=0.75, marker=config.get_plot_marker(alg),
                     markersize=config.plot_mark_size)

            # markery v pravidelnych intervaloch pozdlz linie
            plt.plot(x[::max(int(tick_freq), 1)], df[alg][::max(int(tick_freq), 1)], label='_nolegend_',
                     color=config.get_plot_color(alg),
                     marker=config.get_plot_marker(alg), alpha=0.75, linestyle='none', markersize=config.plot_mark_size)

            # markery na zaciatku a konci linii
            try:
                plt.plot(end_values[alg][0], end_values[alg][1], label='_nolegend_',
                         color=config.get_plot_color(alg), marker=config.get_plot_marker(alg), alpha=0.75,
                         linestyle='none', markersize=config.plot_mark_size)

            except KeyError:
                continue

    # Add labels and grid
    plt.xlabel(config.x_label)
    plt.ylabel(config.y_label)
    plt.title(f"{config.title}: {generic.extract_filename_from_filepath(file)}")
    plt.legend(loc='upper center', ncol=3, bbox_to_anchor=(0.5, -0.1))
    # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),)
    plt.grid(True, alpha=0.25)
    plt.tight_layout()

    # Show the plot
    save_figure(generic.extract_filename_from_filepath(file))
    # show_figure()

    print("Figure saved!")

    plt.close()


def plot_line_graphs_grid(x_axis_name: str, discrete: bool, cols: int, rows: int, regex: str = '/*.csv', logarithmic : bool=False,
                          xlim: Optional[Tuple[float, float]] = None,
                          ylim: Optional[Tuple[float, float]] = None,
                          legend_cols : int=3,
                          rect: Tuple[float, float, float, float] = (0, 0.02, 1, 0.80),
                          order: Optional[List[str]] = None):

    files = glob.glob(f"{config.data_dir}{regex}")

    if order is not None:
        def sort_key(f):
            name = generic.extract_filename_from_filepath(f)
            try:
                return order.index(name)
            except ValueError:
                return len(order)  # čo nie je v zozname ide na koniec

        files = sorted(files, key=sort_key)

    fig, axes = plt.subplots(rows, cols, figsize=(cols * config.export_width, rows * config.export_height),
                             sharex=False, sharey=False)
    for ax in axes.flat:
        ax.tick_params(axis='x', which='major', labelsize=16, colors='black')
        ax.tick_params(axis='y', which='major', labelsize=18, colors='black')

    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Cambria'],  # or 'Times New Roman', etc.
        'font.size': 18,
        'axes.labelsize': 'large',
    })
    #fig.suptitle(config.title)

    axes = axes.flatten()
    all_lines = []

    for i, file in enumerate(files):
        ax = axes[i]
        df = pd.read_csv(file, sep=';')
        #df = trim_line_graph(df)
        end_values = get_end_values(df)

        df = clip_df_by_xlim(df, x_axis_name, xlim) #new
        x = df[x_axis_name]

        #if limity:
            #ax.set_ylim(miny, maxy)
        #set_axis_limits(plt, xlim=xlim, ylim=ylim)
        set_limits_ax(ax, xlim=xlim, ylim=ylim)

        if logarithmic:
            ax.set_yscale('symlog')

        if xlim is not None:
            min_x, max_x = xlim
        else:
            min_x, max_x = min(x), max(x)

        tick_freq = 0

        if discrete:
            ax.set_xticks(np.arange(min_x, max_x + 1, 1))
        else:
            tick_freq = calculate_tick_frequency(max_x)
            ax.set_xticks(np.arange(min_x, max_x, tick_freq))

        for label in ax.get_xticklabels():
            label.set_fontname('Cambria')
            label.set_fontweight('bold')

        for label in ax.get_yticklabels():
            label.set_fontname('Cambria')
            label.set_fontweight('bold')

        for alg in df.columns[1:]:

            if discrete:
                ax.plot(x, df[alg], label=alg, linewidth=config.plot_line_width,
                         color=config.get_plot_color(alg), marker=config.get_plot_marker(alg), alpha=0.75)

            else:
                line, = ax.plot(x, df[alg], label=alg, linewidth=config.plot_line_width,
                         color=config.get_plot_color(alg), alpha=0.75)
                '''ax.plot(x[::int(720)], df[alg][::int(720)], label='_nolegend_',
                         color=config.get_plot_color(alg),
                         marker=config.get_plot_marker(alg), alpha=0.75, linestyle='none')'''
                line, = ax.plot([], [], label=alg, linewidth=config.plot_line_width,
                                color=config.get_plot_color(alg), alpha=0.75, marker=config.get_plot_marker(alg), markersize=config.plot_mark_size)
                if i == 0:
                    all_lines.append(line)

                ax.plot(x[::max(int(tick_freq),1)], df[alg][::max(int(tick_freq),1)], label='_nolegend_',
                         color=config.get_plot_color(alg),
                         marker=config.get_plot_marker(alg), alpha=0.75, linestyle='none', markersize=config.plot_mark_size)
                try:
                    ax.plot(end_values[alg][0], end_values[alg][1], label='_nolegend_',
                             color=config.get_plot_color(alg), marker=config.get_plot_marker(alg), alpha=0.75,
                             linestyle='none', markersize=config.plot_mark_size)
                    # print(f'max_x: {max_x}, last: {end_values[alg][0]}, dif: {max_x - end_values[alg][0]}, margin: {max_x * 0.25}')
                    if max_x - end_values[alg][0] > max_x * 0.75:
                        '''
                        ax.plot(end_values[alg][0] + 200, end_values[alg][1], label='_nolegend_', color=config.get_plot_color(alg),
                                marker=1, alpha=1, linestyle='none', markersize=8.5)
                        all_lines.append(line)
                        ax.plot(end_values[alg][0] + 200, end_values[alg][1], label='_nolegend_', color=config.get_plot_color(alg),
                                marker=8, alpha=1, linestyle='none', markersize=10)
                        all_lines.append(line)
                        '''

                except KeyError:
                    continue

        ax.set_title(generic.extract_filename_from_filepath(file), fontname="Cambria")
        ax.grid(True)

    # Hide unused subplots if any
    for i in range(len(files), len(axes)):
        fig.delaxes(axes[i])

    # Set shared labels
    fig.supxlabel(config.x_label)
    fig.supylabel(config.y_label)

    # Global legend
    fig.legend(handles={l.get_label(): l for l in all_lines}.values(), loc='upper center', ncol=legend_cols)
    #bbox_to_anchor=(0.5, -0.05)


    fig.tight_layout(rect=rect)  # Leave space for legend & title

    # Save single figure
    generic.create_dir_if_not_exists(config.export_dir)
    for ext in config.export_extensions:
        fig.savefig(f"{config.export_dir}/{generic.sanitize_filename(config.title)}.{ext}")

    plt.close(fig)

def scatter_line_graph(file : str, x_axis_name : str, y_axis_name : str, discrete : bool):

    print(f"Ploting file: {file}")

    # Load your result table
    df = pd.read_csv(file, sep=';')

    # Create the plot
    create_figure()

    for alg in df['algorithm'].unique():
        alg_df = df[df['algorithm'] == alg].copy()
        if discrete:
            alg_df[x_axis_name] += np.random.uniform(-0.45, 0.45, size=len(alg_df))
        plt.scatter(alg_df[x_axis_name], alg_df[y_axis_name], label=alg, alpha=0.7,color=config.get_plot_color(alg),marker=config.get_plot_marker(alg))

    try:
        max_x = max(df[x_axis_name])
        min_x = min(df[x_axis_name])

        if discrete:
            plt.xticks(np.arange(min_x, max_x + 1, 1))
        else:
            tick_freq = calculate_tick_frequency(max_x)
            plt.xticks(np.arange(min_x, max_x + tick_freq, tick_freq))
    except KeyError:
        pass

    # Add labels and grid
    plt.xlabel(config.x_label)
    plt.ylabel(config.y_label)
    plt.title(f"{config.title}: {generic.extract_filename_from_filepath(file)}")
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=5)
    plt.grid(True)

    # Show the plot
    save_figure(generic.extract_filename_from_filepath(file))
    #show_figure()

    print("Figure saved!")

    plt.close()

def compare_memory_error(filename : str, output : str):

    df = pd.read_csv(filename, sep=';', decimal=',')

    # Replace commas in numeric strings and convert to float
    df["Original runtime"] = pd.to_numeric(df["Original runtime"], errors='coerce')
    df["New runtime"] = pd.to_numeric(df["New runtime"], errors='coerce')

    # Set up bar positions
    labels = df["Input"]
    x = np.arange(len(labels))
    width = 0.4

    # Create the plot
    #fig, ax = plt.subplots(figsize=(10, 6))

    create_figure()
    #plt.grid(True)

    bars1 = plt.bar(x - width/2, df["Original runtime"], width, label='Original', edgecolor=config.get_plot_color('MHS-MXP'), color='brown')
    bars2 = plt.bar(x + width/2, df["New runtime"], width, label='New', edgecolor=config.get_plot_color('original MHS-MXP'), color='lightseagreen')

    # Add "error" labels
    for i, (mark_orig, mark_new) in enumerate(zip(df["Original mark"], df["New mark"])):
        if pd.notna(mark_orig) and str(mark_orig).strip() == "error":
            plt.text(x[i] - width/2, df["Original runtime"][i] + 500, 'X', ha='center', color='darkred')
        if pd.notna(mark_new) and str(mark_new).strip() == "error":
            plt.text(x[i] + width/2, df["New runtime"][i] + 500, 'X', ha='center', color='darkred')

    # Customize plot
    plt.ylabel('Runtime duration (secs)')
    plt.title('')
    plt.xticks(x, labels)

    plt.xlabel('Inputs')
    #plt.xticklabels(labels)
    #plt.legend()

    plt.tight_layout()
    #plt.show()

    save_figure(output)