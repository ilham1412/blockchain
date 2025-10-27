from web3 import Web3
import json
import sys
from datetime import datetime
import config

def list_creator_works(creator_address=None):
    """List all works registered by a creator"""
    
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

    # Use default account if none provided
    if not creator_address:
        creator_address = config.ACCOUNT_ADDRESS
    
    print(f"📋 Listing works for: {creator_address}\n")

    try:
        # Get all work IDs for creator
        work_ids = contract.functions.getCreatorWorks(creator_address).call()
        
        if not work_ids:
            print("No works registered by this creator")
            return True
        
        print(f"Total works: {len(work_ids)}\n")
        print("═" * 80)
        
        # Get details for each work
        for i, work_id in enumerate(work_ids, 1):
            work_details = contract.functions.getWorkDetails(work_id).call()
            
            print(f"\n{i}. Work ID: {work_details[0]}")
            print(f"   Title:        {work_details[1]}")
            print(f"   Type:         {work_details[2]}")
            print(f"   Content Hash: {work_details[3][:16]}...{work_details[3][-16:]}")
            print(f"   Registered:   {datetime.fromtimestamp(work_details[5]).strftime('%Y-%m-%d %H:%M:%S UTC')}")
            if work_details[6]:
                print(f"   Metadata:     {work_details[6]}")
        
        print("\n" + "═" * 80)
        return True
        
    except Exception as e:
        print(f"✗ Error retrieving works: {e}")
        return False

if __name__ == "__main__":
    creator_address = sys.argv[1] if len(sys.argv) > 1 else None
    list_creator_works(creator_address)