# utils.py contains utility functions for the project

from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.objects.process_tree.obj import Operator
import networkx as nx
import queue
import matplotlib.pyplot as plt
import ndjson
import json
from pm4py.objects.powl.obj import StrictPartialOrder, Transition

class ExtendedProcessTree(ProcessTree):
    def __init__(self, operator=None, parent=None, children=None, label=None, graph=None):
        super().__init__(operator, parent, children, label)
        self.graph = graph
        
    def l(self, label):
        self._set_label(label)
        return self

    def s(self, children: list):
        if self.is_tau():
            self.operator = Operator.SEQUENCE
            self._children = children
        elif self.operator == Operator.SEQUENCE:
            self._children += children
        else:
            child = ExtendedProcessTree(operator=Operator.SEQUENCE)
            child._set_parent(self)
            child._children = children
            self._children.append(child)
            map(lambda c: c._set_parent(child), child._children)
        map(lambda c: c._set_parent(self), self._children)
        return self

    def p(self, children: list):
        if self.is_tau():
            self.operator = Operator.PARALLEL
            self._children = children
        elif self.operator == Operator.PARALLEL:
            self._children += children
        else:
            child = ExtendedProcessTree(operator=Operator.PARALLEL)
            child._set_parent(self)
            child._children = children
            self._children.append(child)
            map(lambda c: c._set_parent(child), child._children)
        map(lambda c: c._set_parent(self), self._children)
        return self
    
    def expand(self, expand_queue):
        def find_directed_cut(graph):

            def split_graph(graph, node, direction):
                
                def get_crossing_nodes(crossing_edges):
                    out_crossing = [edge[0] for edge in crossing_edges]
                    in_crossing = [edge[1] for edge in crossing_edges]
                    return out_crossing, in_crossing
                
                graph_copy = graph.copy()
                if direction == "in":
                    crossing_edges = list(graph_copy.in_edges(node))
                elif direction == "out":
                    crossing_edges = list(graph_copy.out_edges(node))
                out_crossing, in_crossing = get_crossing_nodes(crossing_edges)
                graph_copy.remove_edges_from(crossing_edges)
                components = list(nx.weakly_connected_components(graph_copy))
                # if a node is in a component containing a in or out crossing node, it is in the cut
                in_subgraph = graph_copy.subgraph([node for component in components if any(node in component for node in in_crossing) for node in component]).copy()
                out_subgraph = graph_copy.subgraph([node for component in components if any(node in component for node in out_crossing) for node in component]).copy()
                return out_subgraph, in_subgraph
            
            source = [node for node, deg in graph.in_degree() if deg == 0][0]
            bfs_edges = list(nx.bfs_edges(graph, source))
            bfs_nodes = [source] + [v for u, v in bfs_edges]
            for node in bfs_nodes:
                if graph.in_degree(node) > 1:
                    cut1, cut2 = split_graph(graph, node, "in")
                    return cut1, cut2
                elif graph.out_degree(node) > 1:
                    cut1, cut2 = split_graph(graph, node, "out")
                    return cut1, cut2
            for node in bfs_nodes:
                if graph.out_degree(node) > 0:
                    cut1, cut2 = split_graph(graph, node, "out")
                    return cut1, cut2
                
        num_nodes = self.graph.number_of_nodes()
        if num_nodes == 1:  # graph with one node
            self.l(list(self.graph.nodes)[0])
        elif num_nodes > 0:  # graph with multiple nodes
            if not nx.is_connected(self.graph.to_undirected()): # Parallel cut
                components = [self.graph.subgraph(c).copy() for c in nx.connected_components(self.graph.to_undirected())]
                parallel_children = list(map(lambda component: ExtendedProcessTree(graph=component), components))
                for child in parallel_children:
                    expand_queue.put(child)
                self.p(parallel_children)
            else:  # Sequence cut
                # Find directed cut finds first advanced sequence cut, if not found, finds first basic sequence cut
                cut1, cut2 = find_directed_cut(self.graph)
                sequence_children = [ExtendedProcessTree(graph=cut) for cut in [cut1, cut2]]
                for child in sequence_children:
                    expand_queue.put(child)
                self.s(sequence_children)

    def convert(self, graph):
        tree = ExtendedProcessTree(graph=graph)
        expand_queue = queue.Queue()
        expand_queue.put(tree)
        while not expand_queue.empty():
            current_tree_node = expand_queue.get()
            current_tree_node.expand(expand_queue)
        return tree
    
    def is_tau(self):
        return self.label == None and self.operator == None
    
    def count_shortest_path(self):
        match self.operator:
            case Operator.SEQUENCE:
                return sum([child.count_shortest_path() for child in self._children])
            case Operator.PARALLEL:
                return max([child.count_shortest_path() for child in self._children])
            case None:
                return 1
    
