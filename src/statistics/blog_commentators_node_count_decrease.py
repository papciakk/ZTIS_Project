import csv
from collections import defaultdict

nodes = {}

with open("edges.csv", "r", newline='') as f:
    rows = csv.reader(f, delimiter=',', quotechar='\"')
    edges = list(rows)
    edges = edges[1:]

edges = sorted(edges, key=lambda k: int(k[2]), reverse=True)
edges = edges[:500]

comentators = set([e[0] for e in edges])
blog_owners = defaultdict(int)

for e in edges:
    blog_owners[e[1]] += int(e[2])

for c in comentators:
    if c not in blog_owners:
        blog_owners[c] = 1

nodes_weight = defaultdict(int)
for e in edges:
    nodes_weight[e[1]] += int(e[2])

nodes = []
for id, weight in nodes_weight.items():
    nodes.append((id, id, weight))

node_target_ids = set(nodes_weight.keys())
for e in edges:
    if e[0] not in node_target_ids:
        nodes.append((e[0], e[0], 1))

with open("edges_50k.csv", 'w') as f:
    print("source,target,weight", file=f)
    for n in edges:
        print("\"{}\",\"{}\",\"{}\"".format(n[0], n[1], n[2]), file=f)

with open("nodes_50k.csv", 'w') as f:
    print("id,label,size", file=f)
    for n in nodes:
        print("\"{}\",\"{}\",\"{}\"".format(n[0], n[1], n[2]), file=f)
