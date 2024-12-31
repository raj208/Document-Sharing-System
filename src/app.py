from web3 import Web3, HTTPProvider
from flask import Flask, render_template, redirect, request, session
import json
from werkzeug.utils import secure_filename
import os
import hashlib

def hash_file(filename):
    h = hashlib.sha1()
    with open(filename, 'rb') as file:
        chunk = 0
        while chunk != b'':
            chunk = file.read(1024)
            h.update(chunk)
    return h.hexdigest()

# Connect to Ethereum Network (Ganache)
web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
if web3.isConnected():
    print("Connected to Ganache")
else:
    print("Connection failed")

def connect_with_register_blockchain(acc):
    blockchainServer = 'http://127.0.0.1:7545'
    web3 = Web3(HTTPProvider(blockchainServer))
    if acc == 0:
        acc = web3.eth.accounts[0]
    web3.eth.defaultAccount = acc
    artifact_path = '../build/contracts/register.json'
    with open(artifact_path) as f:
        contract_json = json.load(f)
        contract_abi = contract_json['abi']
        contract_address = contract_json['networks']['5777']['address']
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    return contract, web3

def connect_with_file_blockchain(acc):
    blockchainServer = 'http://127.0.0.1:7545'
    web3 = Web3(HTTPProvider(blockchainServer))
    if acc == 0:
        acc = web3.eth.accounts[0]
    web3.eth.defaultAccount = acc
    artifact_path = '../build/contracts/file.json'
    with open(artifact_path) as f:
        contract_json = json.load(f)
        contract_abi = contract_json['abi']
        contract_address = contract_json['networks']['5777']['address']
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    return contract, web3

app = Flask(__name__)
app.secret_key = 'sacetc8'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

@app.route('/')
def homePage():
    return render_template('register.html')

@app.route('/login')
def loginPage():
    return render_template('index.html')

@app.route('/registerUser', methods=['POST'])
def registerUser():
    walletaddr = request.form.get('walletaddr')
    password = request.form.get('password')
    
    # Basic input validation
    if not walletaddr or not password:
        return render_template('register.html', err='Please fill in all fields')
    
    # Validate wallet address format
    if not Web3.isAddress(walletaddr):
        return render_template('register.html', err='Invalid wallet address format')
    
    try:
        contract, web3 = connect_with_register_blockchain(0)
        print("Connected to blockchain:", contract.address)
    except Exception as e:
        print(f"Blockchain connection error: {e}")
        return render_template('register.html', err="Blockchain connection failed")
    
    try:
        # Attempt to register user
        tx_hash = contract.functions.registerUser(walletaddr, int(password)).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        
        print("Registration successful")
        return redirect('/login')
    
    except ValueError as e:
        error_msg = str(e)
        print(f"Smart contract execution error: {error_msg}")
        
        # Check if the error is due to an already registered user
        if "revert" in error_msg and "already registered" in error_msg:
            return render_template('register.html', err="User already registered")
        else:
            return render_template('register.html', err="Invalid registration details or an unknown error occurred")
    
    except Exception as e:
        print(f"Unexpected error during registration: {e}")
        return render_template('register.html', err="An unknown error occurred during registration")

@app.route('/loginUser', methods=['POST'])
def loginUser():
    walletaddr = request.form['walletaddr']
    password = request.form['password']
    print(walletaddr, password)
    contract, web3 = connect_with_register_blockchain(0)
    try:
        state = contract.functions.loginUser(walletaddr, int(password)).call()
        if state == True:
            session['username'] = walletaddr
            return redirect('/dashboard')
        else:
            return render_template('index.html', err='Invalid Credentials')
    except:
        return render_template('index.html', err='No Account')

@app.route('/dashboard')
def dashboardPage():
    return render_template('dashboard.html')

@app.route('/uploadFile', methods=['POST', 'GET'])
def uploadFile():
    doc = request.files['chooseFile']
    if session['username'] not in os.listdir(app.config['UPLOAD_FOLDER']):
        os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], session['username']))
    doc1 = secure_filename(doc.filename)
    doc.save(os.path.join(app.config['UPLOAD_FOLDER'], session['username'] + '/' + doc1))
    hashid = hash_file(os.path.join(app.config['UPLOAD_FOLDER'], session['username'] + '/' + doc1))
    print(hashid)
    try:
        contract, web3 = connect_with_file_blockchain(0)
        tx_hash = contract.functions.addFile(session['username'], os.path.join(app.config['UPLOAD_FOLDER'], session['username'] + '/' + doc1), hashid).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)
        return render_template('dashboard.html', res='File uploaded successfully')
    except:
        return render_template('dashboard.html', res='File already uploaded')

