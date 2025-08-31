import subprocess
from update_lottery import update_lottery
from update_predict import PredictGame, update_predict
import os
import datetime as dt

base_path = os.path.dirname(os.path.realpath(__file__))

def commit():
  subprocess.call(['sh', f'{base_path}/update-git.sh'])

if __name__ == "__main__":
  # update(config=testnet, update_all=False)
  update_predict(game=PredictGame.PS_MAINNET, update_all=False)
  update_predict(game=PredictGame.PRDT_MAINNET, update_all=False)
  update_lottery(update_all=False)
  commit()
