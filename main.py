import json
import config
from web3 import Web3

# Настройка подключения
infura_url = 'https://rpc.mantle.xyz'
web3 = Web3(Web3.HTTPProvider(infura_url))

# Проверка подключения
assert web3.is_connected(), "Failed to connect to Ethereum node"

# ABI и адрес контракта NFT
nft_contract_abi = json.load(open('abi/cow.json'))
nft_contract_address = '0xa7236aC4aE735Bcad76E3d56D07D929a9Be865f6'  # Замените на реальный адрес контракта

# Создание объекта контракта
nft_contract = web3.eth.contract(address=nft_contract_address, abi=nft_contract_abi)

keys_list = []
with open("private_keys.txt", "r") as f:
    for row in f:
        private_key=row.strip()
        if private_key:
            keys_list.append(private_key)

# Функция для получения всех tokenId на заданном кошельке
def get_tokens_of_wallet(wallet_address, token_range):
    wallet_address = web3.to_checksum_address(wallet_address)
    nft_count = nft_contract.functions.balanceOf(wallet_address).call()
    owned_tokens = []
    for token_id in token_range:
        if len(owned_tokens) == nft_count:
            break
        try:
            owner = nft_contract.functions.ownerOf(token_id).call()
            if owner.lower() == wallet_address.lower():
                owned_tokens.append(token_id)
        except Exception as e:
            print(f"Error checking token {token_id}: {e}")
    print(f"wallet: {wallet_address} owned_tokens: {owned_tokens}")
    return owned_tokens


# Функция для перевода всех NFT с одного адреса на другой
def transfer_all_nfts(from_address, private_key, to_address, token_ids):
    wallet_out = web3.to_checksum_address(to_address)
    gas_price = web3.eth.gas_price
    gas_limit = 70000

    for tokenId in token_ids:
        tx = nft_contract.functions.safeTransferFrom(from_address, wallet_out, tokenId).build_transaction({
            'from': from_address,
            'nonce': web3.eth.get_transaction_count(from_address),
            'gas': gas_limit,
            'gasPrice': gas_price
        })
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        web3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transferred tokenId {tokenId} from {from_address} to {to_address}")


start = config.start
for private_key in keys_list:
    ids = range(start, config.end)
    account = web3.eth.account.from_key(private_key)
    wallet = account.address
    token_ids = get_tokens_of_wallet(wallet, ids)
    if len(token_ids) > 0:
        transfer_all_nfts(wallet, private_key, config.to_address, token_ids)
        start = max(token_ids)
