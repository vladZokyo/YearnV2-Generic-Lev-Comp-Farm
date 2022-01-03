from itertools import count
from brownie import Wei, reverts, chain
from useful_methods import (
    genericStateOfStrat,
    withdraw,
    stateOfStrat,
    genericStateOfVault,
    deposit,
    tend,
    sleep,
    harvest,
    wait
)
import random
import brownie


def test_full_generic(Strategy, FlashLoanPlugin, web3, chain, cdai, Vault, dai, whale, strategist):
    # our humble strategist is going to publish both the vault and the strategy
    currency = dai
    # deploy vault
    vault = strategist.deploy(Vault)
    vault.initialize(currency, strategist, strategist, "", "", strategist, strategist, {"from": strategist})

    deposit_limit = Wei("1_000_000 ether")

    # set limit to the vault
    vault.setDepositLimit(deposit_limit, {"from": strategist})

    # deploy strategy
    strategy = strategist.deploy(Strategy, vault, cdai)
    plugin = FlashLoanPlugin.deploy(
        strategy,
        cdai,
        {'from': strategist}
    )
    plugin.setSOLO("0x1E0447b19BB6EcFdAe1e4AE1694b0C3659614e4e", {'from': strategist})
    plugin.updateMarketId({'from': strategist})

    strategy.setFlashLoanPlugin(plugin, {"from": strategist})
    strategy.setMinCompToSell(0.00001 * 1e18, {"from": strategist})

    debt_ratio = 9_500  # 100%
    vault.addStrategy(strategy, debt_ratio, 0, 2**256-1, 1000, {"from": strategist})

    #genericStateOfStrat(strategy, currency, vault)
    #genericStateOfVault(vault, currency)

    # our humble strategist deposits some test funds
    depositAmount = Wei("501 ether")
    currency.transfer(strategist, depositAmount, {"from": whale})
    starting_balance = currency.balanceOf(strategist)

    deposit(depositAmount, strategist, currency, vault)
    # print(vault.creditAvailable(strategy))
    #genericStateOfStrat(strategy, currency, vault)
    #genericStateOfVault(vault, currency)

    assert strategy.estimatedTotalAssets() == 0
    assert strategy.harvestTrigger(1e15) == True
    strategy.harvest({"from": strategist})
    wait(1, chain)
    strategy.harvest({"from": strategist})

    genericStateOfStrat(strategy, currency, vault)
    genericStateOfVault(vault, currency)

    assert strategy.estimatedTotalAssets() >= depositAmount * 0.999999 * (
        debt_ratio / 10_000
    )  # losing some dust is ok
    assert strategy.harvestTrigger(1) == False

    # whale deposits as well
    whale_deposit = Wei("2000 ether")
    deposit(whale_deposit, whale, currency, vault)
    assert strategy.harvestTrigger(1 * 30 * 1e9) == True
    harvest(strategy, strategist, vault)
    genericStateOfStrat(strategy, currency, vault)
    genericStateOfVault(vault, currency)

    for i in range(5):
        waitBlock = random.randint(10, 50)
        print(f"\n----wait {waitBlock} blocks----")
        sleep(chain, waitBlock)
        cdai.mint(0, {'from': strategist})

        # if harvest condition harvest. if tend tend
        #harvest(strategy, strategist, vault)
        #tend(strategy, strategist)
        strategy.harvest({"from": strategist})
        something = True
        action = random.randint(0, 9)
        if action == 1:
            withdraw(random.randint(50, 100), whale, currency, vault)
        elif action == 2:
            withdraw(random.randint(50, 100), whale, currency, vault)
        elif action == 3:
            deposit(
                Wei(str(f"{random.randint(10000,50000)} ether")), whale, currency, vault
            )
        else:
            something = False

        if something:
            genericStateOfStrat(strategy, currency, vault)
            genericStateOfVault(vault, currency)

    # strategist withdraws
    vault.withdraw({"from": strategist})
    genericStateOfStrat(strategy, currency, vault)
    genericStateOfVault(vault, currency)

    profit = currency.balanceOf(strategist) - starting_balance

    print(Wei(profit).to("ether"), " profit")
    print(vault.strategies(strategy)[6], " total returns of strat")
