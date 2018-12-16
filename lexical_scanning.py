from re import fullmatch

class LexicalAnalysis:
    def __init__(self):
        self.PIF = []
        self.STid = []
        self.STconst = []
        self.codificationTable = self.read_codification_table()
        self.reservedWords, self.separators, self.operators = self.identify_special_characters()

    def read_codification_table(self):
        self.codificationTable = {}
        f = open("CodificationTable.txt", "r")
        line = f.readline().strip("\n")
        while line != "":
            words = line.split("  ")
            if words[1][0]==' ':
                words[1].strip(" ")
                words[0]=' '
            self.codificationTable[words[0]] = int(words[1])
            line = f.readline().strip("\n")
        return self.codificationTable
    
    
    def identify_special_characters(self):
        reservedWords = ['int','while','if']
        separators = [' ',':',';']
        operators = ['<','=']
        return reservedWords, separators, operators
    
    
    def split_by_separators(self, line, operators, separators):
        for i in range(len(line)):
            letter = line[i]
            if letter in separators or letter in operators[:5]:
                return line[0:i], letter, i
            if letter in operators[5:] or letter == '!':
                next = line[i + 1]
                if next == '=':
                    return line[0:i], letter + next, i + 1
                elif letter != "!":
                    return line[0:i], letter, i
        return line, '', len(line)
    
    
    def addToST(self, word, type):
        if type == 0:
            ST = self.STid
        else:
            ST = self.STconst
        for i in range(len(ST)):
            if word < ST[i]:
                ST.insert(i, word)
                return i
        ST.append(word)
        return len(ST) - 1
    
    
    def changePIF(self, newPos, type):
        for elem in self.PIF:
            if elem[0] == type and elem[1] >= newPos:
                elem[1] += 1
    
    
    def lexic_analysis(self,file):
        f = open(file, "r")
    
        lineNr = 0
        line = f.readline()
        while line != "":
            words = []
            line = line.strip('\n')
            while line != "":
                word, sep, i = self.split_by_separators(line, self.operators, self.separators)
                words.append(word)
                words.append(sep)
                line = line[i + 1:]
    
            for word in words:
                if word == '':
                    continue
    
                if word in self.reservedWords + self.operators + self.separators:
                    self.PIF.append([self.codificationTable[word], -1])
    
                elif fullmatch("((-)?[1-9][0-9]*)|0", word):
                    if word not in self.STconst:
                        writtenPos = self.addToST(word, 1)
                        self.changePIF(writtenPos, 1)
    
                    self.PIF.append([1, self.STconst.index(word)])
    
                elif fullmatch("\'[a-zA-Z0-9]\'", word):
                    if word not in self.STconst:
                        writtenPos = self.addToST(word, 1)
                        self.changePIF(writtenPos, 1)
    
                    self.PIF.append([1, self.STconst.index(word)])
    
                elif fullmatch("^[a-zA-Z][a-zA-Z0-9]*", word):
                    if len(word) > 8:
                        raise Exception(
                            "Identifiers can be named using maximum 8 characters\n line " + str(lineNr) + " word: " + word)
    
                    if word not in self.STid:
                        writtenPos = self.addToST(word, 0)
                        self.changePIF(writtenPos, 0)
    
                    self.PIF.append([0, self.STid.index(word)])
    
                else:
                    raise Exception("Invalid identifier at line " + str(lineNr) + " problem at word " + word)
    
            line = f.readline()
            
    def perform_lexical_analysis(self):
        try:
            self.lexic_analysis("program.txt")
            f = open("PIF.txt", "w")
            for word in self.PIF:
                f.write(str(word[0]) + " " + str(word[1]) + "\n")
            # print("Symbol table for identifiers: " + str(self.STid))
            # print("Symbol table for constant: " + str(self.STconst))
        except Exception as e:
            print("Lexical error: \n\t" + str(e))