# Regex to DFA Tool

- Object Oriented like Python program which takes a Regex in Prenex form and returns its corresponding DFA.
- Uses core Finite Automata Theory notions.
- The transformation process is split in two parts:
  - Firstly, the Regex is turned into an NFA using Thompson’s construction.
  - Secondly, the resulted NFA is turned into a DFA using the subset construction algorithm.

## Prenex normal form

- In the Prenex Normal Form (PNF), the operator ALWAYS precedes the operands.
- Example of PNF:
  - Regex: `ab|c*`
  - Prenex: `UNION CONCAT a b STAR c`

## How to run the program?

- Create an input file containing a prenex expression.
- Run the program with the following command: `python3 main.py <input_file> <output_file>`
- The contents of the output file will be the following:

```
<alphabet>
<nr_states>
<initial_state>
<final_states_list>
<transition_1>
<transition_2>
...
<transition_n>
```

## Technical details

This is a short description of how the program works:

- The whole input file is read into a buffer, which is then sent to the Expression class.
- There, the string is parsed, and the data is stored recursively in a tree like data structure.
- Once the parsing is complete, the expression is then transformed into an NFA using Thompson’s construction.
- The NFA is then transformed into a DFA using the subset construction algorithm.
- In the end, the resulting DFA is written in the output file using a to_str() method.

Other details:

- The Expression class is extremely similar to a Java abstract class.
  - Different types of basic expressions, such as `Star`, `Union`, `Concat`, all inherit from the Expression class.
  - Method overriding is used for the to_nfa_callback() method.
  - Each to_nfa_callback() method corresponds to a rule for a specific operator in Thompson's algorithm.
- Both the NFA and DFA class use the same State class for their internal states.
- Most of the methods of the DFA class are not used in this project, but are useful for implementing a simple Lexer.