def create_powl_model(data):
    '''
    usage: create_powl_model(data); nt, im, fm = pm4py.convert_to_petri_net(powl)
    '''
    nodes = {}
    for node in data['sampled_nodes']:
        nodes[node['task']] = Transition(label=node['task'])

    powl_model = StrictPartialOrder(nodes=nodes.values())
    for edge in data['sampled_links']:
        powl_model.order.add_edge(nodes[edge['source']], nodes[edge['target']])
    
    return powl_model

with open('taskbench_multimedia.json') as f:
    data_multimedia = ndjson.load(f)
    data_multimedia = [x for x in data_multimedia if x['type'] == 'dag']

demo_data_multimedia_0 = """{
    "Video-to-Audio": {
        "arguments": ["example.mp4"]
    },
    "Audio Splicer": {
        "arguments": ["<Video-to-Audio>", "example.wav"]
    },
    "Audio Effects": {
        "arguments": ["<Audio Splicer>", "add reverb"]
    },
    "Audio-to-Text": {
        "arguments": ["<Audio Splicer>"]
    },
    "Audio-to-Image": {
        "arguments": ["<Audio Effects>"]
    }
}"""

demo_data_multimedia_0b = """{
    "Video-to-Audio": {
        "arguments": ["example.mp4"]
    },
    "Audio Splicer": {
        "arguments": ["<Video-to-Audio>", "example.wav"]
    },
    "Audio-to-Text": {
        "arguments": ["<Audio Splicer>"]
    },
    "Audio Effects": {
        "arguments": ["<Audio Splicer>", "add reverb"]
    },
    "Audio-to-Image": {
        "arguments": ["<Audio Effects>"]
    }
},
{
    "Video-to-Audio": {
        "arguments": ["example.mp4"]
    },
    "Audio Splicer": {
        "arguments": ["<Video-to-Audio>", "example.wav"]
    },
    "Audio Effects": {
        "arguments": ["<Audio Splicer>", "add reverb"]
    },
    "Audio-to-Image": {
        "arguments": ["<Audio Effects>"]
    },
    "Audio-to-Text": {
        "arguments": ["<Audio Splicer>"]
    }
}"""

demo_data_multimedia_1 = """{
    "Voice Changer": {
        "arguments": ["example.wav", "female"]
    },
    "Audio-to-Image": {
        "arguments": ["<Voice Changer>"]
    },
    "Audio Noise Reduction": {
        "arguments": ["<Voice Changer>"]
    },
    "Image-to-Video": {
        "arguments": ["<Audio-to-Image>", "example.jpg"]
    }
}"""

demo_data_multimedia_1b = """{
    "Voice Changer": {
        "arguments": ["example.wav", "female"]
    },
    "Audio Noise Reduction": {
        "arguments": ["<Voice Changer>"]
    },
    "Audio-to-Image": {
        "arguments": ["<Voice Changer>"]
    },
    "Image-to-Video": {
        "arguments": ["<Audio-to-Image>", "example.jpg"]
    }
},
{
    "Voice Changer": {
        "arguments": ["example.wav", "female"]
    },
    "Audio-to-Image": {
        "arguments": ["<Voice Changer>"]
    },
    "Image-to-Video": {
        "arguments": ["<Audio-to-Image>", "example.jpg"]
    },
    "Audio Noise Reduction": {
        "arguments": ["<Voice Changer>"]
    }
}"""

