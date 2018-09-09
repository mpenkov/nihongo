# -*- encoding: utf-8 -*-
import csv
import gzip
import io
import json
import os.path as P

import cherrypy
import mako.template
import networkx as nx

import logging
logging.basicConfig(level=logging.DEBUG)


def search(graph, node, seen, depth=1000):
    if depth == 0:
        return

    seen.add(node)

    for _, n in graph.edges([node]):
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
    logging.debug('seen: %r', seen)
    return graph.subgraph(seen)


class WebApp(object):
    @cherrypy.expose
    def index(self, kanji='露', heisig_lesson=None):
        if heisig_lesson:
            lesson_kanji = [k['kanji'] for k in heisig_dict.values()
                            if k['lessonnumber'] == heisig_lesson]
            subgraph = G.subgraph(lesson_kanji)
            centrality = nx.degree_centrality(subgraph)
            max_val = max(centrality.values())
            kanji = [k for k, c in centrality.items() if c == max_val][0]
        else:
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
        logging.info('node_index: %r', node_index)
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


config = {
    '/': {
        'tools.staticdir.root': P.dirname(P.abspath(__file__)),
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'static',
    }
}
cherrypy.tree.mount(WebApp(), '/', config=config)
cherrypy.engine.start()
cherrypy.engine.block()
