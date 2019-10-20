import hashlib
import datetime
import pickle
import json
from flask import Flask, jsonify, render_template
from flask_classful import FlaskView, route
import requests

gdata = []
app = Flask(__name__)
def update(newblock):
    mychain.chain.append(newblock)

class block():

    def __init__(self, index, data, previous_hash, timestamp):
        self.index = index
        self.data = data
        self.nonce = 0
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        sha = hashlib.sha1()
        sha.update((str(self.data) +
                    str(self.timestamp) +
                    str(self.previous_hash) +
                    str(self.nonce) +
                    str(self.index)
                    ).encode('utf-8'))
        return sha.hexdigest()

    def mine_block(self, difficulty):
        while (self.hash[:difficulty] != '0' * difficulty):
            self.nonce = self.nonce + 1
            self.hash = self.calculate_hash()
        print("Mined block: ", self.hash)
        return self.hash

    def check_if_mined(self, difficulty):
        newhash = ""
        self.nonce = 0
        while (newhash[:difficulty] != '0' * difficulty):
            self.nonce = self.nonce + 1
            newhash = self.calculate_hash()
        return newhash


class Blockchain():

    def __init__(self):
        self.difficulty = 3
        self.chain = []
        self.nodes=['127.0.0.1:5002']
        self.createGenesis()

    def createGenesis(self):
        g=block(0, "genesis block", "0", datetime.datetime.now())
        g.mine_block(3)
        self.chain.append(g)

    def getLatestBlock(self):
        return self.chain[-1]

@app.route('/verify/<id>/<pwd>')
def verify(id, pwd):
    f = open("lgnid.txt", "r")
    l = []
    y = []
    flag = 0
    for x in f.readlines():
        a = x.rstrip()
        l.append(a.split(":")[0])  # list of ip addresses
        y.append(a.split(":")[1])
    if id in l:
        index = l.index(id)
        if y[index] == pwd:
            flag = 1
    f.close()
    if flag == 1:
        return render_template("entry.html")
    else:
        return render_template("login.html")


mychain = Blockchain()
with open("Blkchn.txt", "rb") as f:
    mychain.chain=pickle.load(f)

'''mychain.addblock(block(0,"zero Block" ,"0",datetime.datetime.now()))	 
mychain.addblock(block(1,"1zero Block" ,"0",datetime.datetime.now()))'''


# mychain.print_chain()
# mychain.chain[1].data="vtd"
# mychain.print_chain()
# mychain.check_if_valid()

@app.route('/storedata/<int:eid>/<int:mid>/<int:pid>/<int:hid>/<int:cid>')
def storedata(eid, mid, pid, hid,cid):
    global gdata
    data = {"eid": eid, "mid": mid, "pid": pid, "hid": hid,"cid":cid}
    gdata.append(data)
    return render_template("entry.html")


@app.route('/print_chain')
def print_chain():
    res = []
    for i in range(0, len(mychain.chain)):
        y = {"index": '', 'data': '', "timestamp": "", "previous_hash": "", "hash": "", "nonce": ""}

        y['index'] = (mychain.chain[i].index)
        print(mychain.chain[i].index)

        y['data'] = mychain.chain[i].data
        print(mychain.chain[i].data)
        y['timestamp'] = mychain.chain[i].timestamp
        y['previous_hash'] = mychain.chain[i].previous_hash
        y['hash'] = mychain.chain[i].hash
        y['nonce'] = mychain.chain[i].nonce
        res.append(y)
    return render_template('result.html', value=res)


@app.route('/addblock')
def addblock():
    global gdata
    newblock = block(index=len(mychain.chain), data=gdata, timestamp=datetime.datetime.now(), previous_hash="")

    newblock.previous_hash = mychain.getLatestBlock().hash
    newblock.mine_block(mychain.difficulty)
    mychain.chain.append(newblock)
    gdata = []
    with open("Blkchn.txt", "wb") as f:
        pickle.dump(mychain.chain, f)
    return render_template("entry.html")


@app.route('/check_if_valid')
def check_if_valid():
    for i in range(1, len(mychain.chain)):
        if (mychain.chain[i].hash != mychain.chain[i].check_if_mined(mychain.difficulty)):
            print("Current hash :", mychain.chain[i].hash, " does not match ",
                  mychain.chain[i].check_if_mined(mychain.difficulty))
            return ("False")
        elif (mychain.chain[i].previous_hash != mychain.chain[i - 1].hash):
            print("Previous hash :", mychain.chain[i - 1].hash, " does not match with attribute prev hash ",
                  mychain.chain[i].previous_hash)
            return ("False")
    return 'True'
app.run(host='127.0.0.1', port=5001)
