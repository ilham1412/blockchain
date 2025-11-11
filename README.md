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

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Node.js and npm (for Solidity compiler)
- Geth (Go-Ethereum)

### Step 1: Clone Repository

```bash
git clone https://github.com/ilham1412/blockchain.git
cd blockchain
```

### Step 2: Install Python Dependencies

```bash
pip install flask web3 werkzeug
```

### Step 3: Install Solidity Compiler

```bash
npm install -g solc
```

### Step 4: Install Geth

**Linux/Mac:**
```bash
# Follow instructions at https://geth.ethereum.org/docs/install-and-build/installing-geth
```

**Windows:**
Download from [https://geth.ethereum.org/downloads](https://geth.ethereum.org/downloads)

## ⚙️ Configuration

### 1. Initialize Blockchain

```bash
# Create data directory
mkdir -p data/keystore

# Initialize blockchain with genesis block
geth --datadir ./data init genesis.json
```

### 2. Create Ethereum Account

```bash
geth --datadir ./data account new
# Save the address and password securely
```

### 3. Update Configuration

Edit `config.py` with your account details:

```python
ACCOUNT_ADDRESS = "0xYourAccountAddress"
UTC_KEYSTORE_FILE = "data/keystore/UTC--your-keystore-file"
```

### 4. Start Blockchain Node

```bash
geth --datadir ./data \
     --networkid 110261 \
     --http \
     --http.addr "0.0.0.0" \
     --http.port 8545 \
     --http.api "eth,net,web3,personal" \
     --allow-insecure-unlock \
     console
```

### 5. Deploy Smart Contract

```bash
# Compile contract
solc --abi --bin copyright_registry.sol -o build/ --overwrite

# Deploy to blockchain
python deploy_copyright_registry.py
# Enter your account password when prompted
```

## 💻 Usage

### Web Application

1. **Start Flask Server:**
```bash
python app.py
```

2. **Access Application:**
Open browser to `http://localhost:5000`

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
