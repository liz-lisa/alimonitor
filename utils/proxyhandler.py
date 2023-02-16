import random


def formatProxy(_ip):
    _ip = _ip.split(":")

    if len(_ip) == 2:  # if IP proxy
        _ip = {
            "http": f'http://{_ip[0]}:{_ip[1]}',
            "https": f'http://{_ip[0]}:{_ip[1]}'
        }

    else:
        _ip = {
            "http": f'http://{_ip[2]}:{_ip[3]}@{_ip[0]}:{_ip[1]}',
            "https": f'http://{_ip[2]}:{_ip[3]}@{_ip[0]}:{_ip[1]}'
        }
    return _ip


def readProxyFile(path):
    with open(path) as f:
        proxyfile = f.read().splitlines()

    _list = []
    for proxy in proxyfile:
        _list.append(formatProxy(proxy))

    return _list


def getProxy():
    return random.choice(proxylist)


proxylist = readProxyFile("proxies.txt")