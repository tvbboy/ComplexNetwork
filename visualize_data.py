from matplotlib import pyplot as plt
from pyvis.network import Network
from mysql_connect.mysql_tool import execute_sql
from redis import Redis
import json
import networkx as nx

# network = Network(height="700px", width="700px")
nx_graph = nx.Graph()

def get_repo_name(repo_id):
    repo_name = execute_sql("select repo_name from repo where repo_id = " + str(repo_id))
    return repo_name[0][0]

def get_edge(repo_i, repo_j, date):
    sum_weight = 0
    weights = execute_sql("select weight from edge where repo_i = " + repo_i + " and repo_j = " + repo_j + " and date <= " + date)
    for weight in weights:
        sum_weight += int(weight[0])
    return sum_weight

cache = Redis(host='localhost', port=6379, decode_responses=True)
res_map = json.loads(cache.hget(name='lamda2=0.50', key='data'))
repo_ids = []
for key in res_map.keys():
    repo_ids.append(key)
    nx_graph.add_node(get_repo_name(key))
    # network.add_node(key, get_repo_name(key))

for key1 in repo_ids:
    for key2 in repo_ids:
        if str(key1) < str(key2):
            nx_graph.add_edge(get_repo_name(key1), get_repo_name(key2), weight = get_edge(key1, key2, "201912"))
            # network.add_edge(key1, key2, weight = get_edge(key1, key2, "201904"))

# 边的绘图碰到一个问题，把【0， 正无穷】的权重映射到【0，2】，否则边的绘制会太粗
edgewidth = [0.5 * (1 - 2 ** ((-1) * nx_graph.get_edge_data(*e)['weight'])) for e in nx_graph.edges()]
options = {
    'pos': nx.circular_layout(nx_graph),
    'node_size': 10,
    'node_color': "red",
    'edge_color': "gray",
    'width': edgewidth,
    'with_labels': True,
}
nx.draw(nx_graph, **options)
# network.show_buttons(filter_=['physics'])
# network.show("201901_201904.html")
plt.title("截止2019-12前的网络状态")
plt.show()



