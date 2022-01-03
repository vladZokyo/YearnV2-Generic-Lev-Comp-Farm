from itertools import count
from brownie import Wei, reverts
from useful_methods import (
    stateOfStrat,
    genericStateOfStrat,
    stateOfVault,
    deposit,
    wait,
    withdraw,
    harvest,
    assertCollateralRatio,
)
import brownie


def test_deleverage_without_flashloans(
    web3,
    chain,
    comp,
    vault,
    enormousrunningstrategy,
    whale,
    gov,
    strategist,
    dai
):
    strategy = enormousrunningstrategy
    currency = dai
    stateOfStrat(strategy, currency, comp)
    print("s")
    strategy.setDyDx(False, {"from": gov})
    print("b")
    strategy.setCollateralTarget(0, {"from": gov})
    print("x")
    vault.updateStrategyDebtRatio(strategy, 0, {"from": gov})
    print("y")
    strategy.harvest({"from": gov})
    print("z")
    stateOfStrat(strategy, currency, comp)
    strategy.harvest({"from": gov})
    stateOfStrat(strategy, currency, comp)
    strategy.harvest({"from": gov})
    stateOfStrat(strategy, currency, comp)
    strategy.harvest({"from": strategist})
    stateOfStrat(strategy, currency, comp)
    strategy.harvest({"from": strategist})
    stateOfStrat(strategy, currency, comp)
    strategy.harvest({"from": strategist})
    stateOfStrat(strategy, currency, comp)
