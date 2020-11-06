from flask import Flask, flash, redirect, render_template, request, session, abort
import preprocessor as preprocessor
import ranking as ranking
import json
import pickle
import os


import socket
from socketImpl import *
from addr_helper import *

queryNode = None
def socket_connection(func):
    def inner(self, *args, **kwargs):
        self.establish_connection()
        f = func(self, *args, **kwargs)
        self.close_connection()
        return f
    return inner


class Node(object):
    def __init__(self, RemoteChordNodeAddress=None):
        if RemoteChordNodeAddress == None:
            print("Please enter at least one valid Chord Node address !")
            exit(-1)
        self._serverNodeAddress = RemoteChordNodeAddress
        self.client_running = True

    def establish_connection(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._serverNodeAddress.ip, self._serverNodeAddress.port))

    def recv(self):
        return read_socket_data(self._socket)

    def close_connection(self):
        self._socket.close()
        self._socket = None

    def send(self, msg):
        # self._socket.sendall(msg + "\r\n")
        send_socket_data(self._socket, msg)
        self.last_msg_send_ = msg


    @socket_connection
    def lookUpKey(self, key):
        self.send('lookUpKey ' + key)
        return self.recv()

    @socket_connection
    def insertKeyVal(self, key, value):
        self.send('insertKeyVal ' + key + ' ' + str(value))
        return self.recv()

    def load_dict(self,fileName):
        file = open(fileName,'rb')
        data=pickle.load(file)
        keys = data.keys()
        for key in keys:
            value = data[key]
            self.insertKeyVal(key, value)


    def look_up(self,key):
        returnvalue = self.lookUpKey(key)
        if returnvalue == '-1':
            print("Key :", key, " not found !!")
        else:
            print("Key : ", key, " :: Value : ", returnvalue)
            return returnvalue

app = Flask(__name__)

with open('file_url.pickle','rb') as pick:
    file_to_url = pickle.load(pick)

@app.route("/")
def root():
    return render_template('index.html')

@app.route("/search",methods=['POST'])
def search():
    global file_to_url
    query = request.form['qBox']
    preproceed_query=preprocessor.preprocess(query)
    print(' query ==> '+preproceed_query)
    top_result = []
    lookup=eval(queryNode.lookUpKey(query))
    tokens = preproceed_query.split()
    if(tokens!='' and lookup!=[]):
        for token in tokens:
            ranking.__query(token,lookup)
        ranked_docs=ranking.rank_docs()
        ranked_docs_sorted = sorted(ranked_docs.items(), key=lambda x: x[1], reverse=True)[:100]
        for doc in ranked_docs_sorted:
            top_result.append(file_to_url[doc[0]])
    return render_template('search_result.html',value=top_result, query=query)

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        queryNode = Node(NodeAddress(sys.argv[1], sys.argv[2]))
        queryNode.load_dict("index.pickle")
    else:
        print("Insufficient argumrnts")

    app.run(host='127.0.0.1', port=8000)
