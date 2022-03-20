from __future__ import annotations
from Dfa import *

Conf = (State, str)


class NFA:
    def __init__(self, states, sigma, qi, delta, f):
        from Expression import Epsilon
        self.states: Set[State] = states
        self.sigma: Set[str] = sigma
        self.qi: State = qi
        self.delta: Dict[State, Dict[Union[str, Epsilon], [State]]] = delta
        self.f: List[State] = f
        self.eps_closures: Dict[State, List[State]] = {}

    def rename_states(self, x: int) -> None:
        for state in self.states:
            state.rename_nfa(x)

    def __str__(self):
        return "sigma <alphabet>: " + str(self.sigma) + "\n" + \
               "qi <initial state>: " + str(self.qi) + "\n" + \
               "f <final states>: " + str(self.f) + "\n" + \
               "delta: " + str(self.delta) + "\n" + \
               "states: " + str(self.states) + "\n"

    def to_csv(self, file):
        with open(file, "w") as f_out:
            f_out.write("from,char,to\n")
            for src, dic in self.delta.items():
                for symbol, dest_l in dic.items():
                    for dest in dest_l:
                        is_final: str = ""
                        if dest in self.f:
                            is_final = "f"
                        f_out.write(src.id + "," + str(symbol) + "," + str(is_final) + dest.id + "\n")

    def compute_eps_closures(self):
        from Expression import Epsilon
        for src in self.states:
            self.eps_closures[src] = []
            viz: Set[State] = set()
            stack: List[State] = [src]

            while stack:
                s: State = stack.pop()
                viz.add(s)

                if s not in self.delta:
                    continue

                neighbours: List[State] = sum(list(self.delta[s].values()), [])
                for neighbour in neighbours:
                    if neighbour not in viz and Epsilon() in self.delta[s] and neighbour in self.delta[s][Epsilon()]:
                        stack.append(neighbour)
                        self.eps_closures[src].append(neighbour)

    def get_dfa(self) -> DFA:
        # Initialise local variables that will be used to build the DFA
        self.compute_eps_closures()
        states: Set[State] = set()
        sigma: List[str] = list(self.sigma)
        qi: State = State("0").compose([self.qi] + self.eps_closures[self.qi])
        states.add(qi)
        delta: Dict[State, Dict[str, State]] = {}
        f: Set[State] = set()
        for dest_nfa in qi.composed_from:
            if dest_nfa in self.f:
                f.add(qi)
                break
        sink_state: State = State("S")

        # Start building the DFA in a DFS manner
        viz: Set[State] = set()
        stack: List[State] = [qi]

        while stack:
            src: State = stack.pop()
            viz.add(src)

            for symbol in sigma:
                # Find the set of states from the NFA that will make up the new state in the DFA
                dest_l: List[State] = []
                for d in src.composed_from:
                    if d in self.delta and symbol in self.delta[d]:
                        dest_l.extend(self.delta[d][symbol])
                        for dest_nfa in self.delta[d][symbol]:
                            dest_l.extend(self.eps_closures[dest_nfa])
                if not dest_l:
                    delta.setdefault(src, dict()).setdefault(symbol, sink_state)
                else:
                    dest: State = State(str(len(states))).compose(dest_l)
                    if dest not in states:
                        states.add(dest)
                    else:
                        for state in states:
                            if dest == state:
                                dest = state
                                break

                    # Compute new final states
                    for dest_nfa in dest.composed_from:
                        if dest_nfa in self.f:
                            f.add(dest)
                            break

                    # Add the transition
                    delta.setdefault(src, dict()).setdefault(symbol, dest)
                    if dest not in viz:
                        stack.append(dest)

        # Add sink state and its transitions
        sink_state.nr = len(states)
        states.add(sink_state)
        for symbol in sigma:
            delta.setdefault(sink_state, dict()).setdefault(symbol, sink_state)

        # Clear the NFA info from the DFA
        for state in states:
            state.composed_from = {}

        return DFA("", states, sigma, qi, delta, list(f), {sink_state})
