import web3
from web3 import Web3
import json

w3 = Web3(Web3.WebsocketProvider('ws://127.0.0.1:7545'))
print(w3.isConnected())


with open('../contract/build/contracts/Incidents.json', 'r') as file:
    abi = json.load(file)

deployments = list(abi['networks'].items())
i = w3.eth.contract(address=deployments[0][1]['address'], abi=abi['abi'])


def get_incidents():
    # preprocessing
    return i.functions.getIncidents().call()