@app.route('/mydocuments')
def mydocuments():
    try:
        k = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], session['username']))
        data = []
        for i in k:
            dummy = []
            dummy.append(os.path.join(app.config['UPLOAD_FOLDER'], session['username']) + '/' + i)
            data.append(dummy)
    except:
        data = []
    return render_template('mydocuments.html', dashboard_data=data, len=len(data))

@app.route('/sharedocument')
def sharedocument():
    data = []
    data1 = []
    contract, web3 = connect_with_register_blockchain(0)
    _usernames, _passwords = contract.functions.viewUsers().call()
    for i in range(len(_usernames)):
        dummy = []
        if _usernames[i] != session['username']:
            dummy.append(_usernames[i])
            data.append(dummy)
    
    try:
        k = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], session['username']))
    except:
        k = []
    for i in k:
        dummy = []
        dummy.append(os.path.join(app.config['UPLOAD_FOLDER'], session['username']) + '/' + i)
        data1.append(dummy)
    
    return render_template('sharedocument.html', dashboard_data=data, dashboard_data1=data1, len=len(data), len1=len(data1))

@app.route('/toShare', methods=['POST'])
def toShare():
    flag = 0
    userId = request.form['userId']
    docId = request.form['docID']
    hashid = hash_file(docId)
    contract, web3 = connect_with_file_blockchain(0)
    _users, _names, _files, _tokens = contract.functions.viewFiles().call()
    
    for i in range(len(_files)):
        if hashid == _files[i]:
            if userId in _tokens[i]:
                flag = 1
                break
    
    if flag == 0:
        tx_hash = contract.functions.addToken(hashid, userId).transact()
        web3.eth.waitForTransactionReceipt(tx_hash)

    data = []
    data1 = []
    contract, web3 = connect_with_register_blockchain(0)
    _usernames, _passwords = contract.functions.viewUsers().call()
    for i in range(len(_usernames)):
        dummy = []
        if _usernames[i] != session['username']:
            dummy.append(_usernames[i])
            data.append(dummy)

    try:
        k = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], session['username']))
    except:
        k = []
    for i in k:
        dummy = []
        dummy.append(os.path.join(app.config['UPLOAD_FOLDER'], session['username']) + '/' + i)
        data1.append(dummy)

    if flag == 1:
        return render_template('sharedocument.html', err='Document already shared', dashboard_data=data, dashboard_data1=data1, len=len(data), len1=len(data1))
    else:
        return render_template('sharedocument.html', res='Document Shared', dashboard_data=data, dashboard_data1=data1, len=len(data), len1=len(data1))

@app.route('/shareddocuments')
def shareddocuments():
    data = []
    contract, web3 = connect_with_file_blockchain(0)
    _users, _names, _files, _tokens = contract.functions.viewFiles().call()
    for i in range(len(_names)):
        if session['username'] in _tokens[i][1:]:
            dummy = []
            dummy.append(_tokens[i][0])
            dummy.append(_names[i])
            data.append(dummy)
    
    return render_template('shareddocuments.html', dashboard_data=data, len=len(data))

@app.route('/myshareddocuments')
def myshareddocuments():
    contract, web3 = connect_with_file_blockchain(0)
    _users, _names, _files, _tokens = contract.functions.viewFiles().call()
    data = []
    for i in range(len(_names)):
        if _users[i] == session['username']:
            for j in _tokens[i]:
                if j != session['username'] and j != '0x0000000000000000000000000000000000000000':
                    dummy = []
                    dummy.append(_names[i])
                    dummy.append(j)
                    data.append(dummy)
    
    return render_template('myshareddocuments.html', dashboard_data=data, len=len(data))

@app.route('/cancel/static/uploads/<id1>/<id2>/<id3>')
def cancelDocument(id1, id2, id3):
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], id1 + '/' + id2 + '/' + id3))
    return redirect('/mydocuments')

if __name__ == '__main__':
    app.run(debug=True)
