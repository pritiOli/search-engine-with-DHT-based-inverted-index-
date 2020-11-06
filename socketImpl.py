

def read_socket_data(skt):
	final_data = ""
	while 1:
		recvd = skt.recv(1024)
		recvd = recvd.decode('utf-8')
		print(recvd)
		if recvd[-2:] == "\r\n":
			final_data += recvd[:-2]
			break
		final_data += recvd
	return final_data

# add \r\n to help find the end of message
def send_socket_data(skt, mesg):
	recvd = str(mesg) + "\r\n"
	skt.sendall(recvd.encode('utf-8'))
