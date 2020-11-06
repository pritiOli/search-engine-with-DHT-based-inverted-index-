# !/bin/python3
import sys
import threading
import json
import random
import socket
import time
import pickle
from socketImpl import *
from activeNode import *
from addr_helper import *

is_running = True



class BackGroundProcess(threading.Thread):
    def __init__(self, obj, method):
        threading.Thread.__init__(self)
        self.obj_ = obj
        self.method_ = method

    def run(self):
        getattr(self.obj_, self.method_)()

class Node(object):
    def __init__(self, localAdress, RemoteChordNodeAddress=None):
        self._address = localAdress
        self.threads = {}
        self.fingerTbl = {}
        self._predecessor = None
        self.db = {}
        for index in range(N_BITS):
            self.fingerTbl[index] = None
        self.joinChord(RemoteChordNodeAddress)

    def joinChord(self, RemoteChordNodeAddress=None):
        if RemoteChordNodeAddress:
            remoteInstance = RemoteChordNode(RemoteChordNodeAddress)
            self.fingerTbl[0] = remoteInstance.findSuccessor(self.getIdentifier())
        else:
            self.fingerTbl[0] = self  # fot the node-0

    def getIdentifier(self, offset=0):
        return (self._address.hashFn() + offset) % LIMIT

    def putKey(self, key, value):
        self.db[key] = value

    def getKeyHash(self, key):
        return hash_(key) % LIMIT

    def getKey(self, key):
        retval = self.db.get(key)
        if retval:
            return retval
        else:
            return '-1'

    def toStr(self):
        return "Node %s" % self._address



    def start(self):
        self.threads['run'] = BackGroundProcess(self, 'run')
        self.threads['fixFingers'] = BackGroundProcess(self, 'fixFingers')
        self.threads['stabilize'] = BackGroundProcess(self, 'stabilize')
        self.threads['checkPredecessor'] = BackGroundProcess(self, 'checkPredecessor')
        for key in self.threads:
            self.threads[key].start()


    # fixes the successor and predecessor
    def stabilize(self):
        while is_running:
            if self.predecessor() != None:
                print(str(self.getIdentifier()) + " :: " + "predecessor : ", self.predecessor().toStr(), "id : ",
                      self.predecessor().getIdentifier())
            if self.successor() != None:
                print(str(self.getIdentifier()) + " :: " + "successor : ", self.successor().toStr(), "id : ",
                      self.successor().getIdentifier())

            print("\n")
            suc = self.successor()

            # this if case added to handle two node case, when the system is starting up
            if suc == self and self.predecessor() != None:
                self.fingerTbl[0] = self.predecessor()

            else:
                x = suc.predecessor()
                if x != None and \
                        rangeBound(x.getIdentifier(), self.getIdentifier(), suc.getIdentifier()) and \
                        (self.getIdentifier() != suc.getIdentifier()) and \
                        (x.getIdentifier() != self.getIdentifier()) and \
                        (x.getIdentifier() != suc.getIdentifier()):
                    self.fingerTbl[0] = x
            self.successor().notify(self)
            time.sleep(SLEEP_FOR)

    # returns the first remote node object
    def successor(self):
        return self.fingerTbl[0]

    # fixes predecesor
    def notify(self, remote):
        # print(str(self.getIdentifier()) + " :: " + "notify called ", remote.toStr())
        if (self.predecessor() == None or self.predecessor() == self) or \
                ((rangeBound(remote.getIdentifier(), self.predecessor().getIdentifier(), self.getIdentifier())) and \
                 (self.predecessor().getIdentifier() != self.getIdentifier()) and \
                 (remote.getIdentifier() != self.predecessor().getIdentifier()) and \
                 (remote.getIdentifier() != self.getIdentifier())):

            self._predecessor = remote

            for key in self.db.keys():  # this key is plain word or string

                if self.getKeyHash(key) <= remote.getIdentifier():
                    remote.insertKeyVal(key, self.db[key])

    def predecessor(self):
        return self._predecessor

    def fixFingers(self):
        nxt = 0
        while is_running:
            nxt = nxt + 1
            if nxt > N_BITS:
                # self.printFingerable()
                nxt = 1
            self.fingerTbl[nxt - 1] = self.findSuccessor(self.getIdentifier(1 << (nxt - 1)))
            time.sleep(SLEEP_FOR)


    def checkPredecessor(self):
        while is_running:
            # check the predecessor is up or not
            if self.predecessor() != None:
                if self.predecessor()._address.hashFn() != self._address.hashFn():
                    if self.predecessor().nudge() == False:
                        self._predecessor = None
            time.sleep(SLEEP_FOR)

    def findSuccessor(self, id):
        # check paper for implementation

        if (rangeBound(id, self.getIdentifier(), self.successor().getIdentifier()) and \
                (self.getIdentifier() != self.successor().getIdentifier()) and \
                (id != self.getIdentifier())):

            return self.successor()
        else:
            remote = self.closestPrecedingNode(id)
            if self._address.hashFn() != remote._address.hashFn():
                return remote.findSuccessor(id)
            else:
                return self

    def closestPrecedingNode(self, id):
        for idx in reversed(range(N_BITS)):
            if self.fingerTbl[idx] != None and \
                    (rangeBound(self.fingerTbl[idx].getIdentifier(), self.getIdentifier(), id) and \
                     (self.getIdentifier() != id) and \
                     (self.fingerTbl[idx].getIdentifier() != self.getIdentifier()) and \
                     (self.fingerTbl[idx].getIdentifier() != id)):
                return self.fingerTbl[idx]

        return self

    def lookUpKey(self, key):
        print("LOOK UP for key:",key)
        ret = self.getKey(key)
        if(ret!='-1'):
            print("FOUND")
        else:
            print("NOT FOUND")
        return ret

    def insertKeyVal(self, key, value):
        # print("INSERT key:",key,":: value")
        self.putKey(key, value)

    def run(self):

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((self._address.ip, int(self._address.port)))
        self._socket.listen(10)

        while 1:
            try:
                conn, addr = self._socket.accept()
            except socket.error:
                print("accept failed")

            request = read_socket_data(conn)  # it might receive nudge request

            if request:

                msg = request.split()

                command = msg[0]  # gets the instruction in english
                request = request[len(command) + 1:]  # get the arguiment for the instruction

                # defaul : "" = not respond anything
                result = json.dumps("")

                if command == 'insertKeyVal':
                    key = msg[1]
                    val =msg[2:]

                    value = " ".join(val)  # value could be of multiple words
                    hashkey = self.getKeyHash(key)
                    # print("Request for hashKey : ", hashkey, " Found!")
                    node = self.findSuccessor(hashkey)
                    # print("Destination Node addr : ", node._address, " id: ", node.getIdentifier())
                    if node.getIdentifier() == self.getIdentifier():
                        self.insertKeyVal(key, value)
                    else:
                        node.insertKeyVal(key, value)

                    result = "INSERTED"

                if command == 'finalInsertKeyVal':
                    key = msg[1]
                    value = " ".join(msg[2:])  # value could be of multiple words
                    self.insertKeyVal(key, value)
                    result = "INSERTED"

                if command == 'lookUpKey':
                    key = msg[1]
                    hashkey = self.getKeyHash(key)

                    # print("Request for hashKey : ", hashkey, " Found!")

                    node = self.findSuccessor(hashkey)
                    print("Destination Node addr : ", node._address, " id: ", node.getIdentifier())
                    if node.getIdentifier() == self.getIdentifier():
                        response = self.lookUpKey(key)
                    else:
                        response = node.lookUpKey(key)

                    result = response

                if command == 'finalLookUpKey':
                    key = msg[1]
                    response = self.lookUpKey(key)
                    result = response


                if command == 'successor':
                    successor = self.successor()
                    result = json.dumps((successor._address.ip, successor._address.port))

                if command == 'getPredecessor':
                    if self._predecessor != None:
                        predecessor = self.predecessor()
                        result = json.dumps((predecessor._address.ip, predecessor._address.port))

                if command == 'findSuccessor':
                    successor = self.findSuccessor(int(request))
                    result = json.dumps((successor._address.ip, successor._address.port))

                if command == 'closestPrecedingNode':
                    closest = self.closestPrecedingNode(int(request))
                    result = json.dumps((closest._address.ip, closest._address.port))

                if command == 'notify':
                    npredecessor = NodeAddress(request.split(' ')[0], int(request.split(' ')[1]))
                    self.notify(RemoteChordNode(npredecessor))

                send_socket_data(conn, result)



if __name__ == "__main__":

    if len(sys.argv) == 2:
        local = Node(NodeAddress("127.0.0.1", sys.argv[1]))
    else:
        local = Node(NodeAddress("127.0.0.1", sys.argv[1]), NodeAddress("127.0.0.1", sys.argv[2]))
    local.start()