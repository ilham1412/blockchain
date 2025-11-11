#!/usr/bin/env python3
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

def normalize_hash(h):
    """Normalize hex hash input: accept with/without 0x and lowercase"""
    if not h:
        return h
    h = h.strip()
    if h.startswith("0x") or h.startswith("0X"):
        return h[2:].lower()
    return h.lower()

def try_variants_check(contract, content_hash):
    """
    Try checking various variants of the provided hash against the contract:
    - as provided
    - with/without '0x' prefix
    - lowercase/uppercase handled by normalize_hash
    Returns the found work_id or empty string.
    """
    if not content_hash:
        return ""
    # normalize (no 0x)
    base = normalize_hash(content_hash)

    variants = [base, "0x" + base]
    for v in variants:
        try:
            work_id = contract.functions.checkContentExists(v).call()
            if work_id:
                return work_id
        except Exception:
            # ignore and try next variant
            pass
    return ""

def print_work_details(work_details):
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

def verify_work(work_id=None, filepath=None, content_hash_arg=None):
    """Verify a work registration on the blockchain"""
    
    # Connect to blockchain
    w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
    if not w3.is_connected():
        print("✗ Cannot connect to blockchain")
        return False
    print("✓ Connected to blockchain")

    # Load contract
    if not config.CONTRACT_ADDRESS:
        print("✗ CONTRACT_ADDRESS not set in config.py")
        return False
    
    try:
        with open(config.ABI_FILE, "r") as f:
            abi = json.load(f)
    except Exception as e:
        print(f"✗ Failed to load ABI file: {e}")
        return False

    contract = w3.eth.contract(address=config.CONTRACT_ADDRESS, abi=abi)
    print(f"✓ Contract loaded\n")

    # If filepath provided, compute its hash
    file_hash = None
    if filepath:
        try:
            print(f"📄 Calculating hash for: {filepath}")
            file_hash = calculate_file_hash(filepath)
            print(f"✓ Content hash: {file_hash}\n")
        except Exception as e:
            print(f"✗ Failed to calculate file hash: {e}")
            return False

    # If explicit content-hash argument provided (CLI --hash)
    provided_hash = None
    if content_hash_arg:
        provided_hash = normalize_hash(content_hash_arg)
        print(f"🔎 Searching by provided content hash: {content_hash_arg}")

    # Precedence:
    # 1) If work_id is provided -> show work details and optionally compare file or provided hash
    # 2) Else if file_hash is provided -> lookup by file_hash
    # 3) Else if provided_hash is provided -> lookup by provided_hash
    # 4) Else -> error
    if work_id:
        try:
            work_details = contract.functions.getWorkDetails(work_id).call()
            print_work_details(work_details)

            # If file hash provided, verify hash matches
            target_hash = None
            if file_hash:
                target_hash = file_hash
            elif provided_hash:
                target_hash = provided_hash

            if target_hash:
                try:
                    is_valid = contract.functions.verifyWork(work_id, target_hash).call()
                    if is_valid:
                        print("\n✅ File/hash MATCHES registered work!")
                        print("   This file/hash is authentic.")
                    else:
                        print("\n⚠️ File/hash DOES NOT MATCH!")
                        print("   This file/hash may have been modified or is different.")
                except Exception as e:
                    print(f"\n✗ Error verifying hash: {e}")
            return True

        except Exception as e:
            print(f"✗ Work not found or error: {e}")
            return False

    # If file uploaded but no work_id, try to find by file hash
    if file_hash:
        try:
            print("🔍 Checking blockchain for this content hash...")
            existing_work_id = try_variants_check(contract, file_hash)
            if existing_work_id:
                print(f"✅ This content is registered on blockchain! Work ID: {existing_work_id}\n")
                return verify_work(work_id=existing_work_id, filepath=None)
            else:
                print("⚠️  This content is NOT registered on blockchain")
                print("   No matching registration found.")
                return False
        except Exception as e:
            print(f"✗ Error checking content: {e}")
            return False

    # If hash provided via CLI (--hash) but no work_id
    if provided_hash:
        try:
            print("🔍 Checking blockchain for the provided content hash...")
            existing_work_id = try_variants_check(contract, provided_hash)
            if existing_work_id:
                print(f"✅ This content hash is registered on blockchain! Work ID: {existing_work_id}\n")
                return verify_work(work_id=existing_work_id, filepath=None)
            else:
                print("⚠️ This content hash is NOT registered on blockchain")
                print("   No matching registration found.")
                return False
        except Exception as e:
            print(f"✗ Error checking provided hash: {e}")
            return False

    print("✗ Please provide either --id <WORK-ID> or --file <path> or --hash <content-hash>")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Verify by Work ID:")
        print("    python verify_work.py --id WORK-12345678")
        print("\n  Verify by File:")
        print("    python verify_work.py --file myart.png")
        print("\n  Verify by Content Hash (hex):")
        print("    python verify_work.py --hash 24466bbc756be2472263d11320757e475547cb75fa93b1309bc5b89248433462")
        print("\n  You can combine --id with --file or --hash to verify the provided file/hash against the on-chain record.")
        sys.exit(1)
    
    work_id = None
    filepath = None
    content_hash_arg = None
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--id" and i + 1 < len(sys.argv):
            work_id = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--file" and i + 1 < len(sys.argv):
            filepath = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--hash" and i + 1 < len(sys.argv):
            content_hash_arg = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    verify_work(work_id, filepath, content_hash_arg)