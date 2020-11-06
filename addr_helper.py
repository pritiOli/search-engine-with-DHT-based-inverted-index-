from conf import *
from hash import *


# check if a key is within the range
def rangeBound(z, x, y):
	x = x % LIMIT
	y = y % LIMIT
	z = z % LIMIT
	if x < y:
		return x <= z and z < y
	return x <= z or z < y

class NodeAddress:
	def __init__(self,*args):
		self.ip = args[0]
		self.port = int(args[1])

	def toStr(self):
		return "[\"%s\", %s]" % (self.ip, self.port)

	def hashFn(self):
		return hash_(("%s:%s" % (self.ip, self.port))) % LIMIT