demo_data_multimedia_2 = """{
    "Video Speed Changer": {
        "arguments": ["example.mp4", "adjust speed"]
    },
    "Video-to-Image": {
        "arguments": ["<Video Speed Changer>"]
    },
    "Image Colorizer": {
        "arguments": ["<Video-to-Image>"]
    },
    "Article Spinner": {
        "arguments": ["Example Article"]
    },
    "Text Summarizer": {
        "arguments": ["<Article Spinner>"]
    },
    "Text-to-Image": {
        "arguments": ["<Text Summarizer>"]
    }
}"""
demo_data_multimedia_2b = """{
    "Article Spinner": {
        "arguments": ["Example Article"]
    },
    "Text Summarizer": {
        "arguments": ["<Article Spinner>"]
    },
    "Text-to-Image": {
        "arguments": ["<Text Summarizer>"]
    },
    "Video Speed Changer": {
        "arguments": ["example.mp4", "adjust speed"]
    },
    "Video-to-Image": {
        "arguments": ["<Video Speed Changer>"]
    },
    "Image Colorizer": {
        "arguments": ["<Video-to-Image>"]
    }
},
{
    "Video Speed Changer": {
        "arguments": ["example.mp4", "adjust speed"]
    },
    "Article Spinner": {
        "arguments": ["Example Article"]
    },
    "Text Summarizer": {
        "arguments": ["<Article Spinner>"]
    },
    "Video-to-Image": {
        "arguments": ["<Video Speed Changer>"]
    },
    "Image Colorizer": {
        "arguments": ["<Video-to-Image>"]
    },
    "Text-to-Image": {
        "arguments": ["<Text Summarizer>"]
    }
},
{
    "Article Spinner": {
        "arguments": ["Example Article"]
    },
    "Text Summarizer": {
        "arguments": ["<Article Spinner>"]
    },
    "Text-to-Image": {
        "arguments": ["<Text Summarizer>"]
    },
    "Video Speed Changer": {
        "arguments": ["example.mp4", "adjust speed"]
    },
    "Video-to-Image": {
        "arguments": ["<Video Speed Changer>"]
    },
    "Image Colorizer": {
        "arguments": ["<Video-to-Image>"]
    }
},
{
    "Article Spinner": {
        "arguments": ["Example Article"]
    },
    "Text Summarizer": {
        "arguments": ["<Article Spinner>"]
    },
    "Video Speed Changer": {
        "arguments": ["example.mp4", "adjust speed"]
    },
    "Text-to-Image": {
        "arguments": ["<Text Summarizer>"]
    },
    "Video-to-Image": {
        "arguments": ["<Video Speed Changer>"]
    },
    "Image Colorizer": {
        "arguments": ["<Video-to-Image>"]
    }
},
{
    "Video Speed Changer": {
        "arguments": ["example.mp4", "adjust speed"]
    },
    "Video-to-Image": {
        "arguments": ["<Video Speed Changer>"]
    },
    "Article Spinner": {
        "arguments": ["Example Article"]
    },
    "Text Summarizer": {
        "arguments": ["<Article Spinner>"]
    },
    "Image Colorizer": {
        "arguments": ["<Video-to-Image>"]
    },
    "Text-to-Image": {
        "arguments": ["<Text Summarizer>"]
    }
},
{
    "Video Speed Changer": {
        "arguments": ["example.mp4", "adjust speed"]
    },
    "Video-to-Image": {
        "arguments": ["<Video Speed Changer>"]
    },
    "Article Spinner": {
        "arguments": ["Example Article"]
    },
    "Text Summarizer": {
        "arguments": ["<Article Spinner>"]
    },
    "Text-to-Image": {
        "arguments": ["<Text Summarizer>"]
    },
    "Image Colorizer": {
        "arguments": ["<Video-to-Image>"]
    }
},
{
    "Article Spinner": {
        "arguments": ["Example Article"]
    },
    "Text Summarizer": {
        "arguments": ["<Article Spinner>"]
    },
    "Video Speed Changer": {
        "arguments": ["example.mp4", "adjust speed"]
    },
    "Video-to-Image": {
        "arguments": ["<Video Speed Changer>"]
    },
    "Text-to-Image": {
        "arguments": ["<Text Summarizer>"]
    },
    "Image Colorizer": {
        "arguments": ["<Video-to-Image>"]
    }
},
{
    "Article Spinner": {
        "arguments": ["Example Article"]
    },
    "Video Speed Changer": {
        "arguments": ["example.mp4", "adjust speed"]
    },
    "Video-to-Image": {
        "arguments": ["<Video Speed Changer>"]
    },
    "Image Colorizer": {
        "arguments": ["<Video-to-Image>"]
    },
    "Text Summarizer": {
        "arguments": ["<Article Spinner>"]
    },
    "Text-to-Image": {
        "arguments": ["<Text Summarizer>"]
    }
}"""

