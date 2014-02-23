#encoding: utf-8
from hashlib import sha1
from random import randint
from struct import pack, unpack

def entropy(bytes):
    """随机生成字符串"""
    s = ""
    for i in range(bytes):
        s += chr(randint(0, 255))
    return s

def intify(hstr):
    """把20字节的hash值转换为数字"""
    assert len(hstr) == 20
    return long(hstr.encode('hex'), 16)

def nodeID():
    """生成node ID"""
    hash = sha1()
    hash.update( entropy(20) )
    return hash.digest()

def dottedQuadToNum(ip):
    """把ipv4转换为4字节整型"""
    hexn = ''.join(["%02X" % long(i) for i in ip.split('.')])
    return long(hexn, 16)

def numToDottedQuad(n):
    """把4字节整型转换为ipv4"""
    d = 256 * 256 * 256
    q = []
    while d > 0:
        m, n = divmod(n, d)
        q.append(str(m))
        d /= 256
    return '.'.join(q)

def decodeNodes(nodes):
    """
    把收到的nodes转成例表. 
    数据格式: [ (node ID, ip, port),(node ID, ip, port),(node ID, ip, port).... ] 
    """
    n = []
    nrnodes = len(nodes) / 26
    nodes = unpack("!" + "20sIH" * nrnodes, nodes)
    for i in xrange(nrnodes):
        nid, ip, port = nodes[i * 3], numToDottedQuad(nodes[i * 3 + 1]), nodes[i * 3 + 2]
        n.append((nid, ip, port))
    return n

def encodeNodes(nodes):
    """
    "编码"nodes 与decodeNodes相反
    """
    n = []
    for node in nodes:
        n.extend([node.nid, dottedQuadToNum(node.ip), node.port])
    return pack("!" + "20sIH" * len(nodes), *n)