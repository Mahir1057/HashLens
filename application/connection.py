import json
from pathlib import Path
from web3 import Web3

# Base directory = directory where this file (connection.py) is located
BASE_DIR = Path(__file__).resolve().parent

# Connect to a local Ethereum node
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

if not w3.is_connected():
    raise ConnectionError("Web3 is not connected. Make sure Ganache/Hardhat is running on port 8545.")

def get_contract_abi():
    certification_json_path = BASE_DIR.parent / "build" / "contracts" / "Certification.json"
    try:
        with open(certification_json_path, 'r') as json_file:
            certification_data = json.load(json_file)
            abi = certification_data.get('abi', [])
            if not abi:
                raise ValueError("ABI is empty. Check Certification.json")
            return abi
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: {certification_json_path} not found. Did you compile the contract?")

contract_abi = get_contract_abi()

# deployment_config.json is expected in project root (hashlens3/)
deployment_config_fpath = BASE_DIR.parent / "deployment_config.json"
try:
    with open(deployment_config_fpath, 'r') as json_file:
        address_data = json.load(json_file)
    contract_address = address_data.get('Certification')
    if not contract_address:
        raise ValueError("Contract address not found in deployment_config.json")
except FileNotFoundError:
    raise FileNotFoundError(f"Error: {deployment_config_fpath} not found. Did you deploy the contract?")

# Interact with the smart contract
contract = w3.eth.contract(address=contract_address, abi=contract_abi)