demo_data_multimedia_0_reasoning = """# TASK DEPENDENCIES #:
Video-to-Audio -> Audio Splicer
Audio Splicer -> Audio-to-Text
Audio Splicer -> Audio Effects
Audio Effects -> Audio-to-Image

# TASK STEPS #:
{
    "Video-to-Audio": {
        "arguments": ["example.mp4"]
    },
    "Audio Splicer": {
        "arguments": ["<Video-to-Audio>", "example.wav"]
    },
    "Audio Effects": {
        "arguments": ["<Audio Splicer>", "add reverb"]
    },
    "Audio-to-Text": {
        "arguments": ["<Audio Splicer>"]
    },
    "Audio-to-Image": {
        "arguments": ["<Audio Effects>"]
    }
}"""

demo_data_multimedia_0b_reasoning = """{
    "Video-to-Audio": {
        "arguments": ["example.mp4"]
    },
    "Audio Splicer": {
        "arguments": ["<Video-to-Audio>", "example.wav"]
    },
    "Audio-to-Text": {
        "arguments": ["<Audio Splicer>"]
    },
    "Audio Effects": {
        "arguments": ["<Audio Splicer>", "add reverb"]
    },
    "Audio-to-Image": {
        "arguments": ["<Audio Effects>"]
    }
},
{
    "Video-to-Audio": {
        "arguments": ["example.mp4"]
    },
    "Audio Splicer": {
        "arguments": ["<Video-to-Audio>", "example.wav"]
    },
    "Audio Effects": {
        "arguments": ["<Audio Splicer>", "add reverb"]
    },
    "Audio-to-Image": {
        "arguments": ["<Audio Effects>"]
    },
    "Audio-to-Text": {
        "arguments": ["<Audio Splicer>"]
    }
}"""

demo_data_multimedia_1_reasoning = """# TASK DEPENDENCIES #:
Voice Changer -> Audio-to-Image
Voice Changer -> Audio Noise Reduction
Audio-to-Image -> Image-to-Video

# TASK STEPS #:
{
    "Voice Changer": {
        "arguments": ["example.wav", "female"]
    },
    "Audio-to-Image": {
        "arguments": ["<Voice Changer>"]
    },
    "Audio Noise Reduction": {
        "arguments": ["<Voice Changer>"]
    },
    "Image-to-Video": {
        "arguments": ["<Audio-to-Image>", "example.jpg"]
    }
}"""

demo_data_multimedia_1b_reasoning = """{
    "Voice Changer": {
        "arguments": ["example.wav", "female"]
    },
    "Audio Noise Reduction": {
        "arguments": ["<Voice Changer>"]
    },
    "Audio-to-Image": {
        "arguments": ["<Voice Changer>"]
    },
    "Image-to-Video": {
        "arguments": ["<Audio-to-Image>", "example.jpg"]
    }
},
{
    "Voice Changer": {
        "arguments": ["example.wav", "female"]
    },
    "Audio-to-Image": {
        "arguments": ["<Voice Changer>"]
    },
    "Image-to-Video": {
        "arguments": ["<Audio-to-Image>", "example.jpg"]
    },
    "Audio Noise Reduction": {
        "arguments": ["<Voice Changer>"]
    }
}"""

