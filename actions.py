class Action:
    def __init__(self, current,name):
        self.current_state=current
        self.name=name

class ShiftAction(Action):
    def __init__(self, current, next, symbol):
        super().__init__(current,"shift")
        self.next=next
        self.symbol=symbol

    def __str__(self):
        print("shift "+str(self.current)+" with "+self.symbol+" to "+str(self.next))

class ReduceAction(Action):
    def __init__(self, current, productionNumber):
        super().__init__(current, "reduce")
        self.productionNumber=productionNumber

    def __str__(self):
        print("reduce "+str(self.current)+" with production "+self.productionNumber)

class AcceptAction(Action):
    def __init__(self, current):
        super().__init__(current, "accept")

    def __str__(self):
        print("accept "+str(self.current))