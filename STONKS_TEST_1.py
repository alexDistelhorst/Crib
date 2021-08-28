from time import time
import hashlib
import json
from textwrap import dedent
from uuid import uuid4
import jsonpickle
from flask import Flask
from urllib.parse import urlparse
from datetime import datetime
import requests
import RSA




class Blockchain (object):
	def __init__(self):
		self.chain = [self.addGenesisBlock()]
		self.pendingTransactions = []
		self.difficulty = 2
		self.minerRewards = 50
		self.blockSize = 10
		self.nodes = set()

	def register_node(self, address):
		parsedUrl = urlparse(address)
		self.nodes.add(parsedUrl.netloc)

	def resolveConflicts(self):
		neighbors = self.nodes
		newChain = None

		maxLength = len(self.chain)

		for node in neighbors:
			response = requests.get(f'http://{node}/chain')

			if response.status_code == 200:
				length = response.json()['length']
				chain = response.json()['chain']

				if length > maxLength and self.isValidChain():
					maxLength = length
					newChain = chain

		if newChain:
			self.chain = self.chainJSONdecode(newChain)
			print(self.chain)
			return True

		return False

	def minePendingTransactions(self, miner):
		
		lenPT = len(self.pendingTransactions)
		if(lenPT <= 1):
			print("Not enough transactions to mine! (Must be > 1)")
			return False
		else:
			for i in range(0, lenPT, self.blockSize):

				end = i + self.blockSize
				if i >= lenPT:
					end = lenPT
				
				transactionSlice = self.pendingTransactions[i:end]

				newBlock = Block(transactionSlice, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), len(self.chain))
				#print(type(self.getLastBlock()));

				hashVal = self.getLastBlock().hash
				newBlock.prev = hashVal
				newBlock.mineBlock(self.difficulty)
				self.chain.append(newBlock)
			print("Mining Transactions Success!")

			payMiner = Transaction("Miner Rewards", miner, self.minerRewards)
			self.pendingTransactions = [payMiner]
		return True

	def addTransaction(self, sender, reciever, amt, keyString, senderKey):
		keyByte = keyString.encode("ASCII")
		senderKeyByte = senderKey.encode("ASCII")

		#print(type(keyByte), keyByte);

		key = RSA.import_key(keyByte)
		senderKey = RSA.import_key(senderKeyByte)

		if not sender or not reciever or not amt:
			print("transaction error 1")
			return False

		transaction = Transaction(sender, reciever, amt)

		transaction.signTransaction(key, senderKey)

		if not transaction.isValidTransaction():
			print("transaction error 2")
			return False
		self.pendingTransactions.append(transaction)
		return len(self.chain) + 1

	def getLastBlock(self):

		return self.chain[-1]

	def addGenesisBlock(self):
		tArr = []
		tArr.append(Transaction("me", "you", 10))
		genesis = Block(tArr, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), 0)

		genesis.prev = "None"
		return genesis

	def isValidChain(self, console):
		for i in range(1, len(self.chain)):
			b1 = self.chain[i-1]
			b2 = self.chain[i]

			if not b2.hasValidTransactions():
				print("error 3")
				return False

			if b2.hash != b2.calculateHash():
				print("error 4")
				return False


			if b2.prev != b1.hash:
				console.log("error 5")
				return False
		return True

	def generateKeys(self):
		key = RSA.generate(2048)
		private_key = key.export_key()
		file_out = open("private.pem", "wb")
		file_out.write(private_key)

		public_key = key.publickey().export_key()
		file_out = open("receiver.pem", "wb")
		file_out.write(public_key)
		
		print(public_key.decode('ASCII'))
		return key.publickey().export_key().decode('ASCII')


	def chainJSONencode(self):

		blockArrJSON = []
		for block in self.chain:
			blockJSON = {}
			blockJSON['hash'] = block.hash
			blockJSON['index'] = block.index
			blockJSON['prev'] = block.prev
			blockJSON['time'] = block.time
			blockJSON['nonse'] = block.nonse
			blockJSON['STONKS'] = block.STONKS


			transactionsJSON = []
			tJSON = {}
			for transaction in block.transactions:
				tJSON['time'] = transaction.time
				tJSON['sender'] = transaction.sender
				tJSON['reciever'] = transaction.reciever
				tJSON['amt'] = transaction.amt
				tJSON['hash'] = transaction.hash
				transactionsJSON.append(tJSON)

			blockJSON['transactions'] = transactionsJSON

			blockArrJSON.append(blockJSON)

		return blockArrJSON

	def chainJSONdecode(self, chainJSON):
		chain=[]
		for blockJSON in chainJSON:

			tArr = []
			for tJSON in blockJSON['transactions']:
				transaction = Transaction(tJSON['sender'], tJSON['reciever'], tJSON['amt'])
				transaction.time = tJSON['time']
				transaction.hash = tJSON['hash']
				tArr.append(transaction)


			block = Block(tArr, blockJSON['time'], blockJSON['index'])
			block.hash = blockJSON['hash']
			block.prev =blockJSON['prev']
			block.nonse = blockJSON['nonse']
			block.STONKS = blockJSON['STONKS']

			chain.append(block)
		return chain
		
	def getBalance(self, person):
		balance = 0
		for i in range(1, len(self.chain)):
			block = self.chain[i]
			try:
				for j in range(0, len(block.transactions)):
					transaction = block.transactions[j]
					if(transaction.sender == person):
						balance -= transaction.amt
					if(transaction.reciever == person):
						balance += transaction.amt
			except AttributeError:
				print("no transaction")
		return balance + 100