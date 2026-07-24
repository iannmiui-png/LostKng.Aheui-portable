#!/usr/bin/env python3
"""
sync_alphabet.py [file.html ...]

Rewrites the ALPHABET constant in a page so it matches aheui_alphabet.txt.

The residues stored in a PNG are indices into this alphabet, so it is not
cosmetic: changing which syllables the grid compiler can emit renumbers
every index after the first difference. That happened once already -- the
input block changed from 마/밯 to 무/붛, indices past position 9 shifted,
and a page with a stale constant decoded the grid into garbage and crashed
before printing anything. Run this after any compiler change.
"""
import re
import sys


def js_escape(alpha):
    return ''.join('\\n' if c == '\n' else c if c == ' ' else '\\u%04X' % ord(c)
                   for c in alpha)


def sync(path, alphabet='aheui_alphabet.txt'):
    alpha = open(alphabet, encoding='utf-8').read()
    src = open(path, encoding='utf-8').read()
    new = 'const ALPHABET = "%s";' % js_escape(alpha)
    out, n = re.subn(r'const\s+ALPHABET\s*=\s*"[^"]*";',
                     lambda _m: new, src, count=1)
    if not n:
        return False, 0
    open(path, 'w', encoding='utf-8').write(out)
    return True, len(alpha)


if __name__ == '__main__':
    targets = sys.argv[1:] or ['aheui_console.html']
    for t in targets:
        ok, n = sync(t)
        print(f'{t}: {"synced " + str(n) + " symbols" if ok else "no ALPHABET constant found"}')
