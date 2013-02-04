"""Create a digraph given a breakdown of Kanji.
Each node in the graph will be a Kanji character or primitive.
Heisig allows Kanji to be associated with more than one keyword (e.g. when used as primitives in more complex Kanji).
Kanji (and primitives) may be grouped together (given synonym relationships).
"""

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage="usage: python %s breakdown.txt [options]" % __file__)
    parser.add_option("-s", "--synonym", dest="synonym", type="string", default=None, help="the location of the synonym file")
    opts, args = parser.parse_args()
    if len(args) != 1:
        parser.error("invalid number of arguments")

    import csv
    synonyms = dict()
    if opts.synonym:
        with open(opts.synonym) as fin:
            reader = csv.reader(fin, delimiter=",")
            for r in reader:
                for i in range(1, len(r)):
                    synonyms[r[i]] = r[0]

    keywords = dict()
    primitives = dict()
    numbers = dict()
    all_primitives = set()
    with open(args[0]) as fin:
        reader = csv.reader(fin, delimiter=",")
        for r in reader:
            number = int(r[0])
            keywords[number] = r[1]
            numbers[r[1]] = number
            primitives[number] = filter(None, r[2:])
            all_primitives = all_primitives.union(set(primitives[number]))

    print "digraph g {"
    for number in keywords:
        for p in primitives[number]:
            try:
                node_from = synonyms[keywords[number]]
            except KeyError:
                node_from = keywords[number]
            try:
                node_to = synonyms[p]
            except KeyError:
                node_to = p
            print "\"%s\" -> \"%s\"" % (node_from, node_to)
    print "}"
    