demo_data_multimedia_2_reasoning = """# TASK DEPENDENCIES #:
Article Spinner -> Text Summarizer
Text Summarizer -> Text-to-Image
Video Speed Changer -> Video-to-Image
Video-to-Image -> Image Colorizer

# TASK STEPS #:
{
    "Article Spinner": {
        "arguments": ["Example Article"]
    },
    "Text Summarizer": {
        "arguments": ["<Article Spinner>"]
    },
    "Text-to-Image": {
        "arguments": ["<Text Summarizer>"]
    },
    "Video Speed Changer": {
        "arguments": ["example.mp4", "adjust speed"]
    },
    "Video-to-Image": {
        "arguments": ["<Video Speed Changer>"]
    },
    "Image Colorizer": {
        "arguments": ["<Video-to-Image>"]
    }
}"""
demo_data_multimedia_2b_reasoning = """{
    "Video Speed Changer": {
        "arguments": ["example.mp4", "adjust speed"]
    },
    "Article Spinner": {
        "arguments": ["Example Article"]
    },
    "Text Summarizer": {
        "arguments": ["<Article Spinner>"]
    },
    "Video-to-Image": {
        "arguments": ["<Video Speed Changer>"]
    },
    "Image Colorizer": {
        "arguments": ["<Video-to-Image>"]
    },
    "Text-to-Image": {
        "arguments": ["<Text Summarizer>"]
    }
},
{
    "Article Spinner": {
        "arguments": ["Example Article"]
    },
    "Text Summarizer": {
        "arguments": ["<Article Spinner>"]
    },
    "Text-to-Image": {
        "arguments": ["<Text Summarizer>"]
    },
    "Video Speed Changer": {
        "arguments": ["example.mp4", "adjust speed"]
    },
    "Video-to-Image": {
        "arguments": ["<Video Speed Changer>"]
    },
    "Image Colorizer": {
        "arguments": ["<Video-to-Image>"]
    }
},
{
    "Article Spinner": {
        "arguments": ["Example Article"]
    },
    "Text Summarizer": {
        "arguments": ["<Article Spinner>"]
    },
    "Video Speed Changer": {
        "arguments": ["example.mp4", "adjust speed"]
    },
    "Text-to-Image": {
        "arguments": ["<Text Summarizer>"]
    },
    "Video-to-Image": {
        "arguments": ["<Video Speed Changer>"]
    },
    "Image Colorizer": {
        "arguments": ["<Video-to-Image>"]
    }
},
{
    "Video Speed Changer": {
        "arguments": ["example.mp4", "adjust speed"]
    },
    "Video-to-Image": {
        "arguments": ["<Video Speed Changer>"]
    },
    "Article Spinner": {
        "arguments": ["Example Article"]
    },
    "Text Summarizer": {
        "arguments": ["<Article Spinner>"]
    },
    "Image Colorizer": {
        "arguments": ["<Video-to-Image>"]
    },
    "Text-to-Image": {
        "arguments": ["<Text Summarizer>"]
    }
}"""

demo_messages = [
    {"role": "user", "content": f"# TOOL LIST #: {str([x for x in data_multimedia if x['id'] == '36690562'][0]['sampled_nodes'])} \n # USER REQUEST #: {[x for x in data_multimedia if x['id'] == '36690562'][0]['user_request']}"},
    {"role": "assistant", "content": demo_data_multimedia_0},
    {"role": "user", "content": f"Generate alternative valid task steps, that fulfill all the requirements # REQUIREMENTS # given above."},
    {"role": "assistant", "content": demo_data_multimedia_0b},
    {"role": "user", "content": f"# TOOL LIST #: {str([x for x in data_multimedia if x['id'] == '27258164'][0]['sampled_nodes'])} \n # USER REQUEST #: {[x for x in data_multimedia if x['id'] == '27258164'][0]['user_request']}"},
    {"role": "assistant", "content": demo_data_multimedia_1},
    {"role": "user", "content": f"Generate alternative valid task steps that fulfill all the requirements # REQUIREMENTS # given above."},
    {"role": "assistant", "content": demo_data_multimedia_1b},
    {"role": "user", "content": f"# TOOL LIST #: {str([x for x in data_multimedia if x['id'] == '33377661'][0]['sampled_nodes'])} \n # USER REQUEST #: {[x for x in data_multimedia if x['id'] == '33377661'][0]['user_request']}"},
    {"role": "assistant", "content": demo_data_multimedia_2},
    {"role": "user", "content": f"Generate alternative valid task steps that fulfill all the requirements # REQUIREMENTS # given above."},
    {"role": "assistant", "content": demo_data_multimedia_2b}
]

with open('tool_desc_multimedia.json') as f:
    tools = json.load(f)
    tools = json.dumps(tools)
    
