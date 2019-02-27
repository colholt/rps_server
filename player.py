class Player():
    def __init__(self, name, obj):
        self.name = name
        self.obj = obj
        self.hand = []
        self.trash = []
        self.status = 1
        self.lastPlayed = None
        self.opponent = None
        self.turn = False

    def getName(self):
        return self.name

    def getSelf(self):
        return self.obj

    def getStatus(self):
        return self.status

    def setStatus(self, status):
        self.status = status

    def addHand(self, card):
        self.hand.append(card)

    def setOpponent(self, opponent):
        self.opponent = opponent

    def getOpponent(self):
        return self.opponent

    def getHand(self):
        return self.hand

    def setState(self, state):
        self.obj.state = state

    def setTurn(self, val):
        self.turn = val

    def getTurn(self):
        return self.turn

    def setPlayed(self, card):
        print 'setting played:',card
        if card in self.hand:
            print 'card to hand:', card
            self.lastPlayed = card
            self.hand.remove(card)
            self.trash.append(card)

    def getPlayed(self):
        print 'returning',self.lastPlayed
        return self.lastPlayed