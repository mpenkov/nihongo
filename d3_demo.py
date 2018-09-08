# -*- encoding: utf-8 -*-
import csv
import gzip
import io
import json

import cherrypy
import mako.template
import networkx as nx

import logging
logging.basicConfig(level=logging.DEBUG)


def search(graph, node, seen, depth=1000):
    if depth == 0:
        return

    neighbors = [src for (src, dst) in graph.in_edges([node])]
    neighbors += [dst for (src, dst) in graph.out_edges([node])]

    logging.debug('node: %r depth: %r neighbors: %r seen: %r',
                  node, depth, neighbors, seen)

    seen.add(node)

    for n in neighbors:
        if n not in seen:
            search(graph, n, seen, depth - 1)


G = nx.read_yaml('graph.yml')


with gzip.GzipFile('heisig-data.txt.gz') as fin:
    fin.readline()
    reader = csv.DictReader(
        io.StringIO(fin.read().decode('utf-8')), delimiter=':'
    )
    heisig = list(reader)


heisig_dict = {k['kanji']: k for k in heisig}
from_keyword = {k['keyword5th-ed']: k['kanji'] for k in heisig}


def get_keyword(kanji):
    try:
        return heisig_dict[kanji]['keyword5th-ed']
    except KeyError:
        return None


def adaptive_subgraph(graph, kanji, threshold=20):
    for depth in reversed(range(2, 5)):
        logging.debug('depth: %r', depth)
        seen = set([kanji])
        search(G, kanji, seen, depth=depth)
        if len(seen) < threshold:
            break
    return graph.subgraph(seen)


class WebApp(object):
    @cherrypy.expose
    def index(self, kanji='露'):
        try:
            kanji = from_keyword[kanji]
        except KeyError:
            pass
        subgraph = adaptive_subgraph(G, kanji)

        nodes = [
            {'kanji': k, 'keyword': get_keyword(k), "id": k}
            for k in subgraph.nodes
        ]
        node_index = {k['kanji']: i for i, k in enumerate(nodes)}
        edges = [
            {'source': node_index[src], 'target': node_index[dst]}
            for (src, dst) in subgraph.edges
        ]
        variables = {
            'current_kanji': node_index[kanji],
            'nodes': json.dumps(nodes),
            'edges': json.dumps(edges),
        }

        with open('d3-template.html') as fin:
            template = fin.read()

        template = template.replace(
            '// <data></data>',
            """\
currentKanji = ${current_kanji};
nodes = ${nodes};
links = ${edges};
""")

        return mako.template.Template(template).render(**variables)


cherrypy.quickstart(WebApp())
