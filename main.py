from __future__ import annotations
from Expression import *
import sys

if __name__ == '__main__':
    with open(sys.argv[1], "r") as f_in:
        ex: Expression = Expression.from_prenex_string(f_in.read())
        nfa: NFA = ex.to_nfa()
        dfa: DFA = nfa.get_dfa()
        with open(sys.argv[2], "w") as f_out:
            f_out.write(dfa.to_str_stage2())
