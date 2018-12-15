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
                # print(s)
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

    def read_transitions_from_file(self, file):
        with open(file, "r") as f:
            transitions = f.read().split('\n')
            transitions = [trans.split(' ') for trans in transitions if trans != '']
            for trans in transitions:
                self.transitions[int(trans[0])] = []
                if len(trans) == 2:
                    if trans[1] == 'acc':
                        self.transitions[int(trans[0])].append(AcceptAction(int(trans[0])))
                    else:
                        self.transitions[int(trans[0])].append(ReduceAction(int(trans[0]), int(trans[1])))
                elif len(trans) == 3:
                    self.transitions[int(trans[0])].append(ShiftAction(int(trans[0]), int(trans[2]), trans[1]))
        # print([str(trans)+" -> "+str([str(action) for action in self.transitions[trans]]) for trans in self.transitions])

    def find_production(self, prod_nr):
        prod = [(x, tuple[0]) for x in self.grammar.P for tuple in self.grammar.P[x] if tuple[1] == prod_nr]
        return prod[0]

    def find_action_with_symbol(self, actions, symbol):
        for action in actions:
            if action.symbol == symbol:
                return action
        return -1

    def get_reverse_index(self, list, elem):
        for i in range(len(list)-1,-1,-1):
            if list[i] == elem:
                return i
        return -1

    def check_input(self, sequence):
        working = [0]
        input = sequence
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
                print("accept " + str(head_working))
                accept = True
                break

            if transitions[0].name == "reduce":
                print("reduce "+str(head_working))
                prodNr = transitions[0].productionNumber
                production = self.find_production(prodNr)
                lhs, rhs = production[0], production[1]

                index_rhs = self.get_reverse_index(working, rhs[0])
                if index_rhs == -1:
                    error = True
                    break
                working = working[:index_rhs]+[lhs]
                action = self.find_action_with_symbol(self.transitions[working[-2]],lhs)
                if action == -1:
                    error = True
                    break
                working.append(action.next)

                output=[prodNr]+output

            if transitions[0].name == "shift":
                if head_input != "eps":
                    input = input[1:]
                action = self.find_action_with_symbol(transitions, head_input)
                if action == -1:
                    error = True
                    break
                print("shift "+str(head_working)+" with "+ head_input + " to "+str(action.next))
                working += [head_input, action.next]

        if accept:
            return list(map(lambda x: x+1, output))
        elif error:
            print("Grammar doesn't accept the given sequence!")


alg = LR0("grammar_simple.txt")
alg.cannonical_collection()
alg.save_transitions_to_file("transitions.txt")
print("Output:",alg.check_input(["a","b","b","c"]))
# alg.read_transitions_from_file("transitions.txt")