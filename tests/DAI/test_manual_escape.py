from itertools import count
from brownie import Wei, reverts, chain
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


def test_manual_escape(
    web3, chain, comp, vault, enormousrunningstrategy, whale, gov, dai, strategist
):
    while enormousrunningstrategy.storedCollateralisation() > 1*1e16:
        print(enormousrunningstrategy.storedCollateralisation()/1e18)
        deposits, borrows = enormousrunningstrategy.getCurrentPosition()
        theolent = borrows/0.795
        space = deposits - theolent
        assert space > 0
        enormousrunningstrategy.manualDeleverage(min(space, borrows), {'from': strategist})
        
    deposits, borrows = enormousrunningstrategy.getCurrentPosition()
    print(deposits/1e18)
    print(borrows/1e18)

    vault.updateStrategyDebtRatio(enormousrunningstrategy, 0, {'from':gov})
    enormousrunningstrategy.harvest({'from': strategist})
    wait(1, chain)
    enormousrunningstrategy.harvest({'from': strategist})
    stateOfStrat(enormousrunningstrategy, dai, comp)
    strState = vault.strategies(enormousrunningstrategy)
    assert strState[5] < 10*1e18  # debt < 10 dai
    assert strState[7] < 10*1e18  # loss < 10 dai

def test_escape_migrate(
    web3, chain, comp, vault, enormousrunningstrategy, whale, Strategy, gov,cdai,  dai, strategist
):
    while enormousrunningstrategy.storedCollateralisation() > 1*1e16:
        print(enormousrunningstrategy.storedCollateralisation()/1e18)
        deposits, borrows = enormousrunningstrategy.getCurrentPosition()
        theolent = borrows/0.795
        space = deposits - theolent
        assert space > 0
        enormousrunningstrategy.manualDeleverage(min(space, borrows), {'from': strategist})
        
    deposits, borrows = enormousrunningstrategy.getCurrentPosition()
    print(deposits/1e18)
    print(borrows/1e18)

    
    strState = vault.strategies(enormousrunningstrategy)
    vstrategy = strategist.deploy(Strategy, vault, cdai)
    enormousrunningstrategy.manualReleaseWant(deposits- (borrows*2), {'from': gov})
    assert dai.balanceOf(enormousrunningstrategy) *1.01 >  strState[5] #most of debt is in want

    #force migrate
    enormousrunningstrategy.setForceMigrate(True, {'from': gov})
    vault.migrateStrategy(enormousrunningstrategy, vstrategy, {'from': gov})
    stateOfStrat(vstrategy, dai, comp)
    strState = vault.strategies(vstrategy)
    assert dai.balanceOf(vstrategy) *1.01 >  strState[5]
