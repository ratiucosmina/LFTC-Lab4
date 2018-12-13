from copy import deepcopy

from actions import AcceptAction, ReduceAction, ShiftAction
from regular_grammar import Grammar


class LR0:
    def __init__(self, text_file):
        self.grammar = Grammar()
        self.grammar.read_regular_grammar_file(text_file)
        self.states = []  # list of states, each state has a list of lists lhs,rhs,i (i=dot)
        self.transitions = {}  # key: state, value: list of Action

    def check_conflicts(self, action, ex_state_nr, next_state_nr):
        if ex_state_nr in self.transitions:
            for existent in self.transitions[ex_state_nr]:
                if existent.name == "reduce":
                    if action.name == "reduce":
                        raise Exception("Reduce reduce conflict in state " + str(ex_state_nr) + " current states: " + str(next_state_nr))
                    if action.name == "shift":
                        raise Exception("Shift reduce conflict in state " + str(ex_state_nr) + " current states: " + str(next_state_nr))
                elif existent.name == "shift":
                    if action.name == "reduce":
                        raise Exception("Shift reduce conflict in state " + str(ex_state_nr) + " current states: " + str(next_state_nr))
                    if action.name == "shift" and action.symbol == existent.symbol:
                        raise Exception("Shift shift conflict in state " + str(ex_state_nr) + " on symbol " + action.symbol + " current states: " + str(next_state_nr) + " on symbol(" + action.symbol + ")")

    def closure(self, set_states):
        result = set_states
        for state in result:
            rhs = state[1]
            dot = state[2]

            if dot >= len(rhs) or rhs[dot] not in self.grammar.N:
                continue
            symbol = rhs[dot]

            for right in self.grammar.get_rhs_for_nonterminal(symbol):
                result.append([symbol, right[0], 0])

        return result

    def goto(self, state, symbol):
        result = []
        for element in state:
            rhs = element[1]
            dot = element[2]

            if dot >= len(rhs):
                continue

            current = rhs[dot]
            if current == symbol:
                elem = deepcopy(element)
                elem[2] += 1
                result.append(elem)

        return self.closure(result)

    def cannonical_collection(self):
        s0 = self.closure([["S'", 'S', 0]])
        self.states.append(s0)

        i = 0
        for state in self.states:
            symbols_done = []
            for element in state:
                lhs = element[0]
                rhs = element[1]
                dot = element[2]

                action = None
                if dot >= len(rhs):  # punctul e la final
                    if lhs == "S\'":  # accept
                        action = AcceptAction(i)
                    else:  # reduce
                        productions = self.grammar.get_rhs_for_nonterminal(lhs)  # iau toate productiile care match
                        prodNr = next(x[1] for x in productions if x[0]==rhs)
                        action = ReduceAction(i, prodNr)

                else:  # shift
                    symbol = rhs[dot]
                    if symbol in symbols_done:
                        continue

                    next_state = self.goto(state, symbol)
                    symbols_done.append(symbol)

                    # am calculat goto, acum gasesc numarul state-ului nou ca sa il pun in tabel

                    try:
                        stateNr = self.states.index(next_state)
                    except ValueError:
                        stateNr = len(self.states)
                        self.states.append(next_state)

                    action = ShiftAction(i, stateNr, symbol)

                if i not in self.transitions.keys():
                    self.transitions[i] = [action]
                    continue

                self.check_conflicts(action, i, stateNr)

                self.transitions[i].append(action)

            i += 1

        #asta doar printeaza pe ecran tranzitiile
        #just for debugging, se poate sterge
        for key in self.transitions.keys():
            for transition in self.transitions[key]:
                s = str(key) + " -> " + transition.name
                if transition.name == "shift":
                    s += " with symbol " + transition.symbol + " to " + str(transition.next)
                elif transition.name == "reduce":
                    s += " with production " + str(transition.productionNumber)
                print(s)

    #salvez tranzitiile in fisier ca sa nu fac prostia asta de fiecare data
    def save_transitions_to_file(self, file):
        f = open(file, "w")
        for key in self.transitions.keys():
            for action in self.transitions[key]:
                if action.name == "accept":
                    f.write(str(key) + " acc\n")
                elif action.name == "reduce":
                    f.write(str(key) + " " + str(action.productionNumber) + "\n")
                elif action.name == "shift":
                    f.write(str(key) + " " + action.symbol + " " + str(action.next) + "\n")
        f.close()

    #ToDo citeste tranzitiile din fisier
    #vezi mai sus cum le scriu
    #self.transitions e un dictionar, cheia e practic state-ul de pe linie (id-ul state-ului, deci 0,1 etc)
    #valoarea e o lista de actions
    #action poate fi AcceptAction care primeste doar starea din cheie
    #ReduceAction care primeste valoarea din cheie si production number care e schis in fisier
    #ShiftAction care primeste cheia, next_state si symbol, scrise in fisier
    def read_transitions_from_file(self, file):
        pass

    def check_input(self, sequence):
        working = [0]
        input = [sequence]
        output = []
        accept = False
        error = False

        while not accept and not error:
            if len(working) == 0:
                error = True
                break
            head_working = working[-1]
            if len(input) == 0:
                head_input = "eps"
            else:
                head_input = input[0]

            transitions = self.transitions[head_working]
            if len(transitions) == 0:
                error = True
                break

            if transitions[0].name == "accept":
                accept = True
                break
            if transitions[0].name == "reduce":
                prodNr = transitions[0].productionNumber
                # ToDo find production in a separate function
                #in self.grammar.P am toate productiile, e un dictionar
                #cheia e left hand side-ul productiei
                #valoarea e o lista de rhs-uri, fiecare e un tuple (rhs, numarul productiei)
                #deci daca as avea productia S->aA cu numarul 1, e salvata {'S':[('aA',1)]}

                #ToDo pop from working stack until all rhs is popped
                #ToDo push lhs in input stack

                output=[prodNr]+output
                pass

            if transitions[0].name == "shift":
                #ToDo find action with symbol equal to head_input
                # ToDo if not found, set error to true
                # ToDo if found, push head_input to working stack, push next_state index to working
                pass

        # ToDo if accept return output
        # ToDo error raise exception
            #message of the exception contains input stack or something


alg = LR0("grammar_simple.txt")
alg.cannonical_collection()
alg.save_transitions_to_file("transitions.txt")
