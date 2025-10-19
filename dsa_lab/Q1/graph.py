import matplotlib.pyplot as plt
import pandas as pd

# Read CSVs with proper headers
data1 = pd.read_csv("Lab1/LinearTimeComplexity.csv")
data2 = pd.read_csv("Lab1/SquaredTimeComplexity.csv")

# Create a figure with 2 subplots (1 row, 2 columns)
fig, axs = plt.subplots(1, 2, figsize=(12, 5))

# Plot for Linear Time Complexity
axs[0].plot(data1['n'], data1['time'], marker='o', label="O(n)")
axs[0].set_title("Linear Time Complexity")
axs[0].set_xlabel("Input Size (n)")
axs[0].set_ylabel("Time (s)")
axs[0].grid(True)
axs[0].legend()

# Plot for Squared Time Complexity
axs[1].plot(data2['n'], data2['time'], marker='o', color='orange', label="O(n²)")
axs[1].set_title("Squared Time Complexity")
axs[1].set_xlabel("Input Size (n)")
axs[1].set_ylabel("Time (s)")
axs[1].grid(True)
axs[1].legend()

# Adjust layout to prevent overlap
plt.tight_layout()

# Show the plots
plt.show()