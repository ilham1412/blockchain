# 🔐 Blockchain Copyright Registry

A decentralized web application for registering and verifying proof of work ownership using blockchain technology. Built with Ethereum smart contracts, Python, and Flask.

## 📋 Overview

This platform allows artists, writers, and creators to register immutable proof of ownership for their work on a private Ethereum blockchain. Once registered, you'll have cryptographic evidence that you created the work at a specific date and time.

### Key Features

- ✅ **Immutable Registration** - Work ownership recorded permanently on blockchain
- ✅ **Content Hash Verification** - SHA-256 hash prevents duplicate registrations
- ✅ **Public Verification** - Anyone can verify work authenticity
- ✅ **Timestamped Proof** - Blockchain-verified creation date
- ✅ **Web Interface** - User-friendly Flask web application
- ✅ **CLI Tools** - Command-line scripts for advanced users

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Flask Web Application           │
│  (Frontend: HTML, Backend: Python)  │
└─────────────┬───────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────┐
│         Web3.py Interface               │
│      (Ethereum JSON-RPC Client)         │
└─────────────┬───────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────┐
│      Geth (Go-Ethereum) Node            │
│      Private Blockchain Network         │
└─────────────┬───────────────────────────┘
              │
              ↓
┌─────────────────────────────────────────┐
│    CopyrightRegistry Smart Contract     │
│         (Solidity ^0.8.0)               │
└─────────────────────────────────────────┘
```

## 🛠️ Tech Stack

- **Blockchain**: Ethereum (Geth)
- **Smart Contract**: Solidity 0.8.0
- **Backend**: Python 3.8+
- **Web Framework**: Flask
- **Blockchain Interface**: Web3.py
- **Frontend**: HTML5, CSS3
- **Database**: Blockchain (no traditional database needed)

## 📁 Project Structure

```
blockchain/
├── copyright_registry.sol          # Smart contract (Solidity)
├── genesis.json                    # Blockchain genesis configuration
├── config.py                       # Configuration settings
├── app.py                          # Flask web application
├── deploy_copyright_registry.py    # Contract deployment script
├── register_work.py                # CLI: Register work
├── verify_work.py                  # CLI: Verify work
├── list_works.py                   # CLI: List all works
├── contract_address.txt            # Deployed contract address
├── templates/                      # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── register.html
│   ├── verify.html
│   └── my_works.html
├── uploads/                        # Uploaded files storage
└── build/                          # Compiled contract artifacts
```

## 🚀 Installation & Setup (Langkah-Langkah)

### Prerequisites

- Python 3.8 or higher
- Node.js and npm (for Solidity compiler)
- Geth (Go-Ethereum)

### Setup Dependencies
```bash
pip install flask werkzeug web3
```

### Step 1: Prepare Data Directories and Accounts
Create data directories and generate 3 Ethereum accounts.
```bash
mkdir data
# Create 3 accounts. Save the addresses and key paths.
geth --datadir data account new
geth --datadir data account new
geth --datadir data account new
```
*Example Accounts:*
- Account 1 (Deployer)
- Account 2
- Account 3 (Miner)

### Step 2: Initialize Genesis Block
Edit `genesis.json` (copy from reference) with the following changes:

1. **Replace the `alloc` section** with Account 1:
   ```json
   "alloc": {
     "0xACCOUNT1": { "balance": "1000000000000000000000" }
   }
   ```

2. **Replace the `extradata` field** with Account 3 address (without the `0x` prefix).
   Format:
   ```json
   "extradata": "0x000000000000000000000000ACCOUNT3WITHOUT0X0000000000000000000000000000000000000"
   ```

Then initialize the first node:
```bash
geth --datadir data init genesis.json
```

### Step 3: Run First Node (Miner)
Run the first client using Account 3 and get the enode URL.
```bash
# Replace ADDRESS_ACCOUNT_3 with your actual account address
geth --datadir data --mine --miner.etherbase 0xADDRESS_ACCOUNT_3 --unlock 0xADDRESS_ACCOUNT_3 --allow-insecure-unlock --http --http.corsdomain "*"
```
*Note: Copy the `enode://...` URL from the output.*

### Step 4: Setup Second Node
Create `data2` directory, initialize, and run the second node connecting to the first.
```bash
mkdir data2
geth --datadir data2 init genesis.json

# Replace ENODE_URL with the one from Step 3
geth --datadir data2 --port 30305 --authrpc.port 8552 --http --bootnodes ENODE_URL --ipcpath //./pipe/geth-data2.ipc
```

### Step 5: Configure Application
Edit `config.py` and update the following variables with Account 1's details:
- `ACCOUNT_ADDRESS`: Your Account 1 address
- `UTC_KEYSTORE_FILE`: Path to your Account 1 keystore file

### Step 6: Configure Deployment Script
Edit `deploy_copyright_registry.py` and update the following variables with Account 1's details:
- `DEPLOYER_ADDRESS`: Your Account 1 address
- `KEY_UTC_FILE`: Path to your Account 1 keystore file

