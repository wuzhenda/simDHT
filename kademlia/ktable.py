#encoding: utf-8
from time import time
from random import randint
from bisect import bisect_left

from constants import *
from utils import intify

class BucketFull(Exception):
    pass


class KTable(object):
    def __init__(self, nid):
        self.nid = nid
        self.buckets = [ KBucket(0, 2**160) ]

    def touchBucket(self, target):
        """
        更新指定node所在bucket最后访问时间
        """
        try:
            self.buckets[self.bucketIndex(target)].touch()
        except IndexError:
            pass

    def append(self, node):
        """
        插入node
        """
        if self.nid == node.nid: return #不存储自己
        
        index = self.bucketIndex(node.nid)
        try:
            bucket = self.buckets[index]
            bucket.append(node)
        except IndexError:
            return
        except BucketFull:
            #拆表前, 先看看自身node ID是否也在该bucket里, 如果不在, 终止
            if not bucket.inRange(self.nid): return

            self.splitBucket(index)
            self.append(node)

    def findCloseNodes(self, target, n=K):
        """
        找出离目标node ID或infohash最近的前n个node
        """
        nodes = []
        if len(self.buckets) == 0: return nodes

        index = self.bucketIndex(target)
        try:
            nodes = self.buckets[index].nodes
            min = index - 1
            max = index + 1

            while len(nodes) < n and ((min >= 0) or (max < len(self.buckets))):
                #如果还能往前走
                if min >= 0:
                    nodes.extend(self.buckets[min].nodes)

                #如果还能往后走
                if max < len(self.buckets):
                    nodes.extend(self.buckets[max].nodes)

                min -= 1
                max += 1

            #按异或值从小到大排序
            num = intify(target)
            nodes.sort(lambda a, b, num=num: cmp(num^intify(a.nid), num^intify(b.nid)))
            return nodes[:n]
        except IndexError:
            return nodes

    def bucketIndex(self, target):
        """
        定位指定node ID 或 infohash 所在的bucket的索引
        """
        return bisect_left(self.buckets, intify(target))

    def splitBucket(self, index):
        """
        拆表

        index是待拆分的bucket(old bucket)的所在索引值. 
        假设这个old bucket的min:0, max:16. 拆分该old bucket的话, 分界点是8, 然后把old bucket的max改为8, min还是0. 
        创建一个新的bucket, new bucket的min=8, max=16.
        然后根据的old bucket中的各个node的nid, 看看是属于哪个bucket的范围里, 就装到对应的bucket里. 
        各回各家,各找各妈.
        new bucket的所在索引值就在old bucket后面, 即index+1, 把新的bucket插入到路由表里.        
        """
        old = self.buckets[index]
        point = old.max - (old.max - old.min)/2
        new = KBucket(point, old.max)
        old.max = point
        self.buckets.insert(index + 1, new)
        for node in old.nodes[:]:
            if new.inRange(node.nid):
                new.append(node)
                old.remove(node)

    def __iter__(self):
        for bucket in self.buckets:
            yield bucket

    def __len__(self):
        length = 0
        for bucket in self:
            length += len(bucket)
        return length

    def __contains__(self, node):
        try:
            index = self.bucketIndex(node.nid)
            return node in self.buckets[index]
        except IndexError:
            return False


class KBucket(object):
    __slots__ = ("min", "max", "nodes", "lastAccessed")

    def __init__(self, min, max):
        self.min = min
        self.max = max
        self.nodes = []
        self.lastAccessed = time()

    def append(self, node):
        """添加node"""
        if len(node.nid) != 20: return

        #如果已在该bucket里, 替换掉
        if node in self:
            self.remove(node)
            self.nodes.append(node)
        else:
            #不在该bucket并且未满, 插入
            if len(self) < K:
                self.nodes.append(node)
            #满了, 抛出异常, 通知上层代码进行拆表
            else:
                raise BucketFull

        #替换/添加node都要更改bucket最后访问时间
        self.touch()

    def remove(self, node):
        """删除节点"""
        self.nodes.remove(node)

    def touch(self):
        """更新bucket最后访问时间"""
        self.lastAccessed = time()

    def random(self):
        """随机选择一个node"""
        if len(self.nodes) == 0:
            return None
        return self.nodes[randint(0, len(self.nodes)-1)]        

    def isFresh(self):
        """bucket是否新鲜"""
        return (time() - self.lastAccessed) > BUCKET_LIFETIME

    def inRange(self, target):
        """目标node ID是否在该范围里"""
        return self.min <= intify(target) < self.max

    def __len__(self):
        return len(self.nodes)

    def __contains__(self, node):
        return node in self.nodes

    def __iter__(self):
        for node in self.nodes:
            yield node

    def __lt__(self, target):
        """
        为bisect打造, 目的是快速定位bucket的所在索引, 不需一个个循环.
        虽然一个路由表最多只能存储158个bucket, 不过追求极限是程序员的美德之一.
        """
        return self.max <= target


class KNode(object):
    __slots__ = ("nid", "ip", "port")
    
    def __init__(self, nid, ip, port):
        self.nid = nid
        self.ip = ip
        self.port = port

    def __eq__(self, other):
        return self.nid == other.nid