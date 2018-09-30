"""Parses radical information scraped from Wikipedia.

https://en.wikipedia.org/w/index.php?title=Kangxi_radical&action=edit&section=3
"""

import json
import re

_RADICAL_NUMBER_REGEX = re.compile(
    r'\|style="text-align:right"\|\[\[Radical \d+\|(\d+)\]\]', re.UNICODE
)
_RADICAL_CHAR_REGEX = re.compile(
    r'\|\{\{lang\|zh-Hant\|(.+)\}\}'
)

RADICALS = []


def _lazy_init():
    global RADICALS
    with open('radicals.json') as fin:
        RADICALS = [json.loads(line) for line in fin]


def lookup(**kwargs):
    if not RADICALS:
        _lazy_init()

    def matches(radical):
        return all([value == radical.get(key) for (key, value) in kwargs.items()])

    return [radical for radical in RADICALS if matches(radical)]


def _match_or_fail(regex, text):
    match = regex.match(text)
    if match is None:
        raise ValueError('text %r does not match regex %r' % (text, regex))
    return match.group(1)


def _read_row(fin):
    separator = fin.readline().rstrip()
    if separator == '|}':
        raise StopIteration('end of table reached')
    elif separator != '|----':
        raise ValueError('expected row separator, got %r' % separator)
    row = [fin.readline().rstrip() for _ in range(11)]

    number = int(_match_or_fail(_RADICAL_NUMBER_REGEX, row[0]))
    radical_char = _match_or_fail(_RADICAL_CHAR_REGEX, row[1])
    stroke_count = int(row[2][1:])
    english_name = row[3][1:]
    # pinyin = row[4][1:]
    # viet = row[5][1:]
    japanese = row[6][1:]
    kana, romaji = japanese.split(' / ')
    return {
        'number': number,
        'char': radical_char,
        'strokes': stroke_count,
        'en': english_name,
        # 'pinyin': pinyin,
        # 'viet': viet,
        'kana': kana,
        'romaji': romaji,
    }


def _read_rows(fin):
    while True:
        try:
            yield _read_row(fin)
        except StopIteration:
            break


def main():
    import sys
    import json
    for row in _read_rows(sys.stdin):
        print(json.dumps(row, ensure_ascii=False))


if __name__ == '__main__':
    main()
