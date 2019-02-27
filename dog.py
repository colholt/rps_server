from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, task
import random
from player import Player

rps_table = {'rock':{'rock':0,'paper':-1,'scissor':1},
             'paper':{'rock':1,'paper':0,'scissor':-1},
             'scissor':{'rock':-1,'paper':1,'scissor':-1}}

class Chat(LineReceiver):

    def __init__(self, users, lobby):
        self.users = users
        self.lobby = lobby
        self.name = None
        self.state = "GETNAME"

    def connectionMade(self):
        print 'client connected'
        self.sendLine('{"type": "hello", "message": "none"}')

    def connectionLost(self, reason):
        if self.users.has_key(self.name):
            del self.users[self.name]

    def lineReceived(self, line):
        print 'received:', line
        if self.state == "GETNAME":
            self.handle_GETNAME(line)
        elif self.state == "MATCHMAKING":
            self.handle_MATCHMAKING(line)
        elif self.state == 'GAME':
            self.handle_GAME(line)
        elif self.state == 'MATCH':
            self.handle_MATCH(line)

    def handle_GETNAME(self, name):
        if self.users.has_key(name):
            self.sendLine('{"type": "warning", "message": "Name taken, please choose another"}')
            return
        self.sendLine('{"type": "greeting", "message": "hello %s"}' % (name,))
        self.name = name
        self.users[name] = Player(name, self)
        self.users[name].setStatus(1)
        self.state = "MATCHMAKING"
        self.sendLine('{"type": "matchmaking", "message": "none"}')
        self.lobby.append(self.users[name])
        self.do_MATCHMAKING()

    def do_MATCHMAKING(self):
        while len(self.lobby) >= 2:
            pOne = self.lobby.pop(0)
            pTwo = self.lobby.pop(0)
            pOne.setStatus(2)
            pTwo.setStatus(2)
            pOne.setState("GAME")
            pTwo.setState("GAME")
            sendStr1 = '{"type": "opponent", "message": "' + pTwo.getName() + '"}'
            sendStr2 = '{"type": "opponent", "message": "' + pOne.getName() + '"}'
            pOne.getSelf().sendLine(sendStr1.strip('\r'))
            pTwo.getSelf().sendLine(sendStr2.strip('\r'))
            pOne.setOpponent(pTwo)
            pTwo.setOpponent(pOne)

    def handle_GAME(self, msg):
        this = self.users[self.name]
        if "addcard" in msg:
            if len(this.getHand()) < 3:
                if 'rock' in msg:
                    this.addHand("rock")
                    this.getSelf().sendLine('{"type": "addcard", "message": "rock"}')
                elif 'paper' in msg:
                    this.getSelf().sendLine('{"type": "addcard", "message": "paper"}')
                    this.addHand("paper")
                elif 'scissor' in msg:
                    this.getSelf().sendLine('{"type": "addcard", "message": "scissor"}')
                    this.addHand("scissor")
                if len(this.getHand()) == 3:
                    if len(this.getOpponent().getHand()) == 3:
                        ## start game
                        this.getSelf().sendLine(self.createMessage("2manycard", "nope"))
                        this.getSelf().sendLine('{"type": "gamestart", "message": "none"}')
                        this.getOpponent().getSelf().sendLine('{"type": "gamestart", "message": "none"}')
                        this.setState("MATCH")
                        this.getOpponent().setState("MATCH")
                    else:
                        this.getSelf().sendLine(self.createMessage("2manycard", "nope"))

    def handle_MATCH(self, msg):
        this = self.users[self.name]
        if "playcard" in msg:
            if not this.getTurn():
                if 'rock' in msg:
                    this.setTurn(True)  # turn is basically HAS PLAYED
                    this.setPlayed('rock')
                    this.getSelf().sendLine('{"type": "playcard", "message": "rock"}')
                elif 'paper' in msg:
                    this.setTurn(True)  # turn is basically HAS PLAYED
                    this.setPlayed('paper')
                    this.getSelf().sendLine('{"type": "playcard", "message": "paper"}')
                elif 'scissor' in msg:
                    this.setTurn(True)  # turn is basically HAS PLAYED
                    this.setPlayed('scissor')
                    this.getSelf().sendLine('{"type": "playcard", "message": "scissor"}')
                if this.getOpponent().getTurn():
                    # both have played, finish the match
                    print ("%s played %s and %s played %s" % (this.getName(), this.getPlayed(), this.getOpponent().getName(), this.getOpponent().getPlayed()))

                    res = rps_table[this.getPlayed()][this.getOpponent().getPlayed()]
                    if res == 1:
                        this.getSelf().sendLine(self.createMessage("outcome", "won"))
                        this.getOpponent().getSelf().sendLine(self.createMessage("outcome", "loss"))
                    elif res == -1:
                        this.getSelf().sendLine(self.createMessage("outcome", "loss"))
                        this.getOpponent().getSelf().sendLine(self.createMessage("outcome", "won"))
                    else:
                        this.getSelf().sendLine(self.createMessage("outcome", "tie"))
                        this.getOpponent().getSelf().sendLine(self.createMessage("outcome", "tie"))

                    # this.getSelf().sendLine('{"type": "outcome", "message": "%s played %s and %s played %s"}' %
                    #                         (this.getName(), this.getPlayed(), this.getOpponent().getName(), this.getOpponent().getPlayed()))
                    # this.getOpponent().getSelf().sendLine('{"type": "outcome", "message": "%s played %s and %s played %s"}' %
                    #                         (this.getName(), this.getPlayed(), this.getOpponent().getName(), this.getOpponent().getPlayed()))

    def handle_MATCHMAKING(self, msg):
        print 'mm received:', msg

    def handle_CHAT(self, message):
        message = "<%s> %s" % (self.name, message)
        for name, protocol in self.users.iteritems():
            if protocol != self:
                protocol.sendLine(message)

    def createMessage(self, type, message):
        return '{"type": "%s", "message": "%s"}' % (type, message)


class ChatFactory(Factory):

    def __init__(self):
        self.users = {} # maps user names to Chat instances
        self.lobby = []

    def makeGame(self, playerOne, playerTwo):
        self.sendLine("hello")

    def buildProtocol(self, addr):
        return Chat(self.users, self.lobby)


reactor.listenTCP(8123, ChatFactory())
reactor.run()