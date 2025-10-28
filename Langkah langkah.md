### **Langkah-Langkah pembuatan**



step 1 



mkdir data dan buat akun



Public address of the key:   0x5768097d5dEEE4Fb729db86874C988499cFB26aC

Path of the secret key file: data\\keystore\\UTC--2025-10-27T16-13-44.677266800Z--5768097d5deee4fb729db86874c988499cfb26ac



akun 2

Public address of the key:   0x78969CbDa489764C66Fe9aEE350fF0323Ad276E1

Path of the secret key file: data\\keystore\\UTC--2025-10-27T16-14-44.270170500Z--78969cbda489764c66fe9aee350ff0323ad276e1



akun 3

Public address of the key:   0xD9bB517B30C957173533fa52f706a087a6eDc98e

Path of the secret key file: data\\keystore\\UTC--2025-10-27T16-15-09.457555500Z--d9bb517b30c957173533fa52f706a087a6edc98e



step 2

edit genesis.json (salin aja dari kerja sebelumnya)



geth --datadir data init genesis.json



step 3

jalanin client pertama menggunakan address akun 3



lalu ambil enode nya



enode://ce8f1c6ed37e416ced55e646e0b4dae8c4d9a62db1763c5c05d9bf078f353cf84c2f175e81b8083abe70038343a7642769c4d21a34c02c2a3cf476be6d057619@127.0.0.1:30303



step 4



buat mkdir data 2, lalu 

geth --datadir data2 init genesis.json



dan jalankan menggunakan



geth --datadir data2 --port 30305 --authrpc.port 8552 --http --bootnodes enode://ce8f1c6ed37e416ced55e646e0b4dae8c4d9a62db1763c5c05d9bf078f353cf84c2f175e81b8083abe70038343a7642769c4d21a34c02c2a3cf476be6d057619@127.0.0.1:30303 --ipcpath //./pipe/geth-data2.ipc





step 5

membuat copyright\_registry.sol

lalu jalankan

solc --evm-version london copyright\_registry.sol --abi --bin -o build 



step 6



buat deploy\_copyright.py



deployer address ganti akun 1



step 7



buat config.py

lalu masukan address akun 1



step 8

buat register\_work.py



step 9

buat verify\_work.py



step 10

buat list\_work.py



step 11

buat flask dan semua file HTML dalam folder templates (untuk ui)



### **Setup** 



pip install flask werkzeug web3





### Cara menjalankan



1\. jalankan 

geth --datadir data --mine --miner.etherbase 0xD9bB517B30C957173533fa52f706a087a6eDc98e --unlock 0xD9bB517B30C957173533fa52f706a087a6eDc98e



2\. Jalankan di powershell lain

geth --datadir data2 --port 30305 --authrpc.port 8552 --http --bootnodes enode://ce8f1c6ed37e416ced55e646e0b4dae8c4d9a62db1763c5c05d9bf078f353cf84c2f175e81b8083abe70038343a7642769c4d21a34c02c2a3cf476be6d057619@127.0.0.1:30303 --ipcpath //./pipe/geth-data2.ipc



3\. jalankan masing masing

\# Register a work

python register\_work.py myart.png "Sunset Painting" "image" "Original artwork"



\# Verify by Work ID

python verify\_work.py --id WORK-12345678 (lihat id yang ada)



\# Verify by file

python verify\_work.py --file myart.png (lihat gambar yang ada)



\# List your works

python list\_works.py



4\. untuk full ui 

python app.py





### catatan 



Ini adalah sistem pendaftaran hak cipta di mana pencipta dapat membuktikan kepemilikan atas karyanya menggunakan blockchain.



Saya menggunakan Python Flask untuk backend, Solidity untuk kontrak pintar, dan Geth untuk menjalankan blockchain Ethereum pribadi. Frontendnya adalah HTML/CSS dengan Web3.py yang menghubungkan Python ke blockchain.



Bagian blockchain sedang dalam proses registrasi dan verifikasi. Saat pengguna mengunggah file, saya menghitung hash SHA-256-nya, membuat transaksi yang ditandatangani oleh dompet Ethereum mereka, dan mengirimkannya ke kontrak pintar yang menyimpannya secara permanen di blockchain.



Saya menerapkannya dengan: (1) menyiapkan jaringan Geth pribadi, (2) menulis kontrak pintar Solidity untuk menyimpan pendaftaran(copyright\_registry.sol), (3) menerapkan kontrak, dan (4) menggunakan Web3.py di Flask untuk mengirim transaksi dan data kueri. Blockchain memberikan bukti kepemilikan yang tidak dapat diubah dan diberi stempel waktu.

