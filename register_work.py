from web3 import Web3
import json
import hashlib
import sys
from getpass import getpass
from datetime import datetime
import uuid
import config

def calculate_file_hash(filepath):
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def register_work(
    filepath,
    work_title,
    work_type,
    metadata="",
    account_password=None
):
    """Register a work on the blockchain"""
    
    # Connect to blockchain
    w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
    if not w3.is_connected():
        print("✗ Cannot connect to blockchain")
        return False
    print("✓ Connected to blockchain")

    # Load contract
    if not config.CONTRACT_ADDRESS:
        return False
    
    try:
        with open(config.ABI_FILE, "r") as f:
            abi = json.load(f)
        contract = w3.eth.contract(address=config.CONTRACT_ADDRESS, abi=abi)
        print(f"✓ Contract loaded at {config.CONTRACT_ADDRESS}")
    except Exception as e:
        print(f"✗ Failed to load contract: {e}")
        return False

    # Unlock account
    try:
        with open(config.UTC_KEYSTORE_FILE) as keyfile:
            encrypted_key = keyfile.read()
            if not account_password:
                account_password = getpass("Account Password: ")
            private_key = w3.eth.account.decrypt(encrypted_key, account_password)
    except Exception as e:
        print(f"✗ Failed to decrypt account: {e}")
        return False
    
    account = w3.eth.account.from_key(private_key)
    print(f"✓ Using account: {account.address}")

    # Check account balance
    balance = w3.eth.get_balance(account.address)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f"✓ Account balance: {balance_eth} ETH")
    
    if balance == 0:
        print("✗ Insufficient balance. Account has 0 ETH")
        return False

    # Calculate content hash
    print(f"\n📄 Processing file: {filepath}")
    try:
        content_hash = calculate_file_hash(filepath)
        print(f"✓ Content hash: {content_hash}")
    except Exception as e:
        print(f"✗ Failed to calculate hash: {e}")
        return False

    # Check if content already registered
    try:
        existing_work_id = contract.functions.checkContentExists(content_hash).call()
        if existing_work_id:
            print(f"\n⚠️  This content is already registered!")
            print(f"   Work ID: {existing_work_id}")
            try:
                work_details = contract.functions.getWorkDetails(existing_work_id).call()
                print(f"   Title: {work_details[1]}")
                print(f"   Creator: {work_details[4]}")
                print(f"   Registered: {datetime.fromtimestamp(work_details[5])}")
            except:
                pass
            return False
    except Exception as e:
        print(f"⚠️  Warning checking existing content: {e}")

    # Generate unique work ID
    work_id = f"WORK-{uuid.uuid4().hex[:8].upper()}"
    print(f"✓ Generated Work ID: {work_id}")

    # Check who is the contract owner
    try:
        contract_owner = contract.functions.owner().call()
        print(f"\nℹ️  Contract owner: {contract_owner}")
        print(f"   Your address: {account.address}")
        
        if contract_owner.lower() != account.address.lower():
            print("\n⚠️  WARNING: You are not the contract owner!")
            print("   This contract has 'onlyOwner' modifier on registerWork function")
            print("   Only the contract owner can register works with this contract")
            print(f"\n   Solution: Deploy contract from account {account.address}")
            print("   Or use the account that deployed the contract")
            return False
    except Exception as e:
        print(f"⚠️  Could not check contract owner: {e}")

    # Build transaction with proper gas estimation
    try:
        print("\n🔧 Building transaction...")
        
        # Get current nonce
        nonce = w3.eth.get_transaction_count(account.address)
        print(f"   Nonce: {nonce}")
        
        # Estimate gas
        try:
            gas_estimate = contract.functions.registerWork(
                work_id,
                work_title,
                work_type,
                content_hash,
                metadata
            ).estimate_gas({'from': account.address})
            
            # Add 20% buffer to gas estimate
            gas_limit = int(gas_estimate * 1.2)
            print(f"   Gas estimate: {gas_estimate}")
            print(f"   Gas limit (with buffer): {gas_limit}")
        except Exception as e:
            print(f"   Gas estimation failed: {e}")
            print(f"   Using default gas limit: 500000")
            gas_limit = 500000
        
        # Get current gas price
        gas_price = w3.eth.gas_price
        print(f"   Gas price: {w3.from_wei(gas_price, 'gwei')} Gwei")
        
        # Calculate transaction cost
        tx_cost = gas_limit * gas_price
        tx_cost_eth = w3.from_wei(tx_cost, 'ether')
        print(f"   Estimated cost: {tx_cost_eth} ETH")
        
        if tx_cost > balance:
            print(f"✗ Insufficient balance for transaction")
            print(f"   Required: {tx_cost_eth} ETH")
            print(f"   Available: {balance_eth} ETH")
            return False
        
        # Build transaction
        tx = contract.functions.registerWork(
            work_id,
            work_title,
            work_type,
            content_hash,
            metadata
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': config.CHAIN_ID
        })
        
        print("✓ Transaction built successfully")
        
    except Exception as e:
        print(f"✗ Failed to build transaction: {e}")
        print(f"\nDebug info:")
        print(f"  work_id: {work_id}")
        print(f"  work_title: {work_title}")
        print(f"  work_type: {work_type}")
        print(f"  content_hash: {content_hash}")
        print(f"  metadata: {metadata}")
        return False

    # Sign and send transaction
    try:
        print("\n📝 Signing transaction...")
        signed_tx = account.sign_transaction(tx)
        
        print("📤 Sending transaction...")
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"✓ Transaction sent: {tx_hash.hex()}")
        
    except ValueError as e:
        print(f"✗ Transaction rejected: {e}")
        return False
    except Exception as e:
        print(f"✗ Failed to send transaction: {e}")
        return False

    # Wait for confirmation
    try:
        print("\n⏳ Waiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        print(f"\n📦 Transaction mined in block {receipt.blockNumber}")
        print(f"   Status: {receipt.status}")
        print(f"   Gas used: {receipt.gasUsed}")
        
        if receipt.status == 1:
            print(f"\n✅ Work registered successfully!")
            print(f"   Work ID: {work_id}")
            print(f"   Title: {work_title}")
            print(f"   Type: {work_type}")
            print(f"   Hash: {content_hash}")
            print(f"   Block: {receipt.blockNumber}")
            print(f"   Creator: {account.address}")
            
            # Save registration info
            registration_info = {
                "work_id": work_id,
                "title": work_title,
                "type": work_type,
                "content_hash": content_hash,
                "creator": account.address,
                "tx_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "timestamp": datetime.now().isoformat()
            }
            
            output_file = f"registration_{work_id}.json"
            with open(output_file, "w") as f:
                json.dump(registration_info, f, indent=2)
            print(f"\n💾 Registration details saved to {output_file}")
            
            return True
        else:
            print(f"\n✗ Transaction failed (status: {receipt.status})")
            
            # Try to get revert reason
            try:
                tx_receipt = w3.eth.get_transaction(tx_hash)
                w3.eth.call(tx_receipt, receipt.blockNumber)
            except Exception as e:
                print(f"   Revert reason: {e}")
            
            return False
            
    except Exception as e:
        print(f"\n✗ Error waiting for receipt: {e}")
        print(f"   Transaction may still be pending: {tx_hash.hex()}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python register_work.py <filepath> <work_title> [work_type] [metadata]")
        print("\nExample:")
        print('  python register_work.py myart.png "Sunset Painting" "image" "Original artwork"')
        print("\nWork Types:")
        print("  image, text, music, video, photography, code, other")
        sys.exit(1)
    
    filepath = sys.argv[1]
    work_title = sys.argv[2]
    work_type = sys.argv[3] if len(sys.argv) > 3 else "general"
    metadata = sys.argv[4] if len(sys.argv) > 4 else ""
    
    # Check if file exists
    import os
    if not os.path.exists(filepath):
        print(f"✗ File not found: {filepath}")
        sys.exit(1)
    
    success = register_work(filepath, work_title, work_type, metadata)
    sys.exit(0 if success else 1)