
import json
import socket


import threading
from conf import *
from socketImpl import *
from addr_helper import *

def socket_connection(func):
	def inner(self, *args, **kwargs):
		self.mtx.acquire()
		self.establish_connection()
		temp = func(self, *args, **kwargs)
		self.close_connection()
		self.mtx.release()
		return temp
	return inner


class RemoteChordNode(object):
	def __init__(self, RemoteChordNodeAddress = None):
		self._address = RemoteChordNodeAddress
		self.mtx = threading.Lock()

	def establish_connection(self):
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.connect((self._address.ip, self._address.port))

	def close_connection(self):
		self._socket.close()
		self._socket = None

	def toStr(self):
		return "Remote %s" % self._address # this _address object has already 

	def getIdentifier(self, offset = 0):
		return (self._address.hashFn() + offset) % LIMIT

	def send(self, msg):
		send_socket_data(self._socket,msg)
		self.last_msg_send_ = msg

	def recv(self):
		return read_socket_data(self._socket)

	def nudge(self):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((self._address.ip, self._address.port))
			st = "\r\n"
			s.sendall(st.encode('utf-8')) 	# this a dummy string:
								# we have used this all over the place
			s.close()
			return True
		except socket.error:
			return False

	@socket_connection
	def findSuccessor(self,id): # this is not successor # ID is there
		self.send('findSuccessor %s' % id)
		response = self.recv()
		response = json.loads(response)
		addr = NodeAddress(response[0], response[1])
		return RemoteChordNode(addr)

	@socket_connection
	def successor(self):
		self.send('successor')
		response = self.recv()
		response = json.loads(self.recv())
		addr = NodeAddress(response[0], response[1])
		return RemoteChordNode(addr)


	@socket_connection
	def predecessor(self):
		self.send('getPredecessor')
		response = self.recv()
		response = json.loads(response)
		addr = NodeAddress(response[0], response[1])
		return RemoteChordNode(addr)


	@socket_connection
	def closestPrecedingNode(self, id):
		self.send('closestPrecedingNode %s' % id)
		response = self.recv()
		response = json.loads(response)
		addr = NodeAddress(response[0], response[1])
		return RemoteChordNode(addr)

	@socket_connection
	def notify(self, node):
		self.send('notify %s %s' % (node._address.ip, node._address.port))

	@socket_connection
	def lookUpKey(self,key):
		self.send('finalLookUpKey %s' % key)
		response = self.recv()
		return response

	@socket_connection
	def insertKeyVal(self,key,value):
		self.send('finalInsertKeyVal '+key+' '+value)
		response = self.recv()
		return response