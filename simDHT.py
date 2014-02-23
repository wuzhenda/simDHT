#encoding: utf-8
from twisted.application import service, internet

from kademlia.ktable import KTable
from kademlia.kdht import DHTServer
from kademlia.utils import nodeID
from kademlia.constants import NODE_COUNT

class simDHT(object):
    def __init__(self, f):
        self.table = KTable(nodeID())
        self.f = f

    def downloadTorrent(self, ip, port, infohash):
        """
        种子下载, 可以通过迅雷种子, 种子协议, libtorrent下载
        """
        self.f.write("%s %s %s\n" % (ip, port, infohash.encode("hex")))
        self.f.flush()        

application = service.Application("fastbot")
f = open("infohash.log", "w")
for i in range(NODE_COUNT): internet.UDPServer(0, DHTServer(simDHT(f))).setServiceParent(application)