#!/usr/bin/env python
# -*- coding: utf-8 -*-

import signal

def handler(signum, frame):
    #print "Signal %d recu" % signum
    print 'Signal handler called with signal', signum
#    signal.alarm(0)


print "signal.SIGALRM   : %d" % signal.SIGALRM
print "signal.SIGVTALRM : %d" % signal.SIGVTALRM
print "signal.SIGPROF   : %d" % signal.SIGPROF
print "-------------------------------------"

# pour faire un timeout d'attente
#signal.signal(signal.SIGALRM, handler)
#signal.alarm(5)

signal.signal(signal.SIGALRM, handler)
signal.signal(signal.SIGVTALRM, handler)
signal.signal(signal.SIGPROF, handler)

signal.setitimer(signal.ITIMER_VIRTUAL, 1)
#signal.setitimer(signal.ITIMER_PROF, 2)
#signal.setitimer(signal.ITIMER_REAL, 3)
#signal.alarm(3)

#import time

flags = True
count = 1
while flags:
    #time.sleep(1)
    tmp = 0
    for i in range(10000):
        tmp *= i
#    for i in [signal.ITIMER_VIRTUAL, signal.ITIMER_PROF, signal.ITIMER_REAL]:
#        print "> %d : %.2f" % (i, signal.getitimer(i)[0])
    count += 1
    if count > 10000:
        flags = False
print "fin du programme"
