import os
import json

# Blockchain Configuration
RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:8545")
CHAIN_ID = int(os.getenv("CHAIN_ID", "110261"))

# Contract Configuration
def get_contract_address():
    """Read contract address from file"""
    try:
        with open("contract_address.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("contract_address.txt not found")
        print("   Deploy contract first: python deploy_copyright_registry.py")
        return None

CONTRACT_ADDRESS = get_contract_address()
ABI_FILE = "build/CopyrightRegistry.abi"

# Account Configuration
ACCOUNT_ADDRESS = os.getenv("ACCOUNT_ADDRESS", "0x5768097d5dEEE4Fb729db86874C988499cFB26aC")
UTC_KEYSTORE_FILE = os.getenv(
    "UTC_KEYSTORE_FILE",
    "data/keystore/UTC--2025-10-27T16-13-44.677266800Z--5768097d5deee4fb729db86874c988499cfb26ac"
)

# Upload Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'mp4', 'doc', 'docx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("build", exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS