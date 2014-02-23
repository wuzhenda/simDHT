#encoding: utf-8
import socket

from twisted.internet import protocol
from bencode import bencode, bdecode, BTL

from constants import *

class KRPC(protocol.DatagramProtocol):    
    def __init__(self):
        self.actionSwitch = {
            "r": self.responseReceived,
            "q": self.queryReceived,
            "e": self.errorReceived,
        }

        self.queryActions = {
            "ping": self.pingReceived,
            "find_node": self.findNodeReceived,
            "get_peers": self.getPeersReceived,
            "announce_peer": self.announcePeerReceived,
        }

    def datagramReceived(self, data, address):
        """
        数据接收
        """
        try:
            res = bdecode(data)
            self.actionSwitch[res["y"]](res, address)     
        except(BTL.BTFailure, KeyError):
            pass

    def sendKRPC(self, msg, address):
        """
        发送数据
        """
        try:
            self.transport.write(bencode(msg), address)
        except socket.error:
            pass

    def sendQuery(self, msg, address):
        """发送请求类型数据"""
        self.sendKRPC(msg, address)

    def sendResponse(self, msg, address):
        """发送回应类型数据"""
        self.sendKRPC(msg, address)

    def queryReceived(self, res, address):
        """
        收到请求类型的数据后, 智能调用DHT服务器端相关处理函数
        """
        try:
            self.queryActions[res["q"]](res, address)        
        except KeyError:
            pass

    def responseReceived(self, res, address):
        """
        收到请求类型的数据, 直接调用处理find_node回应的方法即可, 
        因为爬虫客户端只实现了find_node请求.
        """
        try:
            self.findNodeHandle(res)
        except KeyError:
            pass

    def errorReceived(self, res, address):
        """收到错误回应, 忽略"""
        pass