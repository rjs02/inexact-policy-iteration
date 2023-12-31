import os
import json
import numpy as np
import matplotlib.pyplot as plt
import argparse

# replace this with your directory
# file path as command line argument
parser = argparse.ArgumentParser(description='Plot runtimes and speedup of iPI')
parser.add_argument('--path', required=True, help='path of the output data (parent directory of cpu directories)')
args = parser.parse_args()
main_dir = args.path

# Get all directories = numCPUs
cpu_dirs = [d for d in os.listdir(main_dir) if os.path.isdir(os.path.join(main_dir, d))]
cores = [int(cpu_dir) for cpu_dir in cpu_dirs]

# lists to store data
cpu_counts = []
means = []
mins = []
maxs = []

# Generate dict with cpu counts as keys and list of runtimes as values
runtime = {}

for cpu_dir in cpu_dirs:
    json_path = os.path.join(main_dir, cpu_dir, 'stats.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    total_runtime_per_run = []
    for run in data['solver_runs']:
        total_runtime = sum([iteration['computation_time'] for iteration in run])
        total_runtime_per_run.append(total_runtime / 1000)

    runtime[cpu_dir] = total_runtime_per_run

# make runtime vs cpu count plot
# calculate mean, min, max

for cpu_count, runtimes in runtime.items():
    means.append(np.mean(runtimes))
    mins.append(np.min(runtimes))
    maxs.append(np.max(runtimes))
    cpu_counts.append(int(cpu_count))  # assuming directory names can be converted to integers

# sort data by cpu_counts
cpu_counts, means, mins, maxs = zip(*sorted(zip(cpu_counts, means, mins, maxs)))
speedup = [means[0] / mean for mean in means]
min_speedup = [means[0] / max for max in maxs]
max_speedup = [means[0] / min for min in mins]
ideal_speedup = [cpu_count for cpu_count in cpu_counts]

# use tex
#plt.rc('text', usetex=True)
#plt.rc('font', family='serif')
# Create a subplot
fig, ax1 = plt.subplots()

# Plot runtime
color = 'tab:blue'
ax1.set_xlabel('#cores')
ax1.set_ylabel('Runtime [s]', color=color)
line1 = ax1.plot(cores, means, color=color, label="mean runtime")
fill1 = ax1.fill_between(cores, mins, maxs, color=color, alpha=0.2)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
color = 'tab:red'
ax2.set_ylabel('Speedup', color=color)
line2 = ax2.plot(cores, speedup, color=color, label="mean speedup")
line3 = ax2.plot(cores, ideal_speedup, color='black', linestyle='--', label="ideal speedup") # ideal speedup line
fill2 = ax2.fill_between(cores, min_speedup, max_speedup, color=color, alpha=0.2)
ax2.tick_params(axis='y', labelcolor=color)

plt.title(f"Runtime and strong scaling of iPI")

# Collect lines and labels for the legend
lines = line1 + line2 + line3
labels = [l.get_label() for l in lines]
# legend small and centered
fig.legend(lines, labels, loc='upper center', bbox_to_anchor=(0.5, 0.92), ncol=3, fontsize='small')
fig.tight_layout()
slurm_id = os.path.basename(os.path.normpath(main_dir))
# save to parent directory of main_dir
path = os.path.dirname(main_dir)
plt.savefig(os.path.join(path, f'strong_scaling_{slurm_id}.png'), dpi=300)
print(f"Plot saved to {os.path.join(path, f'strong_scaling_{slurm_id}.png')}")

# plt.savefig(os.path.join(main_dir, f'strong_scaling_{slurm_id}.png'), dpi=300)
# print(f"Plot saved to {os.path.join(main_dir, f'strong_scaling_{slurm_id}.png')}")
