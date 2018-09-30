import collections
import gzip

with gzip.GzipFile('kradfile.gz') as fin:
    _RAW_DATA = fin.read().decode('euc-jp')


def _parse():
    for line in _RAW_DATA.split('\n'):
        if line and line[0] == "#":
            continue
        elif ' : ' in line:
            kanji, radicals = line.split(' : ')
            radicals = radicals.split(' ')
            yield kanji, radicals


DICT = dict(_parse())

INV = collections.defaultdict(list)
for kanji in DICT:
    for radical in DICT[kanji]:
        INV[radical].append(kanji)


def search(*radicals):
    """Search for Kanji that contain all of the specified radicals."""
    radicals = list(radicals)
    first_radical = radicals.pop()
    candidates = set(INV[first_radical])
    while radicals:
        candidates = candidates.intersection(set(INV[radicals.pop()]))
    if not candidates:
        candidates.add(first_radical)
    return candidates
