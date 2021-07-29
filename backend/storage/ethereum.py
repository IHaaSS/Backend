import json
import os
from base58 import b58decode, b58encode
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
from eth_account import Account

# Web3 setup
w3 = Web3(Web3.WebsocketProvider('ws://' + os.getenv('ETH_IP') +
                                 ':' + os.getenv('ETH_PORT')))

acct = Account.from_key(os.getenv('SECRET_KEY'))
w3.middleware_onion.add(construct_sign_and_send_raw_middleware(acct))
w3.eth.default_account = acct.address

# Contract setup
with open('../../contract/build/contracts/Incidents.json', 'r') as file:
    abi = json.load(file)

deployments = list(abi['networks'].items())
i = w3.eth.contract(address=deployments[0][1]['address'], abi=abi['abi'])


def get_incidents():
    # preprocessing
    incidents = i.functions.getIncidents().call()
    return bytes2hex(incidents)


async def get_incident(ref):
    incident = i.functions.getIncident(ref).call()
    return {
        'content': hex2ipfs(to_hex(incident[0])),
        'created': incident[1],
        'author': incident[2],
        'commentList': bytes2hex(incident[3]),
        'attachmentList': bytes2hex(incident[4]),
        'votedUp': incident[5],
        'votedDown': incident[6]
    }


def add_incident(ref, attachments=None):
    return i.functions.addIncident(ipfs2bytes(ref), attachments).transact()


def remove_incident(ref):
    return i.functions.removeIncident(ref).transact()


def vote_incident(ref, up):
    return i.functions.voteIncident(ref, up).transact()


async def get_comment(incident, index):
    ref = keccak256(incident, index)
    c = i.functions.getComment(ref).call()
    return {
        'parent': to_hex(c[0]),
        'created': c[1],
        'author': c[2],
        'content': to_hex(c[3]),
        'attachmentList': bytes2hex(c[4]),
        'votedUp': c[5],
        'votedDown': c[6]
    }


def add_comment(parent, incident, content, attachments):
    return i.functions.addComment(**locals()).transact()


############
# HELPERS
############

def keccak256(*values):
    return Web3.solidityKeccak(['bytes32', 'uint256'], values)


def ipfs2bytes(ipfsRef):
    return '0x' + b58decode(ipfsRef)[2:].hex()


def hex2ipfs(hexbytes):
    # 1220 is 'Qm' as hex (=sha256 ipfs multihash prefix identifier)
    return b58encode(bytes.fromhex('1220' + hexbytes[2:])).decode('utf-8')


def bytes2hex(bytesarray):
    return [to_hex(b) for b in bytesarray]


def bytes2ipfs(bytesarray):
    return [hex2ipfs(to_hex(b)) for b in bytesarray]


def to_hex(bytesref):
    return '0x' + bytesref.hex()
