update 2014-9-20:
应simDHT原作者要求，在此著名出处。
此处代码fork from https://github.com/fanpei
原作者email:fanpei91@gmail.com


simDHT:
======
屎上代码最简单的DHT爬虫, 基于twisted/Kademlia, 很适合初学者学习.


依赖包:
======
1. [twisted](https://pypi.python.org/pypi/Twisted/13.2.0)
2. [bencode](https://pypi.python.org/pypi/bencode/1.0)


启动*simDHT*服务:
================
`twistd -y simDHT.py`


停止*simDHT*服务:
================
1. `cat twistd.pid`
2. `kill -9 PID`


配置文件:
========
`kademlia/constants.py`


其他:
====
1. 因只实现了DHT协议, 未实现种子下载, 所收集到的**infohash**将会存储在**infohash.log**文件中.
2. 种子下载可去迅雷种子库下载、使用[libtorrent](http://libtorrent.org)、实现种子协议([bep0003](http://www.bittorrent.org/beps/bep_0003.html), [bep0009](http://www.bittorrent.org/beps/bep_0009.html), [bep0010](http://www.bittorrent.org/beps/bep_0010.html))