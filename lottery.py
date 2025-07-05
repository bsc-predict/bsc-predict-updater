import json
from src.classes.LotteryClass import Lottery
from src.web3_provider import web3
import os

LOTTERY_CONTRACT = "0x5aF6D33DE2ccEC94efb1bDF8f92Bd58085432d2c"
CLAIM_TICKETS = "0xc914914f"
BUY_TICKETS = "0x88303dbd"

try:
  base_path = os.path.dirname(os.path.realpath(__file__))
except NameError:
  base_path = "./src/contracts"

with open(f'{base_path}/lottery_abi.json', 'r') as f:
    abi = json.load(f)

contract = web3.eth.contract(LOTTERY_CONTRACT, abi=abi)

def get_lottery(lottery_id: int) -> Lottery:
  res = contract.functions.viewLottery(lottery_id).call()
  return Lottery(res)

def get_current_lottery_id() -> int:
  return contract.functions.currentLotteryId().call()
