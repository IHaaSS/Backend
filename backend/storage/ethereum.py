import json
import os
from base58 import b58decode, b58encode
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
from eth_account import Account


class IncidentsContract:
    def __init__(self):
        # Web3 setup
        w3 = Web3(Web3.WebsocketProvider('ws://' + os.getenv('ETH_IP') +
                                         ':' + os.getenv('ETH_PORT')))
        w3.eth.set_gas_price_strategy(medium_gas_price_strategy)

        acct = Account.from_key(os.getenv('SECRET_KEY'))
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(acct))
        w3.eth.default_account = acct.address

        # Contract setup
        with open('../contract/build/contracts/Incidents.json', 'r') as file:
            abi = json.load(file)

        deployments = list(abi['networks'].items())
        self.i = w3.eth.contract(address=deployments[0][1]['address'], abi=abi['abi'])

    def get_incidents(self):
        incidents = self.i.functions.getIncidents().call()
        return bytes2hex(incidents)

    async def get_incident(self, ref):
        incident = self.i.functions.getIncident(ref).call()
        comments = []
        for j, c in enumerate(incident[2]):
            comments.append(comment2dict(c))

        return {
            'ref': ref,
            'content': hex2ipfs(ref),
            'created': incident[0],
            'author': incident[1],
            'comments': comments,
            'attachments': [attachment2dict(a) for a in incident[3]],
            'votes': incident[4]
        }

    def add_incident(self, ref, attachments):
        return self.i.functions.addIncident(ipfs2bytes(ref), attachments).transact()

    def remove_incident(self, ref):
        return self.i.functions.removeIncident(ref).transact()

    def vote_incident(self, ref, up):
        return self.i.functions.voteIncident(ref, up).transact()

    def vote_comment(self, ref, up):
        return self.i.functions.voteComment(ref, up).transact()

    async def get_comment(self, ref):
        c = self.i.functions.getComment(ref).call()
        return comment2dict(c)

    def add_comment(self, parent, incident, content, attachments):
        ref = self.i.functions.addComment(parent, incident, content, attachments).transact()
        return ref.hex()


############
# HELPERS
############

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


def attachment2dict(a):
    return {
        'name': a[0],
        'ref': to_hex(a[1]),
        'content': hex2ipfs(to_hex(a[1]))
    }


def comment2dict(c):
    return {
        'ref': to_hex(c[0]),
        'parent': to_hex(c[1]),
        'created': c[2],
        'author': c[3],
        'content': hex2ipfs(to_hex(c[4])),
        'attachments': [attachment2dict(a) for a in c[5]],
        'votes': c[6]
    }
