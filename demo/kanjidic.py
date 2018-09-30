import gzip
import os.path as P

_FIELDS = ['MN', 'MP'] + list("UNBCSGHFPKLIQ")
"""
[U] the Unicode/ISO 10646 code of the kanji in hexadecimal;
[N] the index in Nelson (Modern Reader's Japanese-English Character Dictionary)
[B] the classification radical number of the kanji (as in Nelson);
[C] the "classical" radical number
    (where this differs from the one used in Nelson);
[S] the total stroke-count of the kanji;
[G] the "grade" of the kanji, In this case, G2 means it is a Jouyou (general
    use) kanji taught in the second year of elementary schooling in Japan;
[H] the index in Halpern (New Japanese-English Character Dictionary);
[F] the rank-order frequency of occurrence of the kanji in Japanese;
[P] the "SKIP" coding of the kanji, as used in Halpern;
[K] the index in the Gakken Kanji Dictionary (A New Dictionary of Kanji Usage);
[L] the index in Heisig (Remembering The Kanji);
[I] the index in the Spahn & Hadamitsky dictionary.
[Q] the Four-Corner code;
[MN,MP] the index and page number in the 13-volume Morohashi "DaiKanWaJiten";
[E] the index in Henshall (A Guide To Remembering Japanese Characters);
[Y] the PinYin (Chinese) pronunciation(s) of the kanji;
"""

_CURR_DIR = P.dirname(P.abspath(__file__))


def _parse_parts(parts):
    readings = []
    meanings = []
    for part in parts:
        if part[0] == '{' and part[-1] == '}':
            meanings.append(part[1:-1])
            break
        for field in _FIELDS:
            if part.startswith(field):
                yield field, part[len(field):]
                break
        else:
            readings.append(part)
    yield 'meanings', meanings
    # Contains stuff other than the readings now
    # yield 'readings', readings


def _parse():
    with gzip.GzipFile(P.join(_CURR_DIR, 'kanjidic.gz')) as fin:
        next(fin)
        for line in fin:
            # http://www.edrdg.org/kanjidic/kanjidic.html
            parts = line.decode('euc-jp').split(' ')
            kanji = parts.pop(0)
            jis_code = parts.pop(1)
            info = dict(_parse_parts(parts))
            info.update(kanji=kanji, jis_code=jis_code)
            yield info


DICT = {x['kanji']: x for x in _parse()}
