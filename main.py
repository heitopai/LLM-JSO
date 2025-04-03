import llm
import decoder
import random
import os


def generate_meta_prompt(history_sol, n, m, OM, OT):

    prompt = f"""You are given {n} jobs and {m} machines. Each job consists of {m} operations that must be processed in a predefined sequence on designated machines with given processing times:\n"""
    for i in range(n):
        sequence = " → ".join(f"{OM[i][j]}" for j in range(m))
        times = ", ".join(str(OT[i][j]) for j in range(m))
        prompt += f"Job {i} follows the machine sequence {sequence} with processing times {times}.\n"

    prompt += """Below are some previous operation-based representations of schedules and their makespan values. The representations are arranged in descending order of makespan, where smaller values indicate better performance.\n\n"""
    history_sol.sort(key=lambda x: decoder.decode(n, m, OM, OT, x)[1], reverse=True)
    for sol in history_sol:
        schedule, makespan = decoder.decode(n, m, OM, OT, sol)
        prompt += "<rep> " + str(sol).replace("[", "").replace("]", "") + " </rep>\n"
        prompt += "makespan: \n"
        prompt += str(makespan) + "\n\n"

    prompt += f"""Try to find a new representation such that its makespan is smaller than all of the above. The representation must satisfy the following conditions:\n"""
    prompt += """1. It must be different from all representations above. \n"""
    prompt += """2. It must start with <rep> and end with </rep>. \n"""
    prompt += f"""3. It must contain {n*m} numbers in total, with each job number appearing exactly {m} times.\n"""

    prompt += """Do not write code."""
    # print(prompt)
    return prompt

def check_validity(new_representation, n, m):
    if len(new_representation) != n*m:
        return -1
    for i in range(n):
        cnt=new_representation.count(i)
        if cnt != m:
            # print(i, new_representation.count(i))
            return (i, cnt)
    return -2

import re
def parse_response(response):
    try:
        match = re.search(r"<rep>(.*?)</rep>", response, re.DOTALL)
        if match:
            return list(map(int, match.group(1).strip().split(',')))
        return None
    except:
        return None

import ast
def optimize(data_file, iterations, model_name, temperature, output_dir):
    n, m, OM, OT = decoder.read_file(data_file)
    
    history_sol = []
    for _ in range(5):
        operation_list=[num for num in range(n) for _ in range(m)]
        random.shuffle(operation_list)
        history_sol.append(operation_list)

    wrong_return = 0
    no_valid = 0
    history_count = 0
    valid_update = 0
    update = []

    conversation_history = []
    meta_prompt = generate_meta_prompt(history_sol, n, m, OM, OT)
    conversation_history.append({
        "role": "user",
        "content": meta_prompt
    })
    pre = decoder.decode(n, m, OM, OT, history_sol[-1])[1]
    best_sol = history_sol[-1]

    change=[]
    # temperature=0.5
    for _ in range(iterations):
        print("Iteration: ", _)
        response = llm.call_llm(conversation_history, model_name, temperature)
        # print(response)

        new_representation = parse_response(response)
        if new_representation is None:
            conversation_history.append({
                "role": "user",
                # "content": """You return other characters besides a representation! You must return only a representation that starts with [ and end with ]!"""
                "content": "Please try again."
            })
            wrong_return += 1

            continue


        info=check_validity(new_representation, n, m)
        if info != -2:
            if info == -1:
                conversation_history.append({
                    "role": "user",
                    # "content": f"""This representation has {len(new_representation)} numbers in total, but it must has {n*m} numbers in total!\nYou do not need to return the analysis! Return only a representation without any other characters!"""
                    "content": f"The representation you returned contains {len(new_representation)} numbers in total."
                })
                no_valid += 1

                continue
            else:
                conversation_history.append({
                    "role": "user",
                    # "content": f"""Job number {info} does not appears exactly {m} times in this representation!\nYou do not need to return the analysis! Return only a representation without any other characters!"""
                    "content": f"Job number {info[0]} appears {info[1]} times in the representation."
                })
                no_valid += 1

                continue

        if new_representation in history_sol:
            conversation_history.append({
                "role": "user",
                # "content": """This representation has already appeared above! \nYou do not need to return the analysis! Return only a representation without any other characters!"""
                "content": "The representation you returned has already appeared above. "
            })
            history_count += 1

            continue
        history_sol.append(new_representation)
        cur = decoder.decode(n, m, OM, OT, new_representation)[1]
        change.append(cur)
        if cur < pre:
            conversation_history.append({
                "role": "user",
                # "content": f"""Great! The makespan of this representation is {cur}, which is lower than the lowest {pre} above. Give me a new representation again. You do not need to return the analysis! Return only a representation without any other characters!"""
                "content": f"Great! The makespan of this representation is {cur}, which is smaller than the previous minimum of {pre}. Give me a new representation again."
            })       

            valid_update += 1
            update.append(f"{pre} -> {cur}")
            pre = cur
            best_sol = new_representation

        else:
            if cur == pre:
                conversation_history.append({
                    "role": "user",
                    # "content": f"""The makespan of this representation is {cur}, which is equal to the lowest {pre} above. \nYou do not need to return the analysis! Return only a representation without any other characters!"""
                    "content": f"The makespan of this representation is {cur}, which is equal to the previous minimum of {pre}."
                })
            else:
                conversation_history.append({
                    "role": "user",
                    # "content": f"""The makespan of this representation is {cur}, which is higher than or equal to the lowest {pre} above. \nYou do not need to return the analysis! Return only a representation without any other characters!"""
                    "content": f"The makespan of this representation is {cur}, which is larger than the previous minimum of {pre}."
                })


    schedule, makespan = decoder.decode(n, m, OM, OT, best_sol)


    os.makedirs(output_dir, exist_ok=True)

    with open(output_dir + f"/{os.path.basename(data_file)}", "w", encoding='utf-8') as f:
        f.write(f"Makespan: {makespan}\n") 
        f.write(f"wrong return: {wrong_return}\n")
        f.write(f"no valid: {no_valid}\n")
        f.write(f"history count: {history_count}\n")
        f.write(f"valid update: {valid_update}\n")
        f.write("Change: \n")
        f.write(str(change) + "\n")
        f.write("Update: \n")
        f.write(str(update) + "\n")
        f.write("Best solution: \n")
        f.write(str(best_sol) + "\n")
        f.write("Conversation history: \n")
        for entry in conversation_history:
            f.write(f"{entry['role']}: {entry['content']}\n")
    # decoder.plot_gantt(schedule, list(range(m)), dir + f"/{data_file}.jpg")


