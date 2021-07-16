import json
import os
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware
from eth_account import Account

# Web3 setup
w3 = Web3(Web3.WebsocketProvider('ws://' + os.getenv('ETH_IP') +
                                 ':' + os.getenv('ETH_PORT')))

acct = Account.privateKeyToAccount(os.getenv('SECRET_KEY'))
w3.middleware_onion.add(construct_sign_and_send_raw_middleware(acct))
w3.eth.default_account = acct.address

# Contract setup
with open('../contract/build/contracts/Incidents.json', 'r') as file:
    abi = json.load(file)

deployments = list(abi['networks'].items())
i = w3.eth.contract(address=deployments[0][1]['address'], abi=abi['abi'])


def get_incidents():
    # preprocessing
    incidents = i.functions.getIncidents().call()
    return [i.hex() for i in incidents]


def get_incident(ref):
    incident = i.functions.getIncident(ref).call()
    incident[3] = [i.hex() for i in incident[3]]
    return incident


def add_incident(ref, attachments):
    return i.functions.addIncident(ref, attachments).transact()


def vote_incident(ref, up):
    return i.functions.voteIncident(ref, up).transact()


def remove_incident(ref):
    return i.functions.removeIncident(ref).transact()
