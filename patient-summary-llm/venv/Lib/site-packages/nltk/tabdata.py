# Natural Language Toolkit: Encode/Decocode Data as Tab-files
#
# Copyright (C) 2024 NLTK Project
# Author: Eric Kafe <kafe.eric@gmail.com>
# URL: <https://www.nltk.org/>
# For license information, see LICENSE.TXT
#


def rm_nl(s):
    if s[-1] == "\n":
        return s[:-1]
    return s


class TabEncoder:

    def list2txt(self, s):
        return "\n".join(s)

    def set2txt(self, s):
        return self.list2txt(list(s))

    def tup2tab(self, tup):
        return "\t".join(tup)

    def tups2tab(self, x):
        return "\n".join([self.tup2tab(tup) for tup in x])

    def dict2tab(self, d):
        return self.tups2tab(d.items())

    def ivdict2tab(self, d):
        # From integer-value dictionary
        return self.tups2tab([(a, str(b)) for a, b in d.items()])


class TabDecoder:

    def txt2list(self, f):
        return [rm_nl(x) for x in f]

    def txt2set(self, f):
        return {rm_nl(x) for x in f}

    def tab2tup(self, s):
        return tuple(s.split("\t"))

    def tab2tups(self, f):
        return [self.tab2tup(rm_nl(x)) for x in f]

    def tab2dict(self, f):
        return {a: b for a, b in self.tab2tups(f)}

    def tab2ivdict(self, f):
        # To integer-value dictionary
        return {a: int(b) for a, b in self.tab2tups(f)}


# ---------------------------------------------------------------------------
# Maxent data
# ---------------------------------------------------------------------------


class MaxentEncoder(TabEncoder):

    def tupdict2tab(self, d):
        def rep(a, b):
            if a == "wordlen":
                return repr(b)
            if b in [True, False, None]:
                return f"repr-{b}"
            return b

        return self.tups2tab(
            [(a, rep(a, b), c, repr(d)) for ((a, b, c), d) in d.items()]
        )


class MaxentDecoder(TabDecoder):

    def tupkey2dict(self, f):

        def rep(a, b):
            if a == "wordlen":
                return int(b)
            if b == "repr-None":
                return None
            if b == "repr-True":
                return True
            if b == "repr-False":
                return False
            return b

        return {(a, rep(a, b), c): int(d) for (a, b, c, d) in self.tab2tups(f)}


# ---------------------------------------------------------------------------
# Punkt data
# ---------------------------------------------------------------------------


class PunktDecoder(TabDecoder):

    def tab2intdict(self, f):
        from collections import defaultdict

        return defaultdict(int, {a: int(b) for a, b in self.tab2tups(f)})
