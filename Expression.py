from __future__ import annotations
from Nfa import *


# A Java-like abstract class
class Expression:
    def __init__(self, nr: int, params: Optional[List[Expression]], name: str):
        self.nr_params = nr
        self.params = params
        self.name = name

    @classmethod
    def from_prenex_string(cls, prenex: str) -> Expression:
        return cls.from_prenex_lst(prenex.split())

    @classmethod
    def from_prenex_lst(cls, prenex: List[str]) -> Expression:
        while prenex:
            current: Expression = cls.create_expr(prenex.pop(0))
            for i in range(0, current.nr_params):
                current.params.append(Expression.from_prenex_lst(prenex))
            return current

    @staticmethod
    def create_expr(token: str) -> Expression:
        choices: dict = {'STAR': Star([]), 'CONCAT': Concat([]), 'UNION': Union([]), 'PLUS': Plus([]),
                         'NULL': NullExpr()}
        return choices.get(token, Symbol(token))

    def __str__(self):
        if self.nr_params == 0:
            return self.name
        buff: str = self.name + "(" + str(self.params[0])
        for i in range(1, self.nr_params):
            buff += ", " + str(self.params[i])
        return buff + ")"

    def to_regex(self):
        buff: str = ""
        for i in range(0, self.nr_params):
            buff += self.to_regex()
        return buff

    def to_nfa(self) -> NFA:
        return self.to_nfa_callback()

    def to_nfa_callback(self) -> NFA:
        pass


class Plus(Expression):
    def __init__(self, params: Union[List[Expression], None]):
        super().__init__(1, params, "Plus")

    def to_regex(self):
        return self.params[0].to_regex() + "+"

    def to_nfa_callback(self) -> NFA:
        star_e: NFA = Star([self.params[0]]).to_nfa_callback()
        star_e.delta[star_e.qi][Epsilon()].remove(star_e.f[0])
        return star_e


class Star(Expression):
    def __init__(self, params: Union[List[Expression], None]):
        super().__init__(1, params, "Star")

    def to_regex(self):
        return self.params[0].to_regex() + "*"

    def to_nfa_callback(self) -> NFA:
        e: NFA = self.params[0].to_nfa_callback()

        e.rename_states(1)
        si: State = State("0")
        e.states.add(si)
        states_set: Set[State] = e.states
        sf: State = State(str(len(states_set)))
        states_set.add(sf)

        sigma: Set[str] = e.sigma
        qi: State = si
        delta: Dict[State, Dict[Union[str, Epsilon], [State]]] = e.delta
        f: List[State] = [sf]

        # Draw epsilon transitions
        delta.setdefault(si, dict()).setdefault(Epsilon(), []).append(e.qi)
        for f_state in e.f:
            delta.setdefault(f_state, dict()).setdefault(Epsilon(), []).append(e.qi)
            delta.setdefault(f_state, dict()).setdefault(Epsilon(), []).append(sf)

        delta.setdefault(si, dict()).setdefault(Epsilon(), []).append(sf)
        return NFA(states_set, sigma, qi, delta, f)


class Concat(Expression):
    def __init__(self, params: List[Expression]):
        super().__init__(2, params, "Concat")

    def to_regex(self):
        return "(" + self.params[0].to_regex() + self.params[1].to_regex() + ")"

    def to_nfa_callback(self) -> NFA:
        e1: NFA = self.params[0].to_nfa_callback()
        e2: NFA = self.params[1].to_nfa_callback()

        e2.rename_states(len(e1.states))
        states_set: Set[State] = e1.states.union(e2.states)
        sigma: Set[str] = e1.sigma.union(e2.sigma)
        qi: State = e1.qi
        delta: Dict[State, Dict[Union[str, Epsilon], [State]]] = {**e1.delta, **e2.delta}
        f: List[State] = e2.f

        # Draw epsilon transitions
        for f_state in e1.f:
            delta.setdefault(f_state, dict()).setdefault(Epsilon(), []).append(e2.qi)
        return NFA(states_set, sigma, qi, delta, f)


class Union(Expression):
    def __init__(self, params: Union[List[Expression], None]):
        super().__init__(2, params, "Union")

    def to_regex(self):
        return "(" + self.params[0].to_regex() + " U " + self.params[1].to_regex() + ")"

    def to_nfa_callback(self) -> NFA:
        e1: NFA = self.params[0].to_nfa_callback()
        e2: NFA = self.params[1].to_nfa_callback()

        e1.rename_states(1)
        e2.rename_states(len(e1.states) + 1)

        si: State = State("0")
        states_set: Set[State] = e1.states.union(e2.states)
        states_set.add(si)
        sf: State = State(str(len(states_set)))
        states_set.add(sf)

        sigma: Set[str] = e1.sigma.union(e2.sigma)
        qi: State = si
        delta: Dict[State, Dict[Union[str, Epsilon], [State]]] = {**e1.delta, **e2.delta}
        f: List[State] = [sf]

        # Draw epsilon transitions from the new initial states to the old ones
        delta.setdefault(si, dict()).setdefault(Epsilon(), []).append(e1.qi)
        delta.setdefault(si, dict()).setdefault(Epsilon(), []).append(e2.qi)

        # Draw epsilon transitions from the old final states to the new one
        for f_state in e1.f:
            delta.setdefault(f_state, dict()).setdefault(Epsilon(), []).append(sf)

        for f_state in e2.f:
            delta.setdefault(f_state, dict()).setdefault(Epsilon(), []).append(sf)
        return NFA(states_set, sigma, qi, delta, f)


class Symbol(Expression):
    def __init__(self, name: str):
        super().__init__(0, None, name)

    def to_regex(self):
        return self.name

    def to_nfa_callback(self) -> NFA:
        states: Set[State] = set()
        s0: State = State("0")
        s1: State = State("1")
        states.add(s0)
        states.add(s1)

        # !!The same instances in the list of states are found in the dictionary as well!!
        delta: Dict[State, Dict[str, [State]]] = {}
        delta.setdefault(s0, dict()).setdefault(self.name, []).append(s1)
        return NFA(states, set(self.name), s0, delta, [s1])


class Epsilon(Symbol):
    def __init__(self):
        super().__init__("ε")

    def to_nfa_callback(self) -> NFA:
        s0: State = State("0")
        return NFA(set().add(s0), set(), s0, {}, [s0])

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class NullExpr(Expression):
    def __init__(self):
        super().__init__(0, None, "∅")

    def to_nfa_callback(self) -> NFA:
        states: Set[State] = set()
        s0: State = State("0")
        s1: State = State("1")
        states.add(s0)
        states.add(s1)
        return NFA(states, set(), s0, {}, [s1])
