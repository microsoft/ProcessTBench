from . import my_model
from utils import demo_messages_full
import json
from pprint import pprint
import multiprocessing
import pandas as pd
import pickle

def plan_single(user_req, demo_messages, llm, tools):
    system = """# GOAL #: Based on the above tools, I want you to generate a sequence of task steps to solve the # USER REQUEST #. The format must in a strict JSON format, like: 
{
    "tool_name1: tool name must be from # TOOL LIST #": {
        "arguments": [ a concise list of arguments for the tool. Either original text, or user-mentioned filename, or tag '<tool_name>' to refer to the output of the tool yielded in a previous step. ]
    },
    "tool_name2: tool name must be from # TOOL LIST #": {
        "arguments": [ a concise list of arguments for the tool. Either original text, or user-mentioned filename, or tag '<tool_name>' to refer to the output of the tool yielded in a previous step. ]
    },
    ...
}

# REQUIREMENTS #: 
1. the generated sequence of task steps can resolve the given user request # USER REQUEST # perfectly. Tool name must be selected from the given # TOOL LIST #; 
2. the sequence of task steps should strictly align with the # TOOL LIST #, and the number of task steps should be same with the tools in # TOOL LIST #; 
3. the generated sequence of task steps are given in the order they should be executed, and should align with the argument dependencies of the tools in # TOOL LIST #, and with the  # USER REQUEST #; 
4. the task step arguments should be aligned with the input-type field of tools in # TOOL LIST #;
5. pay attention that the intra task step argument dependencies are fulfilled. E.g. if task_stepA has arguments: [<'task_stepB'>, <'task_stepC'>], then task_stepB and task_stepC should be generated before task_stepA;
6. when the user will ask for the generation of more valid task steps, resolve the given user request # USER REQUEST # perfectly, generate more sequences of steps such that the new task steps also fulfill strictly all the requirements # REQUIREMENTS # given above. Pay attention to the order of the task steps, and the argument dependencies of the tools in # TOOL LIST #. """
    messages = [
        {"role": "system", "content": system},
    ]
    messages += demo_messages
    messages += [
        {"role": "user", "content": f"# TOOL LIST #: {tools} \n # USER REQUEST #: {user_req}"}
    ]
    plan1 = llm.get_completion_robust(messages, model='gpt-4-32k')
    result = json.loads(f"[{plan1}]")

    return result

def process_partition(selected_partition):
    df_data_multimedia = pd.read_json('taskbench_multimedia_dag_partitioned.json', lines=True)
    df_data_multimedia = df_data_multimedia[df_data_multimedia['partition'] == selected_partition]
    with open('x2_rephrasing/rephrasing_results_indexed.json') as f:
        rephrasing_results = json.load(f)
    with open('tool_desc_multimedia.json') as f:
                tools = json.load(f)
                tools = json.dumps(tools)
    try:
        with open(f'x2_planner_rephrased/saved_data_{selected_partition}.pkl', 'rb') as f:
            saved_data = pickle.load(f)
            planning_results = saved_data['planning_results']
    except (FileNotFoundError, EOFError):
        planning_results = {}
    
    for _, row in df_data_multimedia.iterrows():
        uid = str(row['id'])
        
        for rid, rephrasing in rephrasing_results[uid]['user_query_variants'].items():
            if uid in planning_results and rid in planning_results[uid]: # Skip if this uid has been processed
                continue
            result = plan_single(rephrasing, demo_messages_full, my_model, tools)
            if uid not in planning_results:
                planning_results[uid] = {}
            planning_results[uid][rid] = result
            print(f"Finishhed with uid {uid} and rid {rid}, in partition {selected_partition}")
            # Save data after each iteration
            with open(f'x2_planner_rephrased/saved_data_{selected_partition}.pkl', 'wb') as f:
                pickle.dump({
                    'planning_results': planning_results,
                }, f)

    return planning_results

if __name__ == '__main__':
    num_partitions = 30
    with multiprocessing.Pool(processes=8) as pool:
        results = pool.map(process_partition, range(num_partitions))

    for i, planning_results in enumerate(results):
        print(f"Results for partition {i}:")
        pprint(planning_results)