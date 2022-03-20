from __future__ import annotations
from typing import *


class State:
    def __init__(self, name: str):
        self.id: str = name
        self.nr: int
        self.composed_from: FrozenSet[State] = frozenset()
        try:
            self.nr = int(name)
        except ValueError:
            self.nr = -1

    def __eq__(self, other):
        if len(self.composed_from) == 0:
            return self.id == other.id
        return self.composed_from == other.composed_from

    def __hash__(self):
        return hash(id)

    def __str__(self):
        if len(self.composed_from) == 0:
            return "State " + self.id
        return str(self.composed_from)

    def __repr__(self):
        return str(self)

    def rename_nfa(self, x: int) -> None:
        self.nr += x
        self.id = str(self.nr)

    def compose(self, lst: List[State]) -> State:
        self.composed_from = frozenset(lst)
        return self
