import hashlib
import time
from datetime import datetime
import json



class Transaction (object):
	def __init__(self, sender, recipient, amt):
		self.sender = sender
		self.recipient = recipient
		self.quantity = quantity
		self.time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S") #change to current date
		self.hash = self.calculateHash()


	def calculateHash(self):
		hashString = self.sender + self.recipient + str(self.quantity) + str(self.time)
		hashEncoded = json.dumps(hashString, sort_keys=True).encode()
		return hashlib.sha256(hashEncoded).hexdigest()

	def isValidTransaction(self):

		if(self.hash != self.calculateHash()):
			return False
		if(self.sender == self.recipient):
			return False
		if(self.sender == "Miner Rewards"):
			#security : unfinished
			return True
		if not self.signature or len(self.signature) == 0:
			print("No Signature!")
			return False
		return True
		#needs work!

	def signTransaction(self, key, senderKey, pkcs1_15):
		if(self.hash != self.calculateHash()):
			print("transaction tampered error")
			return False
		#print(str(key.publickey().export_key()));
		#print(self.sender);
		if(str(key.publickey().export_key()) != str(senderKey.publickey().export_key())):
			print("Transaction attempt to be signed from another wallet")
			return False

		#h = MD5.new(self.hash).digest();

		pkcs1_15.new(key)

		self.signature = "made"
		#print(key.sign(self.hash, ""));
		print("made signature!")
		return True