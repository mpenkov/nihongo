"""Attempt to parse the primitives for each Kanji."""

with open("layout.txt") as fin:
    chunks = fin.read().split("\n\n")

def parse_chunk(chunk, prev_num=0):
    """Parse a chunk given the chunk string and the previous Kanji number.
    Returns the parsed Kanji number, keyword, and list of contained primitives (may be empty).
    If nothing is found, returns None."""
    chunk = chunk.strip()
    lines = chunk.split("\n")
    header = filter(None, lines[0].split(" "))
    if len(header) != 2:
        return None
    number = header[0]
    keyword = header[1]
    print number, keyword
    if prev_num > 0 and number != prev_num + 1:
        # bad Heisig number
        return None
    return number, keyword, list()

parsed = dict()
prev_num = 0
for i, chunk in enumerate(chunks):
    if i > 10:
        break
    result = parse_chunk(chunk, prev_num)
    if not result:
        continue
    prev_num += 1
    print i, result
