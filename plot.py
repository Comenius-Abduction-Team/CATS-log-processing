import pandas as pd
import matplotlib.pyplot as plt
import glob

def plot_file(file):
    # Load your result table
    df = pd.read_csv(file, sep=';')

    # Create the plot
    plt.figure(figsize=(10,6))

    

    # Plot each algorithm as a separate line
    for alg in df.columns[1:]:  # skip 'time_bin'
        plt.plot(df['time'], df[alg], label=alg)

    # Add labels and grid
    plt.xlabel("Time (sec)")
    plt.ylabel("Average Number of Explanations Already Found")
    plt.title("Algorithm Comparison: Average Explanations Found Over Time")
    plt.legend()
    plt.grid(True)

    # Show the plot
    plt.show()
    plt.savefig(f"{file}.pdf")

for file in glob.glob(f"*.csv"):
    plot_file(file)