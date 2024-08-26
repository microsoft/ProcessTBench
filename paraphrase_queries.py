import my_model
from utils import *
import json
from pprint import pprint
import pandas as pd
import multiprocessing
import pandas as pd
import pickle

def rephrase(data,tools):
    system = """Your task is to create more variants of a given user query, aiming at approximating many ways to explain the task to a model ... Here's what you should do step-by-step: 
(1) Understand and explain the given user query and how it aligns with the REQUIREMENTS_FOR_THE_USER_QUERY_AND_TASK_STEPS, TOOL_GRAPH_NODES, TOOL_GRAPH_EDGES, and TASK_STEPS...
(2) Highlight the linking words in the given user query which ensure that the solution of the query aligns with the dependencies described by the tool graph edges ... 
(3) Give examples for how different people could construct the query, the different ways they could order the items in the query, and some different linking words they could use... 
(4) Structure some user query variants based on your previous observations, including two last variants in the Danish and the French language ... 

Then output your thoughts and the user_query_variants in the following JSON_OUTPUT format: {"user_query_step_by_step_decomposition": <string: your output for points (1), (2), (3) and (4)>, "user_query_variants": <list of strings: the list of your user request variants>}. 

REQUIREMENTS_FOR_THE_USER_QUERY_AND_TASK_STEPS:
###
Based on the above tool graph, please be skillful to generate the according task steps and user request.
Requirements: 
1. the generated user request should be somewhat clear, self-contained (user-specified text, image, video, audio, content should be contained in the request) and practical (help users solve a practical problem); 
2. the task steps must be strictly aligned with the tool graph (nodes and edges) and reasonable; 
3. the user request just can be decomposed into task steps solved which are aligned with the tool graph; 
4. each task step corresponds to a tool node in the tool graph, and the number of task steps must be same with the nodes. Each tool node can only be used once; 
5. if need image/audio/video resources in user request, please use files 'example.[jpg/mp4/wav/png]'; 
6. the dependencies among task steps must align with the edges of tool graph;
###
"""
    tool_list = [x['task'] for x in data['sampled_nodes']]
    tool_edge = [[x['source'], x['target']] for x in data['sampled_links']]

    sampled_tools_string = "Given a tool graph with tools as nodes, and invoking chains between tools as edges. The following tools (nodes) are available with their corresponding descriptions and input/outputs types:\n"
    for k, tool in enumerate(tool_list):
        sampled_tools_string += f"Node {k+1}:" + json.dumps(tools[tool]) + "\n"

    sampled_links_string = "These tools can be connected as follows (the directed edges are invoking chains among tools):\n"
    for k, edge in enumerate(tool_edge):
        sampled_links_string += f"Edge: " + edge[0] + " -> " + edge[1] + "\n"

    content = f"""TOOL_GRAPH_NODES:
###
{sampled_tools_string}
###
TOOL_GRAPH_EDGES:
###
{sampled_links_string}
###
USER_QUERY:
###
{data['user_request']}
###
TASK_STEPS:
###
{data['task_steps']}
###
"""
    messages = [{'role': 'system', 'content': system},
                {'role': 'user', 'content': content}]
    result = my_model.get_completion_robust(messages)
    return result

def process_partition(selected_partition):
    with open('tool_desc_multimedia.json') as f:
        tools = json.load(f)['nodes']
    tools = {x['id']: x for x in tools}

    df_data_multimedia = pd.read_json('taskbench_multimedia_dag_partitioned.json', lines=True)
    df_data_multimedia = df_data_multimedia[df_data_multimedia['partition'] == selected_partition]

    # Initialize or load saved data
    try:
        with open(f'rephrasings/saved_data_{selected_partition}.pkl', 'rb') as f:
            saved_data = pickle.load(f)
            planning_results = saved_data['planning_results']
    except (FileNotFoundError, EOFError):
        planning_results = {}

    for _, row in df_data_multimedia.iterrows():
        uid = row['id']

        # Skip if this uid has been processed
        if uid in planning_results:
            continue

        result = rephrase(row, tools)
        planning_results[uid] = result

        # Save data after each iteration
        with open(f'rephrasings/saved_data_{selected_partition}.pkl', 'wb') as f:
            pickle.dump({
                'planning_results': planning_results,
            }, f)

        print(f"Finished processing {uid} in partition {selected_partition}")

    return planning_results

if __name__ == '__main__':

    # Get the number of partitions in your dataset
    num_partitions = 30  # replace with the actual number of partitions

    # Create a pool of workers
    with multiprocessing.Pool(processes=4) as pool:
        # Process each partition in parallel
        results = pool.map(process_partition, range(num_partitions))

    # Print the results
    for i, planning_results in enumerate(results):
        print(f"Results for partition {i}:")
        pprint(planning_results)