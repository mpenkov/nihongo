"""Attempt to parse the primitives for each Kanji."""
import re

with open("primitives.txt") as fin:
    primitives = set(fin.read().split("\n"))

with open("layout.txt") as fin:
    lines = fin.read().split("\n")

regex = re.compile(r"^ {2,}(?P<heisig_number>\d+) {40,}(?P<keyword>[\w ]+)$")
keywords = dict()
stories = dict()
for l in lines:
    m = regex.match(l)
    if m:
        heisig_number = int(m.group("heisig_number"))
        keyword = m.group("keyword")
        keywords[heisig_number] = keyword
        stories[heisig_number] = set()
        #print heisig_number, keyword
        continue
    #
    # this doesn't work too well for a couple of reasons:
    # 1) some primitives are ngrams, so splitting by a space doesn't capture them
    # 2) not all primitives that occur in the story are part of the current Kanji;
    #    they can just be part of the text
    #
    for prim in set(filter(lambda w: w and w.lower() in primitives, l.lower().split(" "))):
        stories[heisig_number].add(prim)

for heisig in sorted(stories):
    print heisig, keywords[heisig]
    print "\t", "\n\t".join(stories[heisig])
