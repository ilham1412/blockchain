import json
import os
from dotenv import load_dotenv

def init_genesis():
    # Load environment variables
    load_dotenv()
    
    account1 = os.getenv('ACCOUNT_1_ADDRESS')
    account3 = os.getenv('ACCOUNT_3_ADDRESS')
    chain_id = os.getenv('CHAIN_ID')
    
    if not all([account1, account3, chain_id]):
        print("Error: Missing required environment variables.")
        print("Please ensure .env is configured with ACCOUNT_1_ADDRESS, ACCOUNT_3_ADDRESS, and CHAIN_ID")
        return

    # Clean addresses (remove 0x prefix if present for extraData, keep for alloc)
    acc1_clean = account1.lower()
    if not acc1_clean.startswith('0x'):
        acc1_clean = '0x' + acc1_clean
        
    acc3_clean = account3.lower()
    if acc3_clean.startswith('0x'):
        acc3_clean = acc3_clean[2:]

    # Construct extraData
    # Prefix (32 bytes zeros) + Signer Address (20 bytes) + Suffix (65 bytes zeros for signature)
    prefix = "0" * 64
    suffix = "0" * 130
    extra_data = f"0x{prefix}{acc3_clean}{suffix}"

    # Load base genesis structure
    genesis = {
        "config": {
            "chainId": int(chain_id),
            "homesteadBlock": 0,
            "eip150Block": 0,
            "eip150Hash": 0,
            "eip155Block": 0,
            "eip158Block": 0,
            "byzantiumBlock": 0,
            "constantinopleBlock": 0,
            "petersburgBlock": 0,
            "istanbulBlock": 0,
            "muirGlacierBlock": 0,
            "berlinBlock": 0,
            "londonBlock": 0,
            "clique": {
                "period": 15,
                "epoch": 30000
            }
        },
        "gasLimit": "9000000000",
        "alloc": {
            acc1_clean: {
                "balance": "1000000000000000000000"  # 1000 ETH
            }
        },
        "difficulty": 1,
        "timestamp": "0x00",
        "extraData": extra_data
    }

    # Write to file
    with open('genesis.json', 'w') as f:
        json.dump(genesis, f, indent=2)
    
    print(f"✅ genesis.json updated successfully!")
    print(f"   Chain ID: {chain_id}")
    print(f"   Allocated Balance to: {acc1_clean}")
    print(f"   Miner (Signer): 0x{acc3_clean}")

if __name__ == "__main__":
    init_genesis()
