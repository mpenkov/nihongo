# -*- encoding: utf-8 -*-
import csv
import gzip
import io
import itertools
import json
import logging
import os.path as P
import sys

import cherrypy
import mako.template
import networkx as nx

import chise
import krad
import kanjidic
import radicals

LOG_FORMAT = "[%(asctime)s: %(levelname)s] %(name)s %(funcName)s: %(message)s"


def search(graph, node, seen, depth=1000):
    if depth == 0:
        return

    seen.add(node)

    for _, n in graph.edges([node]):
        if n not in seen:
            search(graph, n, seen, depth - 1)


CURR_DIR = P.dirname(P.abspath(__file__))
G = nx.read_yaml(P.join(CURR_DIR, 'graph.yml'))


with gzip.GzipFile(P.join(CURR_DIR, 'heisig-data.txt.gz')) as fin:
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

        with open(P.join(CURR_DIR, 'template.html'), encoding='utf-8') as fin:
            template = fin.read()

        template = template.replace(
            '// <data></data>',
            """\
currentKanji = ${current_kanji};
nodes = ${nodes};
links = ${edges};
""")

        return mako.template.Template(template).render(**variables)

    @cherrypy.expose
    def builder(self):
        with open(P.join(CURR_DIR, 'builder-template.html'), encoding='utf-8') as fin:
            template = fin.read()
        return template

    @cherrypy.expose
    def query(self, q):
        parts = q.lower().split(" ")

        logging.info('parts: %r', parts)

        def meaning(kanji):
            try:
                info = kanjidic.DICT[kanji]
            except KeyError:
                return ""
            else:
                if info['meanings']:
                    return info['meanings'][0]
                return ""

        def english_name(rad):
            candidates = radicals.lookup(char=rad)
            if candidates:
                return candidates[0]["en"]
            return ""

        def num_radical_strokes(rad):
            candidates = radicals.lookup(char=rad)
            if candidates:
                return candidates[0]["strokes"]
            return 99

        def make_radicals(radicals):
            return [
                {'kanji': rad, 'ruby': english_name(rad)}
                for rad in sorted(radicals, key=num_radical_strokes)
            ]

        #
        # TODO:
        #
        # - show the radicals in a table
        # - handle spaces in names
        # - autocomplete/autosuggest
        #
        search_results = multisearch(parts)
        logging.info('search_results: %r', search_results)
        results = [
            {
                "kanji": k,
                "meaning": meaning(k),
                "parts": " ".join(chise.decompose(k)),
                "radicals": make_radicals(krad.DICT.get(k, [])),
            } for k in search_results
        ]

        def num_strokes(kanji):
            try:
                info = kanjidic.DICT[kanji['kanji']]
            except KeyError:
                logging.error('no kanjidic entry for %r', kanji['kanji'])
                return 99
            else:
                try:
                    return int(info['S'])
                except ValueError:
                    return 99

        results = sorted(results, key=num_strokes)
        return json.dumps({"r": results})


def multisearch(parts):
    logging.info("parts: %r", parts)
    candidates = set()

    synsets = [synset(p) for p in parts]
    synsets = [s for s in synsets if s]
    logging.info('synsets: %r', synsets)

    for list_of_kanji in itertools.product(*synsets):
        candidates |= krad.search(*list_of_kanji)
        candidates |= chise.search(*list_of_kanji)
    return candidates


def synset(part):
    candidates = set()
    candidates |= set([rad["char"] for rad in radicals.lookup(en=part)])

    try:
        candidates.add(from_keyword[part])
    except KeyError:
        pass

    for info in kanjidic.DICT.values():
        if part in info["meanings"]:
            candidates.add(info["kanji"])

    if len(part) == 1:
        #
        # Could already be a Kanji
        #
        candidates.add(part)

    return sorted(candidates)


def main():
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

    host = '0.0.0.0'
    port = 8080

    try:
        host = sys.argv[1]
        port = int(sys.argv[2])
    except IndexError:
        pass

    config = {
        '/': {
            'tools.staticdir.root': CURR_DIR,
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': 'static',
        },
    }
    cherrypy.tree.mount(WebApp(), '/', config=config)
    cherrypy.config.update({'server.socket_host': host, 'server.socket_port': port})
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    main()
