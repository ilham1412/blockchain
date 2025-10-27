from web3 import Web3
import json
from getpass import getpass
import sys

# Configuration
HTTP_PROVIDER = "http://localhost:8545"
DEPLOYER_ADDRESS = "0x5768097d5dEEE4Fb729db86874C988499cFB26aC"
KEY_UTC_FILE = 'data/keystore/UTC--2025-10-27T16-13-44.677266800Z--5768097d5deee4fb729db86874c988499cfb26ac'
CHAIN_ID = 110261

def deploy_contract():
    # Connect to blockchain
    w3 = Web3(Web3.HTTPProvider(HTTP_PROVIDER))
    if not w3.is_connected():
        print("✗ Failed to connect to blockchain")
        sys.exit(1)
    print("✓ Connected to blockchain")

    # Unlock account
    with open(KEY_UTC_FILE) as keyfile:
        key_data = keyfile.read()
        pwd = getpass("Account Password: ")
        try:
            private_key = w3.eth.account.decrypt(key_data, pwd)
        except Exception as e:
            print(f"✗ Failed to decrypt key: {e}")
            sys.exit(1)
    print("✓ Account unlocked")

    # Load contract ABI and bytecode
    try:
        with open("build/CopyrightRegistry.abi", "r") as f:
            contract_abi = json.load(f)
        with open("build/CopyrightRegistry.bin", "r") as f:
            contract_bytecode = f.read().strip()
    except FileNotFoundError as e:
        print(f"✗ Contract files not found: {e}")
        print("  Run: python compile_contract.py copyright_registry.sol")
        sys.exit(1)
    print("✓ Contract files loaded")

    # Prepare deployment
    CopyrightRegistry = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    nonce = w3.eth.get_transaction_count(DEPLOYER_ADDRESS)

    transaction = CopyrightRegistry.constructor().build_transaction({
        "chainId": CHAIN_ID,
        "from": DEPLOYER_ADDRESS,
        "nonce": nonce,
        "gas": 3000000,
        "gasPrice": w3.eth.gas_price
    })

    # Sign and send transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    print(f"\n📤 Deployment transaction sent")
    print(f"   TX hash: {tx_hash.hex()}")

    # Wait for confirmation
    print("\n⏳ Waiting for confirmation...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    contract_address = tx_receipt.contractAddress
    print(f"\n✅ Contract deployed successfully!")
    print(f"   Address: {contract_address}")
    print(f"   Block: {tx_receipt.blockNumber}")
    print(f"   Gas used: {tx_receipt.gasUsed}")

    # Save contract address
    with open("contract_address.txt", "w") as f:
        f.write(contract_address)
    print(f"\n💾 Contract address saved to contract_address.txt")

    return contract_address

if __name__ == "__main__":
    deploy_contract()