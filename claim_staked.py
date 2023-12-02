from web3 import Web3 
import json
import time
from time import strftime
import requests
import sys
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.middleware import geth_poa_middleware

DECIMALS= 10**18

# Set your account 
MY_ADDRESS="YOUR adress"
MY_PRIVKEY="Yourprivcode"

# Connect with blockchain
w3=Web3(Web3.HTTPProvider('https://polygon-rpc.com/', request_kwargs={'timeout': 60} ))
res=w3.is_connected()
print('polygon node verbonden:',res)
print('chainid', w3.eth.chain_id)
time.sleep(1)
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
acct = w3.eth.account.from_key(MY_PRIVKEY)
print(acct.address)

# Arcomia nft staking contract details
stakecontractaddress=  w3.to_checksum_address("0x4e8e1F6c5C22E70a65d195A3767878d8CfbCE719")  
with open("stakeabi.txt") as f:
    stakeabi = json.load(f)
    #abi = info_json["abi"]
stakeContract=w3.eth.contract(abi=stakeabi,address=stakecontractaddress)

w3.middleware_onion.add(construct_sign_and_send_raw_middleware(acct))
w3.eth.defaultAccount = acct #.address

def claim(x):
    '''
    Function: claimRewards(uint256 _tokenId)

    MethodID: 0x0962ef79
    [0]:  58f77ed63f90aa200a521c42ed6d5f3828ac4384b2a4000000000000000002a9

    decoded value:
    #	Name	Type	Data
    0	_tokenId	uint256	40240817296490171407304243057650680174500241916580999921271128872452096000681
    
    (Decimal to Hexadecimal)
    '''
    gaspr=w3.eth.gas_price 
    priogas = max( round ( 1.0 * (10**9))   , round( 0.038*gaspr ) )  
    priogas_str=str(priogas)

    doclaim= stakeContract.functions.claimRewards( x ).transact({'gas':299000, 'maxPriorityFeePerGas': priogas_str , 'maxFeePerGas': str(round(1.5*gaspr/10.0)) , 'from':acct.address})
    time.sleep(30)


#####################################################################################
###########  One time loop checking if staked amount must be claimed  ###############

# specify minimum threshold RCM reward pending before starting claim
MIN_REWARD=1000  #1000 is about $0.38

# return the price of one unit of gas in wei
MAX_GWEI=200
gaspr=w3.eth.gas_price 
gaspr_gwei = round (gaspr / (10**9)) 
print('Gas (gwei):', gaspr_gwei )

if gaspr / (10**9) > MAX_GWEI :
  print(' ** Do not continue, network too busy and expensive to claim. Try later** ')
  exit()

# get your staked nft
myStakedNfttokens=stakeContract.functions.getStakeInfo( acct.address  ).call()
totalstaked=len(myStakedNfttokens[0])
firstnft=myStakedNfttokens[0][0]

# loop over all staked nft in stake mode and see if we need to claim
while True:
    try: 
        for x in myStakedNfttokens[0]:
          getinfo= stakeContract.functions.getStakeInfoForToken( x , acct.address  ).call()
          print(x , ' pending rcm', round( getinfo[1] / DECIMALS))
          if ((getinfo[1] / DECIMALS)  > MIN_REWARD ):
                print('Lets try to claim')
                claim(x)

        print('Total staked:', totalstaked)

        time.sleep(20)

    except Exception as e:
        print("An exception occurred, lets try again..")
        print(e)
        time.sleep(5)





