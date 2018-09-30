import os.path as P
import collections

_CURR_DIR = P.dirname(P.abspath(__file__))

with open(P.join(_CURR_DIR, 'IDS-UCS-Basic.txt'), encoding='utf-8') as fin:
    _RAW_DATA = fin.read().rstrip()


def _parse_ideographs(text):
    #
    # Each ideograph is either:
    #
    #     1) A single character, where a character for the ideograph actually exists
    #     2) An escape code in the form of "&CDP-FFFF;", where FFFF is hex for the code.
    #
    while text:
        if text.startswith('&'):
            end = text.index(';')
            yield text[:end + 1]
            text = text[end + 1:]
        else:
            yield text[0]
            text = text[1:]


def _parse_raw_data(raw_data):
    for line in raw_data.split('\n')[1:]:
        code_point, kanji, ideographs = line.rstrip().split('\t', 2)
        yield kanji, list(_parse_ideographs(ideographs))


DICT = dict(_parse_raw_data(_RAW_DATA))


def decompose(kanji):
    """Decompose a Kanji as much as possible."""
    try:
        ideographs = DICT[kanji]
    except KeyError:
        return [kanji]
    if len(ideographs) == 1:
        return ideographs
    result = []
    for i in ideographs:
        result.extend(decompose(i))
    return result


INV = collections.defaultdict(list)
for kanji in DICT:
    for ideogram in DICT[kanji] + decompose(kanji):
        INV[ideogram].append(kanji)


def search(*parts):
    """Search for Kanji that contain all of the specified parts."""
    parts = list(parts)
    is_singleton = len(parts) == 1
    first_part = parts.pop()
    candidates = set(INV[first_part])
    while parts:
        candidates = candidates.intersection(set(INV[parts.pop()]))
    if is_singleton and first_part in DICT:
        candidates.add(first_part)
    return candidates
