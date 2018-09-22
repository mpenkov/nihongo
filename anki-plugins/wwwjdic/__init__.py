#
# -*- coding: utf-8 -*-
#

import os.path as P

import aqt.utils

# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

action = QAction("Debug console", mw)
# set it to call testFunction when it's clicked
action.triggered.connect(mw.onDebug)
# and add it to the tools menu
mw.form.menuTools.addAction(action)


def lookup_kanji():
    plugin_dir = P.dirname(P.abspath(__file__))

    with open(P.join(plugin_dir, "template.html")) as fin:
        template = fin.read()

    try:
        kanji = mw.reviewer.card._note.fields[0]
    except Exception:
        pass
    else:
        template = template.replace("露", kanji)

    with open(P.join(plugin_dir, "tmp.html"), "w") as fout:
        fout.write(template)

    aqt.utils.openLink("file://" + P.join(plugin_dir, "tmp.html"))


def map_kanji():
    try:
        kanji = mw.reviewer.card._note.fields[0]
    except Exception:
        kanji = "露"

    aqt.utils.openLink("https://kanji.now.sh/?kanji=" + kanji)

# create a new menu item, "test"
action = QAction("Look up current card on WWWJDIC", mw)
action.setShortcut(QKeySequence("Ctrl+J"))
# set it to call testFunction when it's clicked
action.triggered.connect(lookup_kanji)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

action = QAction("Look up current card on kanji.now.sh", mw)
action.setShortcut(QKeySequence("Ctrl+N"))
action.triggered.connect(map_kanji)
mw.form.menuTools.addAction(action)
