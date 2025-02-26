from typing import Tuple
from classes.LotteryClass import Lottery
import os
import csv
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from collections import deque
import datetime as dt
import subprocess
from dataclasses import dataclass

@dataclass
class UpdateConfig:
  rpl: str
  contract: str
  lottery_file_path: str
  def __init__(self, rpl: str, contract: str, lottery_file_path: str) -> None:
    self.rpl = rpl
    self.contract = contract
    self.lottery_file_path = lottery_file_path


base_path = os.path.dirname(os.path.realpath(__file__))

mainnet_config = UpdateConfig(
  rpl="https://bsc-dataseed.binance.org/",
  contract="0x5aF6D33DE2ccEC94efb1bDF8f92Bd58085432d2c",
  lottery_file_path=f"{base_path}/data/v2/main/lottery.csv",
)

def lottery_to_tuple(id: int, lottery: Lottery) -> Tuple:
  return (
    id,
    lottery.status.value,
    lottery.startTime,
    lottery.endTime,
    lottery.priceTicketInCake,
    lottery.discountDivisor,
    lottery.rewardsBreakdown[0],
    lottery.rewardsBreakdown[1],
    lottery.rewardsBreakdown[2],
    lottery.rewardsBreakdown[3],
    lottery.rewardsBreakdown[4],
    lottery.rewardsBreakdown[5],
    lottery.treasuryFee,
    lottery.cakePerBracket[0],
    lottery.cakePerBracket[1],
    lottery.cakePerBracket[2],
    lottery.cakePerBracket[3],
    lottery.cakePerBracket[4],
    lottery.cakePerBracket[5],
    lottery.countWinnersPerBracket[0],
    lottery.countWinnersPerBracket[1],
    lottery.countWinnersPerBracket[2],
    lottery.countWinnersPerBracket[3],
    lottery.countWinnersPerBracket[4],
    lottery.countWinnersPerBracket[5],
    lottery.firstTicketId,
    lottery.firstTicketIdNextLottery,
    lottery.amountCollectedInCake,
    lottery.finalNumber
  )



def update_lottery(update_all: bool):
  config = mainnet_config
  web3 = Web3(Web3.HTTPProvider(config.rpl))
  web3.middleware_onion.inject(geth_poa_middleware, layer=0)

  with open(f'{base_path}/lottery_abi.json', 'r') as f:
      abi = json.load(f)
  contract = web3.eth.contract(config.contract, abi=abi)

  max_id = 0
  already_processed = set()
  with open(config.lottery_file_path, "r") as f:
    reader = csv.reader(f)
    first = True
    for r in reader:
      if not first:
        max_id = max(max_id, int(r[0]))
        already_processed.add(int(r[0]))
      first = False

  cur = contract.functions.viewCurrentLotteryId().call()

  with open(config.lottery_file_path, "a") as f:
    writer = csv.writer(f)
    start_epoch = 0 if update_all else max_id + 1
    for r in range(start_epoch, cur):
      if r in already_processed:
        continue
      lottery = Lottery(contract.functions.viewLottery(r).call())
      # check if oracle has been called or round cancelled
      if lottery.finalNumber > 0:
        writer.writerow(lottery_to_tuple(r, lottery))
