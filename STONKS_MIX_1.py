import hashlib
import time
from datetime import datetime
import json


class Block:

    def __init__(self, index, proof_no, prev_hash, data, timestamp=None):
        self.index = index
        self.proof_no = proof_no
        self.prev_hash = prev_hash
        self.data = data
        self.timestamp = timestamp or time.time()

    @property
    def calculate_hash(self):
        block_of_string = "{}{}{}{}{}".format(self.index, self.proof_no,
                                              self.prev_hash, self.data,
                                              self.timestamp)

        return hashlib.sha256(block_of_string.encode()).hexdigest()

    def __repr__(self):
        return "{} - {} - {} - {} - {}".format(self.index, self.proof_no,
                                               self.prev_hash, self.data,
                                               self.timestamp)


class BlockChain:

    def __init__(self):
        self.chain = []
        self.current_data = []
        self.difficulty = 2
        self.minerRewards = 50
        self.blockSize = 10
        self.nodes = set()
        self.construct_genesis()

    def construct_genesis(self):
        self.construct_block(proof_no=0, prev_hash=0)

    def construct_block(self, proof_no, prev_hash):
        block = Block(
            index=len(self.chain),
            proof_no=proof_no,
            prev_hash=prev_hash,
            data=self.current_data)
        self.current_data = []

        self.chain.append(block)
        return block





    @staticmethod
    def check_validity(block, prev_block):
        if prev_block.index + 1 != block.index:
            return False

        elif prev_block.calculate_hash != block.prev_hash:
            return False

        elif not BlockChain.verifying_proof(block.proof_no,
                                            prev_block.proof_no):
            return False

        elif block.timestamp <= prev_block.timestamp:
            return False

        return True

    def new_data(self, sender, recipient, quantity):
        self.current_data.append({
            'sender': sender,
            'recipient': recipient,
            'quantity': quantity
        })
        return True

    @staticmethod
    def proof_of_work(last_proof):
        '''this simple algorithm identifies a number f' such that hash(ff') contain 4 leading zeroes
         f is the previous f'
         f' is the new proof
        '''
        proof_no = 0
        while BlockChain.verifying_proof(proof_no, last_proof) is False:
            proof_no += 1

        return proof_no

    @staticmethod
    def verifying_proof(last_proof, proof):
        #verifying the proof: does hash(last_proof, proof) contain 4 leading zeroes?

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @property
    def latest_block(self):
        return self.chain[-1]

    def block_mining(self, details_miner):

        self.new_data(
            sender="0",  #it implies that this node has created a new block
            recipient=details_miner,
            quantity=
            1,  #creating a new block (or identifying the proof number) is awarded with 1
        )

        last_block = self.latest_block

        last_proof_no = last_block.proof_no
        proof_no = self.proof_of_work(last_proof_no)

        last_hash = last_block.calculate_hash
        block = self.construct_block(proof_no, last_hash)

        return vars(block)

    def create_node(self, address):
        self.nodes.add(address)
        return True

    @staticmethod
    def obtain_block_object(block_data):
        #obtains block object from the block data

        return Block(
            block_data['index'],
            block_data['proof_no'],
            block_data['prev_hash'],
            block_data['data'],
            timestamp=block_data['timestamp'])


class Transaction (object):
	def __init__(self, sender, reciever, amt):
		self.sender = sender
		self.reciever = reciever
		self.amt = amt
		self.time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S") #change to current date
		self.hash = self.calculateHash()


	def calculateHash(self):
		hashString = self.sender + self.reciever + str(self.amt) + str(self.time)
		hashEncoded = json.dumps(hashString, sort_keys=True).encode()
		return hashlib.sha256(hashEncoded).hexdigest()

	def isValidTransaction(self):

		if(self.hash != self.calculateHash()):
			return False
		if(self.sender == self.reciever):
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


blockchain = BlockChain()

print("***Mining for STONKS***")
print(blockchain.chain)

last_block = blockchain.latest_block
last_proof_no = last_block.proof_no
proof_no = blockchain.proof_of_work(last_proof_no)

blockchain.new_data(
    sender="0",  #it implies that this node has created a new block
    recipient="Quincy Larson",  #let's send Quincy some coins!
    quantity=
    1,  #creating a new block (or identifying the proof number) is awarded with 1
)

last_hash = last_block.calculate_hash
block = blockchain.construct_block(proof_no, last_hash)

print("***Mining STONKS coin has been successful!***")
print(blockchain.chain)