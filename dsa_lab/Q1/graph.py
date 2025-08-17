import matplotlib.pyplot as plt
import pandas as pd

def load_data(filename='output.csv'):
    """Load performance data from CSV file"""
    try:
        df = pd.read_csv(filename)
        return df
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        return None

def plot_algorithms(df):
    """Plot both O(n) and O(n^2) algorithms"""
    
    # Graph 1: O(n) Algorithm
    plt.figure(figsize=(10, 6))
    plt.plot(df['inputs'], df['time(n)'], 'o-', linewidth=2, markersize=8, color='blue')
    plt.xlabel('Input Size')
    plt.ylabel('Time (ms)')
    plt.title('O(n) Algorithm Performance')
    plt.grid(True)
    plt.show()
    
    # Graph 2: O(n^2) Algorithm  
    plt.figure(figsize=(10, 6))
    plt.plot(df['inputs'], df['time(n^2)'], 's-', linewidth=2, markersize=8, color='red')
    plt.xlabel('Input Size')
    plt.ylabel('Time (ms)')
    plt.title('O(n²) Algorithm Performance')
    plt.grid(True)
    plt.show()

def main():
    df = load_data()
    if df is not None:
        plot_algorithms(df)

if __name__ == "__main__":
    main()