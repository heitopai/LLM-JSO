def read_file(file_path):
    OM = []
    OT = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        n, m = map(int, lines[0].strip().split())
        for line in lines[1:]:
            values = list(map(int, line.strip().split()))
            OM.append(values[::2])
            OT.append(values[1::2])
    return n, m, OM, OT

# def decode(n,m,OM,OT,operation_list):

#     occurrence={}
#     job_op=[]
#     for i in operation_list:
#         tmp=occurrence.get(i,0)
#         job_op.append((i,tmp))
#         occurrence[i]=tmp+1

#     job_last_end_time=[0]*n
#     machine_end_time=[0]*m
#     schedule={}
#     for job,op in job_op:
#         machine=OM[job][op]
#         duration=OT[job][op]

#         start_time=max(job_last_end_time[job],machine_end_time[machine])
#         end_time=start_time+duration

#         job_last_end_time[job]=end_time
#         machine_end_time[machine]=end_time

#         schedule[(job,op)]={
#             "machine":machine,
#             "start":start_time,
#             "end":end_time
#         }

#     makespan = max(info['end'] for info in schedule.values())
#     return schedule, makespan

def find_earliest_slot(machine_intervals, machine, duration, earliest_start):
        """
        在机器的空闲时间段中，找到满足 `earliest_start` 约束的最早插入位置
        """
        if not machine_intervals[machine]:  # 机器无任务，从 earliest_start 开始
            return earliest_start
        
        intervals = machine_intervals[machine]
        
        # 1. 检查 earliest_start 是否能放置任务
        if intervals[0][0] >= earliest_start + duration:
            return earliest_start

        # 2. 遍历空闲区间，找一个可插入的时间片
        for i in range(len(intervals) - 1):
            prev_end = max(intervals[i][1], earliest_start)
            next_start = intervals[i + 1][0]

            if next_start - prev_end >= duration:
                return prev_end

        # 3. 不能插入，则安排到最后
        return max(intervals[-1][1], earliest_start)

import heapq
def decode(n,m,OM,OT,operation_list):
    occurrence={}
    job_op=[]
    for i in operation_list:
        tmp=occurrence.get(i,0)
        job_op.append((i,tmp))
        occurrence[i]=tmp+1

    machine_intervals={i:[] for i in range(m)}
    job_completion = [0] * n
    schedule={}
    for job,op in job_op:
        machine=OM[job][op]
        duration=OT[job][op]
        
        job_prev_end = job_completion[job]  # 该工作前一个操作的完成时间
        
        # 找到最早可插入的时间
        start_time = find_earliest_slot(machine_intervals,machine, duration, job_prev_end)
        end_time = start_time + duration

        schedule[(job,op)]={
            "machine":machine,
            "start":start_time,
            "end":end_time
        }

        # 更新机器调度
        machine_intervals[machine].append((start_time, end_time))
        machine_intervals[machine].sort()

        # 更新工作完成时间
        job_completion[job] = end_time

    makespan = max(info['end'] for info in schedule.values())
    return schedule, makespan

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import cm

def plot_gantt(schedule, machines, results_path):
    """
    Plot the Gantt chart for the schedule.
    :param schedule: Schedule dictionary, format {(job ID, operation number): {'machine': machine ID, 'start': start time, 'end': end time}}
    :param machines: List of machine IDs (defines Y-axis display order)
    """
    # Initialize the plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Color configuration
    unique_jobs = list({op[0] for op in schedule.keys()})  # Get all job IDs
    color_map = cm.get_cmap('Set1', len(unique_jobs))     # Use Set1 color scheme for higher distinguishability
    job_colors = {job: color_map(i) for i, job in enumerate(unique_jobs)}
    
    # Y-axis settings (machine position mapping)
    y_ticks = {machine: idx for idx, machine in enumerate(machines)}
    plt.yticks(range(len(machines)), machines)
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("Machine", fontsize=12)
    # plt.title("Job Shop Scheduling Gantt Chart", fontsize=14, pad=20)
    
    # Plot each operation bar
    for op, details in schedule.items():
        job_id, step = op
        machine_id = details['machine']
        start = details['start']
        end = details['end']
        
        # Create rectangle bar (position: X-axis start time, Y-axis machine position)
        rect = patches.Rectangle(
            (start, y_ticks[machine_id] - 0.4),   # Bottom-left corner coordinates (x, y)
            width = end - start,                  # Width (processing time)
            height = 0.8,                         # Height (machine bar height)
            facecolor = job_colors[job_id],
            edgecolor = 'black',
            alpha = 0.8,
            label = f'J$_{job_id}$'
        )
        ax.add_patch(rect)
        
        # Set background color for the plot
        ax.set_facecolor('#e6f7ff')

        # Add operation text (centered display)
        ax.text(
            x = (start + end) / 2,                # X-axis centered
            y = y_ticks[machine_id],              # Y-axis centered
            s = f'J$_{job_id}$-O$_{step}$\n{end-start}',# Display job-operation and processing time
            ha = 'center', va = 'center',
            fontsize = 8
        )
    
    # Draw a vertical line for makespan
    makespan = max(details['end'] for details in schedule.values())
    plt.axvline(x=makespan, color='red', linestyle='--', linewidth=1.5)
    
    # Annotate makespan value
    plt.text(
        x=makespan, y=-0.5, 
        s=f'Makespan: {makespan}', 
        color='red', fontsize=10, 
        ha='center', va='top'
    )

    # Handle legend (remove duplicates)
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))  # Remove duplicates
    plt.legend(
        by_label.values(), by_label.keys(),
        loc='upper right', 
        title="Jobs", 
        bbox_to_anchor=(1.15, 1)
    )
    
    # Set axis range
    max_time = max(details['end'] for details in schedule.values())
    plt.xlim(0, max_time * 1.05)
    plt.ylim(-0.5, len(machines) - 0.5)
    
    # Adjust layout automatically
    plt.tight_layout()
    # plt.show()
    plt.savefig(results_path)