### Step 7: Compile Smart Contract
Compile `copyright_registry.sol` to generate ABI and BIN files.
```bash
solc --evm-version london copyright_registry.sol --abi --bin -o build --overwrite
```

### Step 8: Setup Web Application
Ensure `app.py` and `templates/` folder are set up for the UI.

### Step 9: Run Web Application
```bash
python app.py
```

## 🏃‍♂️ How to Run

### 1. Start Blockchain Nodes
**Terminal 1 (Node 1 - Miner):**
```bash
geth --datadir data --mine --miner.etherbase 0xADDRESS_ACCOUNT_3 --unlock 0xADDRESS_ACCOUNT_3
```

**Terminal 2 (Node 2 - Peer):**
```bash
geth --datadir data2 --port 30305 --authrpc.port 8552 --http --bootnodes ENODE_URL --ipcpath //./pipe/geth-data2.ipc
```

### 2. Deploy Contract (First Time Only)
```bash
python deploy_copyright_registry.py
```

### 3. Run Web Application
```bash
python app.py
```

## 💻 Usage

### Web Application

1. **Start Flask Server:**
```bash
python app.py
```

2. **Access Application:**
Open browser to `http://127.0.0.1:5000`

3. **Register a Work:**
   - Navigate to "Register Work"
   - Upload your file
   - Fill in work details
   - Enter your account password
   - Submit to blockchain

4. **Verify a Work:**
   - Navigate to "Verify Work"
   - Enter Work ID
   - View registration details

### Command Line Interface

**Register a Work:**
```bash
python register_work.py "uploads/myart.png" "Sunset Painting" "image" "Original artwork"
```

**Verify a Work:**
```bash
# By Work ID
python verify_work.py --id WORK-12345678

# By File
python verify_work.py --file uploads/myart.png

# Both
python verify_work.py --id WORK-12345678 --file uploads/myart.png
```

**List Your Works:**
```bash
python list_works.py

# Or for specific address
python list_works.py 0xYourAccountAddress
```

## 📝 Smart Contract Functions

### `registerWork()`
Register a new work on the blockchain
- **Parameters**: workId, workTitle, workType, contentHash, metadata
- **Returns**: Transaction receipt
- **Event**: `WorkRegistered`

### `verifyWork()`
Verify if a content hash matches a registered work
- **Parameters**: workId, contentHash
- **Returns**: bool (true if valid)

### `getWorkDetails()`
Get full details of a registered work
- **Parameters**: workId
- **Returns**: WorkRegistration struct

### `checkContentExists()`
Check if content hash is already registered
- **Parameters**: contentHash
- **Returns**: workId or empty string

### `getCreatorWorks()`
Get all works by a creator
- **Parameters**: creator address
- **Returns**: Array of work IDs

## 🔒 Security Features

1. **Content Hash Validation** - SHA-256 ensures file integrity
2. **Duplicate Prevention** - Same content cannot be registered twice
3. **Immutable Records** - Blockchain guarantees no tampering
4. **Timestamped Proof** - Block timestamp provides creation date
5. **Cryptographic Signatures** - All transactions are signed

## 📊 How It Works

1. **User uploads a file** (image, document, audio, etc.)
2. **System calculates SHA-256 hash** of the file content
3. **Smart contract checks** if hash already exists
4. **Transaction is created** with work details + hash
5. **User signs transaction** with their private key
6. **Blockchain validates** and records permanently
7. **Work ID is generated** for future verification

## 🌐 Supported File Types

- **Images**: PNG, JPG, JPEG, GIF
- **Documents**: PDF, TXT, DOC, DOCX
- **Audio**: MP3
- **Video**: MP4
- **Maximum Size**: 16 MB

## 🐛 Troubleshooting

### Transaction Failed
- Check account has sufficient ETH balance
- Verify account password is correct
- Ensure Geth node is running
- Check if you're using the contract owner account

### Connection Error
- Verify Geth is running on port 8545
- Check `config.RPC_URL` setting
- Ensure firewall allows connections

### Gas Errors
- Increase gas limit in transaction
- Check current gas price
- Ensure account has ETH for gas fees

## 📚 Additional Resources

- [Ethereum Documentation](https://ethereum.org/developers)
- [Solidity Documentation](https://docs.soliditylang.org/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Geth Documentation](https://geth.ethereum.org/docs/)

## 🎯 Future Enhancements

- [ ] MetaMask integration for easier wallet management
- [ ] IPFS integration for decentralized file storage
- [ ] NFT minting for registered works
- [ ] Multi-user authentication system
- [ ] Public leaderboard and exploration
- [ ] Transfer ownership functionality
- [ ] Batch registration support
- [ ] RESTful API for third-party integrations

---

**⚠️ Important Notes:**

- This is a private blockchain for demonstration/internal use
- Keep your keystore files and passwords secure
- Never commit private keys or passwords to version control
- For production use, consider security audits

**🎉 Happy Creating and Protecting Your Work!**
