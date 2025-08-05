from distutils.command.config import config
from enum import Enum
import os
import csv
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from collections import deque
import datetime as dt
from dataclasses import dataclass

class PredictGame(Enum):
  PS_MAINNET = 1
  PRDT_MAINNET = 2
@dataclass
class UpdateConfig:
  rpl: str
  contract: str
  rounds_file_path: str
  latest_file_path: str
  abi: str

base_path = os.path.dirname(os.path.realpath(__file__))

ps_mainnet_config = UpdateConfig(
  rpl="https://bsc-dataseed.binance.org/",
  contract="0x18B2A687610328590Bc8F2e5fEdDe3b582A49cdA",
  rounds_file_path=f"{base_path}/data/v2/main/rounds.csv",
  latest_file_path=f"{base_path}/data/v2/main/latest.csv",
  abi=f'{base_path}/ps_prediction_abi.json'
)

prdt_mainnet_config = UpdateConfig(
  rpl="https://bsc-dataseed.binance.org/",
  contract="0x5C7D19566c330Be63458510AD45B7d5fb6EB7403",
  rounds_file_path=f"{base_path}/data/prdt/rounds.csv",
  latest_file_path=f"{base_path}/data/prdt/latest.csv",
  abi=f'{base_path}/prdt_prediction_abi.json'
)

testnet_config = UpdateConfig(
  rpl="https://data-seed-prebsc-2-s1.binance.org:8545/",
  contract="0x5E5D4d6337Ac83Ef71fEb143669D95073D0e9462",
  rounds_file_path=f"{base_path}/data/v2/test/rounds.csv",
  latest_file_path=f"{base_path}/data/v2/test/latest.csv",
  abi=f'{base_path}/ps_prediction_abi.json'
)

# Round
  # 0  epoch   uint256
  # 1  startTimestamp   uint256
  # 2  lockTimestamp   uint256
  # 3  closeTimestamp   uint256
  # 4  lockPrice   int256
  # 5  closePrice   int256
  # 6  lockOracleId   uint256
  # 7  closeOracleId   uint256
  # 8  totalAmount   uint256
  # 9  bullAmount   uint256
  # 10  bearAmount   uint256
  # 11  rewardBaseCalAmount   uint256
  # 12  rewardAmount   uint256
  # 13  oracleCalled   bool

LATEST_LENGTH = 250

def get_web3(config: UpdateConfig):
  web3 = Web3(Web3.HTTPProvider(config.rpl))
  web3.middleware_onion.inject(geth_poa_middleware, layer=0)

  with open(config.abi, 'r') as f:
      abi = json.load(f)
  contract = web3.eth.contract(config.contract, abi=abi)
  return web3, contract

def update_predict(game: PredictGame, update_all:bool):
  if game == PredictGame.PS_MAINNET:
    return update_predict_ps(update_all)
  elif game == PredictGame.PRDT_MAINNET:
    return update_predict_prdt(update_all)
  else:
    raise Exception("Invalid game")

def update_predict_prdt(update_all: bool):
  config = prdt_mainnet_config
  _, contract = get_web3(config)
  max_epoch = 0
  already_processed = set()
  with open(config.rounds_file_path, "r") as f:
    reader = csv.reader(f)
    first = True
    for r in reader:
      if not first:
        max_epoch = max(max_epoch, int(r[0]))
        already_processed.add(int(r[0]))

      first = False
  cur = contract.functions.currentEpoch().call()
  updated = False
  with open(config.rounds_file_path, "a") as f:
      writer = csv.writer(f)
      start_epoch = 0 if update_all else max_epoch + 1
      print(f"Already processed: {len(already_processed)}")
      print(f"Epochs: {start_epoch} - {cur}")
      for r in range(start_epoch, cur):
        print(f"Epoch {r:5}", end="\r")
        if r in already_processed:
          continue
        data = contract.functions.rounds(r).call()
        timestamps = contract.functions.timestamps(r).call()
        # genesis, completed
        if data[1] or r < cur - 1:
          updated = True
          writer.writerow([r, *data, *timestamps])
  if not updated:
      return

  with open(config.rounds_file_path, "r") as rounds:
    lines = deque(rounds, LATEST_LENGTH)

  with open(config.rounds_file_path, "r") as inp, open(config.latest_file_path, "w") as out:
    lines = list(csv.reader(inp))
    writer = csv.writer(out)
    writer.writerow(lines[0])
    writer.writerows(lines[-LATEST_LENGTH:])

def update_predict_ps(update_all: bool):
  config = ps_mainnet_config
  web3, contract = get_web3(config)

  block_num = web3.eth.get_block_number()
  latest_timestamp = web3.eth.get_block(block_num).timestamp
  # TODO: why does this fail?
  buffer_blocks = 30 # contract.functions.bufferSeconds().call()
      
  max_epoch = 0
  already_processed = set()
  with open(config.rounds_file_path, "r") as f:
    reader = csv.reader(f)
    first = True
    for r in reader:
      if not first:
        max_epoch = max(max_epoch, int(r[0]))
        already_processed.add(int(r[0]))
      first = False

  cur = contract.functions.currentEpoch().call()
  updated = False
  with open(config.rounds_file_path, "a") as f:
    writer = csv.writer(f)
    start_epoch = 0 if update_all else max_epoch + 1
    print(f"Already processed: {len(already_processed)}")
    print(f"Epochs: {start_epoch} - {cur}")
    for r in range(start_epoch, cur):
      print(f"Epoch {r:5}", end="\r")
      if r in already_processed:
        continue
      data = contract.functions.rounds(r).call()
      # check if oracle has been called or round cancelled
      if data[-1] or (latest_timestamp >= (data[3] + buffer_blocks)):
        updated = True
        writer.writerow(data)

  if not updated:
    return

  with open(config.rounds_file_path, "r") as rounds:
    lines = deque(rounds, LATEST_LENGTH)

  with open(config.rounds_file_path, "r") as inp, open(config.latest_file_path, "w") as out:
    lines = list(csv.reader(inp))
    writer = csv.writer(out)
    writer.writerow(lines[0])
    writer.writerows(lines[-LATEST_LENGTH:])
