import pandas as pd
import matplotlib.pyplot as plt
import glob

def plot_file(file):
    # Load your result table
    df = pd.read_csv(file, sep=';')

    # Create the plot
    plt.figure(figsize=(10,6))

    # Detect when each column reaches its final value
    last_change = 0
    for col in df.columns[1:]:  # skip 'time_bin'
        final_val = df[col].iloc[-1]
        changes = df[col] != final_val
        last_non_final_index = changes[changes].index.max()
        last_change = max(last_change, last_non_final_index)

    # Trim the dataframe up to that point (add 1 to include the row just before plateau)
    df = df.iloc[:min(last_change + 10,df.size)]

    # Plot each algorithm as a separate line
    for alg in df.columns[1:]:  # skip 'time_bin'
        plt.plot(df['time'], df[alg], label=alg)

    # Add labels and grid
    plt.xlabel("Time (sec)")
    plt.ylabel("Average Number of Explanations Already Found")
    plt.title(f"Average Explanations Found Over Time: {file}")
    plt.legend()
    plt.grid(True)

    # Show the plot
    plt.savefig(f"{file}.png")
    #plt.show()

for file in glob.glob(f"results/*.csv"):
    plot_file(file)
