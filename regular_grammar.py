from re import fullmatch

class Grammar:
    def __init__(self):
        self.N = []
        self.Sigma = []
        self.P = {}
        self.S = None


    def read_regular_grammar_file(self, file):
        f = open(file, "r")

        self.N = f.readline().strip("\n").split(",")
        self.Sigma = f.readline().strip("\n").split(",")
        self.S = f.readline().strip("\n")
        self.P = {}

        line = f.readline().strip("\n")
        i=0
        while line != "":
            line = line.split("->")
            if line[0] not in self.P:
                self.P[line[0]] = []
            rhs = line[1].split("|")
            for elem in rhs:
                self.P[line[0]].append((elem,i))
                i+=1
            line = f.readline().strip("\n")

    def get_rhs_for_nonterminal(self,non_terminal):
        if non_terminal not in self.P:
            return None
        return self.P[non_terminal]

    def to_LR_grammar(self):
        if "S1" not in self.N:
            self.N.append("S1")
            self.P["S1"]=[self.S]
            self.S="S1"