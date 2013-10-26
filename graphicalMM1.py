#!/usr/bin/env python
from __future__ import division
from turtle import Turtle, mainloop
from random import expovariate as randexp
import sys

def mean(lst):
    return sum(lst) / len(lst)

def movingaverage(lst):
    """
    Custom built function to obtain moving average
    """
    return [mean(lst[:k]) for k in range(1 , len(lst) + 1)]

class Player(Turtle):
    def __init__(self, lmbda, mu, queue, server):
        Turtle.__init__(self)
        self.interarrivaltime = randexp(lmbda)
        self.servicetime = randexp(mu)
        self.queue = queue
        self.server = server
        self.shape('circle')
        self.served = False
    def move(self, x, y):
        self.setx(x)
        self.sety(y)
    def arrive(self, t):
        self.penup()
        self.arrivaldate = t
        self.move(self.queue.position[0], self.queue.position[1])
        self.color('red')
    def joinqueue(self):
        self.move(self.queue.position[0] + 5, self.queue.position[1])
        self.color('blue')
        self.queue.join(self)
    def startservice(self, t):
        if not self.served:
            self.move(self.server.position[0], self.server.position[1])
            self.servicedate = t + self.servicetime
            self.server.start(self)
            self.color('green')
            self.endqueuedate = t
    def endservice(self):
        self.move(self.server.position[0] + 50, self.server.position[1] - 50)
        self.color('black')
        self.server.players = self.server.players[1:]
        self.endservicedate = self.endqueuedate + self.servicetime
        self.waitingtime = self.endqueuedate - self.arrivaldate
        self.served = True


class Queue():
    def __init__(self, qposition):
        self.players = []
        self.position = qposition
    def __iter__(self):
        return iter(self.players)
    def __len__(self):
        return len(self.players)
    def pop(self, index):
        for p in self.players[:index] + self.players[index + 1:]:  # Shift everyone up one queue spot
            x = p.position()[0]
            y = p.position()[1]
            p.move(x + 10, y)
        self.position[0] += 10  # Reset queue position for next arrivals
        return self.players.pop(index)
    def join(self, player):
        self.players.append(player)
        self.position[0] -= 10

class Server():
    def __init__(self, svrposition):
        self.players = []
        self.position = svrposition
    def __iter__(self):
        return iter(self.players)
    def __len__(self):
        return len(self.players)
    def start(self,player):
        self.players.append(player)
        self.players = sorted(self.players, key = lambda x : x.servicedate)
        self.nextservicedate =  self.players[0].servicedate
    def free(self):
        return len(self.players) == 0

class Sim():
    def __init__(self, T, lmbda, mu, qposition=[200,-200]):
        self.T = T
        self.lmbda = lmbda
        self.mu = mu
        self.queue = Queue(qposition)
        self.server = Server([qposition[0] + 50, qposition[1]])
        self.completed = []
        self.queuelengthdict = {}
        self.systemstatedict = {}
    def run(self):
        t = 0
        self.players = [Player(self.lmbda, self.mu, self.queue, self.server)]
        nextplayer = self.players.pop()
        nextplayer.arrive(t)
        nextplayer.joinqueue()
        while t < self.T:
            t += 1
            # Print progress to screen:
            sys.stdout.write('\r%.2f%% of simulation completed (t=%s of %s)' % (100 * t/self.T, t, self.T))
            sys.stdout.flush()
            if self.server.free():  # Check if server is free
                if len(self.queue) == 0 and t > nextplayer.arrivaldate:
                    nextplayer.startservice(t)
                else:
                    nextservice = self.queue.pop(0)
                    nextservice.startservice(t)
                self.players.append(Player(self.lmbda, self.mu, self.queue, self.server))
            elif t > self.server.nextservicedate:
                self.completed.append(self.server.players[0])
                self.server.players[0].endservice()
                self.players.append(Player(self.lmbda, self.mu, self.queue, self.server))
            if self.players and t > self.players[-1].interarrivaltime + nextplayer.arrivaldate:
                nextplayer = self.players.pop()
                nextplayer.arrive(t)
                nextplayer.joinqueue()
                self.players.append(Player(self.lmbda, self.mu, self.queue, self.server))
            self.queuelengthdict[t] = len(self.queue)
            if self.server.free():
                self.systemstatedict[t] = 0
            else:
                self.systemstatedict[t] = self.queuelengthdict[t] + 1

    def plot(self, warmup=0):
        queuelengths = []
        systemstates = []
        timepoints = []
        for t in self.queuelengthdict:
            if t >= warmup:
                queuelengths.append(self.queuelengthdict[t])
                systemstates.append(self.systemstatedict[t])
                timepoints.append(t)
        import matplotlib.pyplot as plt
        plt.figure(1)
        plt.subplot(221)
        plt.hist(queuelengths, normed=True)
        plt.title("Queue length")
        plt.subplot(222)
        plt.hist(systemstates, normed=True)
        plt.title("System state")
        plt.subplot(223)
        plt.plot(timepoints, movingaverage(queuelengths))
        plt.title("Mean queue length")
        plt.subplot(224)
        plt.plot(timepoints, movingaverage(systemstates))
        plt.title("Mean system state")
        plt.show()

if __name__ == '__main__':
    q = Sim(200, .5, 1)
    q.run()
    q.plot()
