import os
dir1 = "./gemini-2.0-flash-lite_results_20250624170318/"
dir2 = "./gemini-2.0-flash-lite_results_20250624224014/"
dir3 = "./gemini-2.0-flash-lite_results_20250624224038/"
def run(dir):
    files = os.listdir(dir)
    res = {}
    # data = {}
    for file in files:
        data = {}  
        with open(dir + file, 'r', encoding = "utf8") as f:
            for line in f:
                if "Makespan" in line:
                    makespan = float(line.split(":")[1].strip())
                    # print(f"{file}: {makespan}")
                    data["Makespan"] = makespan
                if "Change" in line:
                    # print(line)
                    next_line = next(f, "").strip()
                    next_line = eval(next_line)
                    # print(f"{file}: {len(next_line)}")
                    data["Valid Representations"] = len(next_line)
                    break
        res[file] = data
    # print(res)
    return res

if __name__ == "__main__":
    res1 = run(dir1)
    res2 = run(dir2)
    res3 = run(dir3)
    # Compare same files across directories
    common_files = set(res1.keys()) & set(res2.keys()) & set(res3.keys())
    
    for file in sorted(common_files):
        m1, m2, m3 = res1[file]["Makespan"], res2[file]["Makespan"], res3[file]["Makespan"]
        v1, v2, v3 = res1[file]["Valid Representations"], res2[file]["Valid Representations"], res3[file]["Valid Representations"]
        
        makespans = [m1, m2, m3]
        valid_reps = [v1, v2, v3]
        
        print(f"\n{file}:")
        print(f"  Makespan: Min={min(makespans):.2f}, Max={max(makespans):.2f}, Avg={sum(makespans)/3:.2f}")
        print(f"  Valid Reps: Min={min(valid_reps)}, Max={max(valid_reps)}, Avg={sum(valid_reps)/3:.2f}")
