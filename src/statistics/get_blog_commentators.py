import pickle
from itertools import groupby
from pprint import pprint

with open("blog_commentators.dat", "rb") as f:
    relation = pickle.load(f)

blog_owners = [r[0] for r in relation]
blog_owners.sort()
blog_owners_unique = set(blog_owners)
commentators = set([r[1] for r in relation])

edges = [(key[1], key[0], len(list(group))) for key, group in groupby(relation)]
nodes = [(key, key, len(list(group))) for key, group in groupby(blog_owners)]

for c in commentators:
    if c not in blog_owners:
        nodes.append((c, c, 1))

pprint(nodes)

with open("edges.csv", 'w') as f:
    print("source,target,weight", file=f)
    for n in edges:
        print("\"{}\",\"{}\",\"{}\"".format(n[0], n[1], n[2]), file=f)

with open("nodes.csv", 'w') as f:
    print("id,label,size", file=f)
    for n in nodes:
        print("\"{}\",\"{}\",\"{}\"".format(n[0], n[1], n[2]), file=f)

#
# with open("blog_urls_all.dat", "rb") as f:
#     all_blogs = pickle.load(f)
#
# blogs_to_download = []
# for blog_data in all_blogs:
#     if blog_data[1] not in downloaded_blogs and blog_data[1] is not None:
#         blogs_to_download.append(blog_data[0])
#
# c.execute("""select url from scraped_urls where notes_saved is not null""")
# blogs_stared_downloading = c.fetchall()
# blogs_stared_downloading = set([l[0] for l in blogs_stared_downloading])
#
# blogs_to_download.extend(blogs_stared_downloading)
#
# with open("blog_urls_rest.dat", "wb") as f:
#     pickle.dump(blogs_to_download, f)
