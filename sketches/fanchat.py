
from json import loads, dumps

from zope.interface.common.mapping import IMapping

from twisted.internet.endpoints import serverFromString
from twisted.internet.defer import Deferred, inlineCallbacks
from tubes.itube import IFrame
from tubes.tube import receiver, series
from tubes.framing import bytesToLines, linesToBytes
from tubes.listening import Listener, Flow
from tubes.protocol import flowFountFromEndpoint

from tubes.test.test_chatter import Hub




@receiver(IFrame, IMapping)
def linesToCommands(line):
    yield loads(line)



@receiver(IMapping, IFrame)
def commandsToLines(message):
    yield dumps(message).encode("ascii")



@inlineCallbacks
def main(reactor, port="stdio:"):
    endpoint = serverFromString(reactor, port)
    flowFount = yield flowFountFromEndpoint(endpoint)
    hub = Hub()
    def newBytesFlow(flow):
        hub.newParticipantFlow(Flow(
            flow.fount.flowTo(series(bytesToLines(), linesToCommands)),
            series(commandsToLines, linesToBytes(), flow.drain)
        ))
    flowFount.flowTo(Listener(newBytesFlow))
    yield Deferred()



from twisted.internet.task import react
from sys import argv
react(main, argv[1:])