demo_messages_full = [
    {"role": "user", "content": f"# TOOL LIST #: {tools} \n # USER REQUEST #: {[x for x in data_multimedia if x['id'] == '36690562'][0]['user_request']}"},
    {"role": "assistant", "content": demo_data_multimedia_0},
    {"role": "user", "content": f"Generate alternative valid task steps, that fulfill all the requirements # REQUIREMENTS # given above."},
    {"role": "assistant", "content": demo_data_multimedia_0b},
    {"role": "user", "content": f"# TOOL LIST #: {tools} \n # USER REQUEST #: {[x for x in data_multimedia if x['id'] == '27258164'][0]['user_request']}"},
    {"role": "assistant", "content": demo_data_multimedia_1},
    {"role": "user", "content": f"Generate alternative valid task steps that fulfill all the requirements # REQUIREMENTS # given above."},
    {"role": "assistant", "content": demo_data_multimedia_1b},
    {"role": "user", "content": f"# TOOL LIST #: {tools} \n # USER REQUEST #: {[x for x in data_multimedia if x['id'] == '33377661'][0]['user_request']}"},
    {"role": "assistant", "content": demo_data_multimedia_2},
    {"role": "user", "content": f"Generate alternative valid task steps that fulfill all the requirements # REQUIREMENTS # given above."},
    {"role": "assistant", "content": demo_data_multimedia_2b}
]
    

demo_messages_reasoning = [
    {"role": "user", "content": f"# TOOL LIST #: {str([x for x in data_multimedia if x['id'] == '36690562'][0]['sampled_nodes'])} \n # USER REQUEST #: {[x for x in data_multimedia if x['id'] == '36690562'][0]['user_request']}"},
    {"role": "assistant", "content": demo_data_multimedia_0_reasoning},
    {"role": "user", "content": f"Generate alternative valid task steps, that fulfill all the requirements # REQUIREMENTS # given above."},
    {"role": "assistant", "content": demo_data_multimedia_0b_reasoning},
    {"role": "user", "content": f"# TOOL LIST #: {str([x for x in data_multimedia if x['id'] == '27258164'][0]['sampled_nodes'])} \n # USER REQUEST #: {[x for x in data_multimedia if x['id'] == '27258164'][0]['user_request']}"},
    {"role": "assistant", "content": demo_data_multimedia_1_reasoning},
    {"role": "user", "content": f"Generate alternative valid task steps that fulfill all the requirements # REQUIREMENTS # given above."},
    {"role": "assistant", "content": demo_data_multimedia_1b_reasoning},
    {"role": "user", "content": f"# TOOL LIST #: {str([x for x in data_multimedia if x['id'] == '33377661'][0]['sampled_nodes'])} \n # USER REQUEST #: {[x for x in data_multimedia if x['id'] == '33377661'][0]['user_request']}"},
    {"role": "assistant", "content": demo_data_multimedia_2_reasoning},
    {"role": "user", "content": f"Generate alternative valid task steps that fulfill all the requirements # REQUIREMENTS # given above."},
    {"role": "assistant", "content": demo_data_multimedia_2b_reasoning}
]

def create_graph(data):
    G = nx.DiGraph()
    G.graph['user_request'] = data['user_request']  # Store the user_request in the graph
    for node in data["sampled_nodes"]:
        G.add_node(node["task"])
    for link in data["sampled_links"]:
        G.add_edge(link["source"], link["target"])
    return G


def create_graph_anonymous(data):
    import string
    import networkx as nx
    G = nx.DiGraph()
    G.graph['user_request'] = data['user_request']
    node_names = iter(string.ascii_lowercase)
    node_mapping = {}

    # Add nodes and edges to the graph using original names
    for node in data["sampled_nodes"]:
        G.add_node(node["task"])
    for link in data["sampled_links"]:
        G.add_edge(link["source"], link["target"])

    # Perform a topological sort on the graph
    sorted_nodes = list(nx.topological_sort(G))

    # Assign new names to nodes in topological order
    for node in sorted_nodes:
        node_name = next(node_names)
        node_mapping[node] = node_name

    # Create a new graph with renamed nodes and same edges
    G_new = nx.relabel_nodes(G, node_mapping, copy=True)

    return G_new
    

def draw_graph(G):
    nx.draw(G, with_labels=True)
    plt.show()

def convert_and_view_petri_net(tree):
    from pm4py import convert_to_petri_net, view_petri_net
    net, initial_marking, final_marking = convert_to_petri_net(tree)
    view_petri_net(net, initial_marking, final_marking, format="png")