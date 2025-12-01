from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
import hashlib
from web3 import Web3
import json
from datetime import datetime
import uuid
import config

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_FILE_SIZE

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(config.RPC_URL))

def get_contract():
    """Get contract instance"""
    if not config.CONTRACT_ADDRESS:
        return None
    with open(config.ABI_FILE, "r") as f:
        abi = json.load(f)
    return w3.eth.contract(address=config.CONTRACT_ADDRESS, abi=abi)

def calculate_file_hash(filepath):
    """Calculate SHA-256 hash"""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register work page"""
    if request.method == 'POST':
        # Check file uploaded
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if not config.allowed_file(file.filename):
            flash('File type not allowed', 'error')
            return redirect(request.url)
        
        # Get form data
        work_title = request.form.get('work_title')
        work_type = request.form.get('work_type')
        metadata = request.form.get('metadata', '')
        account_password = request.form.get('account_password')
        
        if not all([work_title, work_type, account_password]):
            flash('Please fill all required fields', 'error')
            return redirect(request.url)
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Calculate hash
        content_hash = calculate_file_hash(filepath)
        
        # Check if already registered
        contract = get_contract()
        if not contract:
            flash('Contract not deployed', 'error')
            return redirect(url_for('index'))
        
        try:
            existing_work_id = contract.functions.checkContentExists(content_hash).call()
            if existing_work_id:
                flash(f'This content already registered as {existing_work_id}', 'warning')
                return redirect(url_for('verify', work_id=existing_work_id))
        except:
            pass
        
        # Register on blockchain
        try:
            with open(config.UTC_KEYSTORE_FILE) as keyfile:
                encrypted_key = keyfile.read()
                private_key = w3.eth.account.decrypt(encrypted_key, account_password)
            
            account = w3.eth.account.from_key(private_key)
            work_id = f"WORK-{uuid.uuid4().hex[:8].upper()}"
            
            nonce = w3.eth.get_transaction_count(account.address)
            
            # Estimate gas dynamically
            try:
                gas_estimate = contract.functions.registerWork(
                    work_id, work_title, work_type, content_hash, metadata
                ).estimate_gas({'from': account.address})
                gas_limit = int(gas_estimate * 1.2)  # Add 20% buffer
            except Exception:
                gas_limit = 500000  # Fallback gas limit
            
            tx = contract.functions.registerWork(
                work_id, work_title, work_type, content_hash, metadata
            ).build_transaction({
                'from': account.address,
                'nonce': nonce,
                'gas': gas_limit,
                'gasPrice': w3.eth.gas_price,
                'chainId': config.CHAIN_ID
            })
            
            signed_tx = account.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # receipt.status can be 1, True, or other truthy values depending on web3 version
            if receipt.status:
                flash(f'Work registered successfully! Work ID: {work_id}', 'success')
                return redirect(url_for('verify', work_id=work_id))
            else:
                flash(f'Transaction failed. Gas used: {receipt.gasUsed}', 'error')
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
        
        return redirect(request.url)
    
    return render_template('register.html')

def normalize_hash_input(h):
    if not h:
        return ""
    h = h.strip()
    if h.startswith("0x") or h.startswith("0X"):
        h = h[2:]
    return h.lower()

# ----- Ganti atau perbarui route /verify menjadi seperti ini -----
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    """Verify work page - now supports Work ID, file upload, OR content hash"""
    work_details = None
    work_id = request.args.get('work_id')

    if request.method == 'POST':
        # Prioritas: jika user isi work_id gunakan itu,
        # lalu cek content_hash, lalu file upload
        work_id = request.form.get('work_id') or None
        content_hash_input = request.form.get('content_hash') or None
        file = request.files.get('file')

        # If file provided, calculate hash
        content_hash_from_file = None
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # calculate hash (same helper as before)
            content_hash_from_file = calculate_file_hash(filepath)

        # If content_hash_input provided, normalize
        if content_hash_input:
            normalized = normalize_hash_input(content_hash_input)
            # ensure '0x' prefix if your contract stored with 0x; try both later
        else:
            normalized = None

        # Load contract
        contract = get_contract()
        if not contract:
            flash('Contract not deployed', 'error')
            return redirect(url_for('index'))

        # 1) If work_id provided: fetch details and optionally compare hash/file
        if work_id:
            try:
                details = contract.functions.getWorkDetails(work_id).call()
                work_details = {
                    'work_id': details[0],
                    'title': details[1],
                    'type': details[2],
                    'content_hash': details[3],
                    'creator': details[4],
                    'timestamp': datetime.fromtimestamp(details[5]).strftime('%Y-%m-%d %H:%M:%S UTC'),
                    'metadata': details[6]
                }
                # Compare hash if available
                target_hash = content_hash_from_file or normalized
                if target_hash:
                    # try compare both variants (with/without 0x) - smart contract may use hex with 0x
                    try:
                        is_valid = contract.functions.verifyWork(work_id, target_hash).call()
                    except:
                        # try with 0x prefix
                        try:
                            is_valid = contract.functions.verifyWork(work_id, "0x" + target_hash).call()
                        except:
                            is_valid = False
                    if is_valid:
                        flash('File/hash MATCHES registered work!', 'success')
                    else:
                        flash('File/hash DOES NOT MATCH registered work', 'warning')
            except Exception as e:
                flash(f'Work not found: {str(e)}', 'error')
            return render_template('verify.html', work_details=work_details)

        # 2) If no work_id but content hash provided -> lookup by hash
        if normalized or content_hash_from_file:
            search_hash = content_hash_from_file or normalized
            found_id = None
            try:
                # try as-is
                found_id = contract.functions.checkContentExists(search_hash).call()
            except:
                # try with 0x prefix
                try:
                    found_id = contract.functions.checkContentExists("0x" + search_hash).call()
                except:
                    found_id = ""
            if found_id:
                flash(f'Content found on-chain: {found_id}', 'success')
                return redirect(url_for('verify', work_id=found_id))
            else:
                flash('Content hash not found on-chain', 'warning')
                return render_template('verify.html', work_details=None)

        # If reached here, nothing provided
        flash('Please provide Work ID, upload a file, or paste a content hash.', 'error')
        return render_template('verify.html', work_details=None)

    # GET request: show empty form or details if ?work_id=...
    if work_id:
        contract = get_contract()
        if contract:
            try:
                details = contract.functions.getWorkDetails(work_id).call()
                work_details = {
                    'work_id': details[0],
                    'title': details[1],
                    'type': details[2],
                    'content_hash': details[3],
                    'creator': details[4],
                    'timestamp': datetime.fromtimestamp(details[5]).strftime('%Y-%m-%d %H:%M:%S UTC'),
                    'metadata': details[6]
                }
            except Exception as e:
                flash(f'Work not found: {str(e)}', 'error')

    return render_template('verify.html', work_details=work_details)

@app.route('/my-works')
def my_works():
    """List user's works"""
    contract = get_contract()
    works = []
    
    if contract:
        try:
            work_ids = contract.functions.getCreatorWorks(config.ACCOUNT_ADDRESS).call()
            for work_id in work_ids:
                details = contract.functions.getWorkDetails(work_id).call()
                works.append({
                    'work_id': details[0],
                    'title': details[1],
                    'type': details[2],
                    'timestamp': datetime.fromtimestamp(details[5]).strftime('%Y-%m-%d %H:%M:%S')
                })
        except Exception as e:
            flash(f'Error loading works: {str(e)}', 'error')
    
    return render_template('my_works.html', works=works)

if __name__ == '__main__':
    app.run(debug=True, port=5000)