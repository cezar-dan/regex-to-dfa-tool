from __future__ import annotations
from State import *
from typing import *

Conf = (State, str)


class DFA:
    def __init__(self, token, states, sigma, qi, delta, f, sink_states):
        self.token: str = token
        self.states: Set[State] = states
        self.sigma: List[str] = sigma
        self.qi: State = qi
        self.delta: Dict[State, Dict[str, State]] = delta
        self.f: List[State] = f
        self.sink_states: Set[State] = sink_states

    @classmethod
    def from_file_string(cls, input: List[str]) -> DFA:
        states: Set[State] = set()
        sigma: List[str] = list()
        delta: Dict[State, Dict[str, State]] = dict()
        reversed_delta: Dict[State, Dict[str, [State]]] = {}
        f: List[State] = list()

        # Add symbol to alphabet
        for i in range(0, len(input[0][:-1])):
            symbol: str = input[0][i]
            if symbol == "\\":
                if input[0][i + 1] == "n":
                    symbol = "\n"
                i += 1
            sigma.append(symbol)

        # Add token
        token: str = input[1][:-1]

        # Add initial state
        qi: State = State(input[2][:-1])

        input[:] = input[3:]
        nr_trans: int = 0
        for trans in input[0:-1]:
            if ',' not in trans:
                break
            nr_trans += 1

            cur, symbol, next = trans[:-1].split(',')
            symbol = symbol[1:-1]

            if symbol.find("\\n") >= 0:
                symbol = symbol.replace("\\n", "\n")

            # Add transition to delta function
            delta.setdefault(State(cur), dict()).setdefault(symbol, State(next))

            # Populate reversed graph (dest nodes become source nodes and vice versa)
            reversed_delta.setdefault(State(next), dict()).setdefault(symbol, []).append(State(cur))

            # Add states to state list
            states.add(State(cur))
            states.add(State(next))

        # Add final states
        for f_state in input[nr_trans].split():
            f.append(State(f_state))

        input[:] = input[nr_trans + 2:]

        # Find states that are not sinks
        not_sink_states: Set[State] = cls.find_not_sink_states(reversed_delta, f)

        return cls(token, states, sigma, qi, delta, f, states.difference(not_sink_states))

    @classmethod
    def from_file(cls, input: List[str]) -> List[DFA]:
        dfas: List[DFA] = []
        while input:
            dfas.append(cls.from_file_string(input))
        return dfas

    @classmethod
    def find_not_sink_states(cls, reversed_delta: Dict[State, Dict[str, State]], f_states: List[State]) -> Set[State]:
        not_sink_states: Set[State] = set()

        for f_state in f_states:
            viz: Set[State] = set()
            stack: List[State] = [f_state]

            while stack:
                s: State = stack.pop()
                viz.add(s)
                not_sink_states.add(s)

                if s not in reversed_delta:
                    continue

                # join list of lists in python (Christian C. Salvadó's comment):
                # https://stackoverflow.com/questions/716477/join-list-of-lists-in-python?lq=1
                neighbours: List[State] = sum(list(reversed_delta[s].values()), [])
                for neighbour in neighbours:
                    if neighbour not in viz and neighbour not in not_sink_states:
                        stack.append(neighbour)
        return not_sink_states

    def step(self, conf: Conf) -> Conf:
        word: str = conf[1]
        symbol: str = word[0]
        cur_state = conf[0]

        # If the transition is not specified, go to sink state and consume the whole word
        if symbol not in self.delta[cur_state]:
            if not self.sink_states:
                self.sink_states.add(State("S"))
            return next(iter(self.sink_states)), ""

        return self.delta[cur_state][symbol], word[1:]

    def accept(self, word: str) -> bool:
        conf: Conf = (self.qi, word)
        while conf[1] != "":
            conf = self.step(conf)
        if conf[0] in self.f:
            return True
        return False

    def longest_prefix(self, word: str) -> (str, int):
        conf: Conf = (self.qi, word)
        last_symbol: str = ""
        prefix: str = ""
        max_prefix: str = ""
        offset_to_non_final: int = 0

        while conf[1] != "" and conf[0] not in self.sink_states:
            offset_to_non_final += 1
            prefix += last_symbol
            if conf[0] in self.f:
                max_prefix = prefix[:]
            last_symbol = conf[1][0]
            conf = self.step(conf)

        # If the word was fully consumed without the DFA reaching a sink state, make a last update
        if conf[0] not in self.sink_states:
            if conf[0] in self.f:
                max_prefix = prefix + last_symbol
            else:
                offset_to_non_final += 1

        return max_prefix, offset_to_non_final - 1

    def __str__(self):
        return "token: " + self.token + "\n" + \
               "sigma <alphabet>: " + str(self.sigma) + "\n" + \
               "qi <initial state>: " + str(self.qi) + "\n" + \
               "f <final states>: " + str(self.f) + "\n" + \
               "delta: " + str(self.delta) + "\n" + \
               "states: " + str(self.states) + "\n" + \
               "sink_states: " + str(self.sink_states)

    def to_csv(self, file):
        with open(file, "w") as f_out:
            f_out.write("from,char,to\n")
            for src, dic in self.delta.items():
                for symbol, dest in dic.items():
                    is_final: str = ""
                    if dest in self.f:
                        is_final = "f"
                    f_out.write(src.id + "," + str(symbol) + "," + str(is_final) + dest.id + "\n")

    def to_str_stage2(self) -> str:
        buffer: str = ""
        for symbol in self.sigma:
            buffer += symbol
        buffer += "\n" + str(len(self.states))
        buffer += "\n" + str(self.qi.id) + "\n"
        for f_state in self.f:
            buffer += f_state.id + " "
        buffer = buffer[:-1]
        for src, dic in self.delta.items():
            for symbol, dest in dic.items():
                buffer += "\n" + str(src.nr) + ",'" + symbol + "'," + str(dest.nr)
        return buffer
