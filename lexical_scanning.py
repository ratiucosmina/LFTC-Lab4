from re import fullmatch

PIF = []
STid = []
STconst = []


def read_codification_table():
    codificationTable = {}
    f = open("CodificationTable.txt", "r")
    line = f.readline().strip("\n")
    while line != "":
        words = line.split("  ")
        if words[1][0]==' ':
            words[1].strip(" ")
            words[0]=' '
        codificationTable[words[0]] = int(words[1])
        line = f.readline().strip("\n")
    return codificationTable


def identify_special_characters(codificationTable):
    vector = []
    for key in codificationTable.keys():
        vector.append(key)
    reservedWords = vector[2:4]
    separators = vector[5:]
    operators = vector[4:5]

    return reservedWords, separators, operators


def split_by_separators(line, operators, separators):
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


def addToST(word, type):
    if type == 0:
        ST = STid
    else:
        ST = STconst
    for i in range(len(ST)):
        if word < ST[i]:
            ST.insert(i, word)
            return i
    ST.append(word)
    return len(ST) - 1


def changePIF(newPos, type):
    for elem in PIF:
        if elem[0] == type and elem[1] >= newPos:
            elem[1] += 1


def lexic_analysis(file,codificationTable, reservedWords, operators, separators):
    f = open(file, "r")

    lineNr = 0
    line = f.readline()
    while line != "":
        words = []
        line = line.strip('\n')
        while line != "":
            word, sep, i = split_by_separators(line, operators, separators)
            words.append(word)
            words.append(sep)
            line = line[i + 1:]

        for word in words:
            if word == '':
                continue

            if word in reservedWords + operators + separators:
                PIF.append([codificationTable[word], -1])

            elif fullmatch("((-)?[1-9][0-9]*)|0", word):
                if word not in STconst:
                    writtenPos = addToST(word, 1)
                    changePIF(writtenPos, 1)

                PIF.append([1, STconst.index(word)])

            elif fullmatch("\'[a-zA-Z0-9]\'", word):
                if word not in STconst:
                    writtenPos = addToST(word, 1)
                    changePIF(writtenPos, 1)

                PIF.append([1, STconst.index(word)])

            elif fullmatch("^[a-zA-Z][a-zA-Z0-9]*", word):
                if len(word) > 8:
                    raise Exception(
                        "Identifiers can be named using maximum 8 characters\n line " + str(lineNr) + " word: " + word)

                if word not in STid:
                    writtenPos = addToST(word, 0)
                    changePIF(writtenPos, 0)

                PIF.append([0, STid.index(word)])

            else:
                raise Exception("Invalid identifier at line " + str(lineNr) + " problem at word " + word)

        line = f.readline()


codificationTable = read_codification_table()

reservedWords, separators, operators = identify_special_characters(codificationTable)
try:
    lexic_analysis("program.txt",codificationTable, reservedWords, operators, separators)
    f=open("PIF.txt","w")
    for word in PIF:
        f.write(str(word[0])+" "+str(word[1])+"\n")
    print("Symbol table for identifiers: " + str(STid))
    print("Symbol table for constant: " + str(STconst))
except Exception as e:
    print("Lexical error: \n\t" + str(e))
