from web3 import Web3
import json
import hashlib
import sys
from datetime import datetime
import config

def calculate_file_hash(filepath):
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def verify_work(work_id=None, filepath=None):
    """Verify a work registration on the blockchain"""
    
    # Connect to blockchain
    w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
    if not w3.is_connected():
        print("✗ Cannot connect to blockchain")
        return False
    print("✓ Connected to blockchain")

    # Load contract
    if not config.CONTRACT_ADDRESS:
        return False
    
    with open(config.ABI_FILE, "r") as f:
        abi = json.load(f)
    contract = w3.eth.contract(address=config.CONTRACT_ADDRESS, abi=abi)
    print(f"✓ Contract loaded\n")

    # Calculate file hash if file provided
    content_hash = None
    if filepath:
        print(f"📄 Calculating hash for: {filepath}")
        content_hash = calculate_file_hash(filepath)
        print(f"✓ Content hash: {content_hash}\n")

    # If work_id provided, verify by ID
    if work_id:
        try:
            work_details = contract.functions.getWorkDetails(work_id).call()
            
            print("═" * 60)
            print("📋 WORK REGISTRATION DETAILS")
            print("═" * 60)
            print(f"Work ID:      {work_details[0]}")
            print(f"Title:        {work_details[1]}")
            print(f"Type:         {work_details[2]}")
            print(f"Content Hash: {work_details[3]}")
            print(f"Creator:      {work_details[4]}")
            print(f"Registered:   {datetime.fromtimestamp(work_details[5]).strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"Metadata:     {work_details[6]}")
            print("═" * 60)
            
            # If file also provided, verify hash matches
            if content_hash:
                is_valid = contract.functions.verifyWork(work_id, content_hash).call()
                if is_valid:
                    print("\n✅ File hash MATCHES registered work!")
                    print("   This file is authentic.")
                else:
                    print("\n⚠️  File hash DOES NOT MATCH!")
                    print("   This file may have been modified.")
            
            return True
            
        except Exception as e:
            print(f"✗ Work not found or error: {e}")
            return False
    
    # If only file provided, search by content hash
    elif content_hash:
        try:
            existing_work_id = contract.functions.checkContentExists(content_hash).call()
            if existing_work_id:
                print(f"✅ This content is registered on blockchain!\n")
                # Recursively call with work_id
                return verify_work(work_id=existing_work_id, filepath=None)
            else:
                print("⚠️  This content is NOT registered on blockchain")
                print("   No matching registration found.")
                return False
        except Exception as e:
            print(f"✗ Error checking content: {e}")
            return False
    else:
        print("✗ Please provide either work_id or filepath")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Verify by Work ID:")
        print("    python verify_work.py --id WORK-12345678")
        print("\n  Verify by File:")
        print("    python verify_work.py --file myart.png")
        print("\n  Verify both:")
        print("    python verify_work.py --id WORK-12345678 --file myart.png")
        sys.exit(1)
    
    work_id = None
    filepath = None
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--id" and i + 1 < len(sys.argv):
            work_id = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--file" and i + 1 < len(sys.argv):
            filepath = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    verify_work(work_id, filepath)