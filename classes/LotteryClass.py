from dataclasses import dataclass
from typing import List
from enum import Enum

class LotteryStatus(Enum):
  Pending = 0
  Open = 1
  Close = 2
  Claimable = 3

@dataclass
class Lottery:
  status: LotteryStatus
  startTime: int
  endTime: int
  priceTicketInCake: int
  discountDivisor: int
  rewardsBreakdown: List[int]
  treasuryFee: int
  cakePerBracket: List[int]
  countWinnersPerBracket: List[int]
  firstTicketId: int
  firstTicketIdNextLottery: int
  amountCollectedInCake: int
  finalNumber: int

  def __init__(self, t: List):
    self.status = LotteryStatus(t[0])
    self.startTime = t[1]
    self.endTime = t[2]
    self.priceTicketInCake = t[3]
    self.discountDivisor = t[4]
    self.rewardsBreakdown = t[5]
    self.treasuryFee = t[6]
    self.cakePerBracket = t[7]
    self.countWinnersPerBracket = t[8]
    self.firstTicketId = t[9]
    self.firstTicketIdNextLottery = t[10]
    self.amountCollectedInCake = t[11]
    self.finalNumber = t[12]
