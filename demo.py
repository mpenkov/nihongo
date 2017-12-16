# -*- encoding: utf-8 -*-
import cherrypy
import mako.template
import networkx as nx


class KanjiNavi(object):
    def __init__(self, graph_path='graph.yml'):
        self._G = nx.read_yaml(graph_path)

    def yield_ancestors(self, kanji):
        for edge in self._G.in_edges([kanji]):
            yield edge[0]

    def is_ancestor_of_any(self, kanji, descendants):
        for d in descendants:
            if kanji != d and self._G.has_edge(kanji, d):
                return True

    def yield_parents(self, kanji):
        """Get the direct ancestors of a kanji."""
        ancestors = list(self.yield_ancestors(kanji))
        for anc in ancestors:
            if not self.is_ancestor_of_any(anc, ancestors):
                yield anc

    def is_child_of_any(self, kanji, ancestors):
        for a in ancestors:
            if a != kanji and self._G.has_edge(a, kanji):
                return True

    def yield_descendants(self, kanji):
        for edge in self._G.out_edges([kanji]):
            yield edge[1]

    def yield_children(self, kanji):
        """Get the direct descendants of a kanji."""
        descendants = list(self.yield_descendants(kanji))
        for desc in descendants:
            if not self.is_child_of_any(desc, descendants):
                yield desc


navi = KanjiNavi()

template = '''<html>
<head>
  <style>
    body { font-size: 72px; }
  </style>
</head>
<body>
  <p>Ancestors:
    % for k in ancestors:
    ${makekanji(k)}
    % endfor
  </p>
  <p>Parents:
    % for k in parents:
    ${makekanji(k)}
    % endfor
  </p>
  <p>Current: ${makekanji(kanji)}</p>
  <p>Children:
    % for k in children:
    ${makekanji(k)}
    % endfor
  </p>
  <p>Descendants:
    % for k in descendants:
    ${makekanji(k)}
    % endfor
  </p>

<%def name="makekanji(kanji)">
<a href="/?kanji=${kanji}">${kanji}</a>
</%def>
'''


class WebApp(object):
    @cherrypy.expose
    def index(self, kanji='露'):
        ancestors = list(navi.yield_ancestors(kanji))
        parents = list(navi.yield_parents(kanji))
        children = list(navi.yield_children(kanji))
        descendants = list(navi.yield_descendants(kanji))

        ancestors = [a for a in ancestors if a not in parents]
        descendants = [d for d in descendants if d not in children]

        variables = {
            'ancestors': ancestors,
            'parents': parents,
            'kanji': kanji,
            'children': children,
            'descendants': descendants,
        }
        print(variables)
        return mako.template.Template(template).render(**variables)

cherrypy.quickstart(WebApp())
