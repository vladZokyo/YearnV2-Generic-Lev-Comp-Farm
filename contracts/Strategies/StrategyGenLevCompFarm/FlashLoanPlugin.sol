// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import {IERC20} 
from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20}
from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";
import {SafeMath}
from "@openzeppelin/contracts/math/SafeMath.sol";
// Vault.
import {VaultAPI} 
from "../../Vault/BaseStrategy.sol";
import {IStrategy}
from "./Interfaces/IStrategy.sol";
// DyDx.
import {DydxFlashloanBase} 
from "../GeneralInterfaces/DyDx/DydxFlashLoanBase.sol";
import {ISoloMargin, Account, Actions}
from "../GeneralInterfaces/DyDx/ISoloMargin.sol";
import {ICallee}
from "../GeneralInterfaces/DyDx/ICallee.sol";
// Compound.
import {CErc20I} 
from "../GeneralInterfaces/Compound/CErc20I.sol";
// AAVE.
import {ILendingPool}
from "../GeneralInterfaces/Aave/ILendingPool.sol";
import {ILendingPoolAddressesProvider}
from "../GeneralInterfaces/Aave/ILendingPoolAddressesProvider.sol";


contract FlashLoanPlugin is ICallee, DydxFlashloanBase {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    IERC20 internal want;
    CErc20I internal cToken;
    address internal SOLO;
    IStrategy internal strategy;

    bool internal awaitingFlash = false;

    uint256 public dyDxMarketId;

    // @notice emitted when trying to do Flash Loan. flashLoan address is 0x00 when no flash loan used
    event Leverage(uint256 amountRequested, uint256 amountGiven, bool deficit, address flashLoan);
    event Debug(uint256 s);

    modifier onlyAutorized() 
    {
        require(msg.sender == strategy.strategist() ||
        msg.sender == VaultAPI(strategy.vault()).governance(), "!autorized");
        _;
    }

    constructor (
        address _strategy,
        address _cToken
        )
    public 
    {
        strategy = IStrategy(_strategy); 
        cToken = CErc20I(_cToken);

        want = IERC20(strategy.want());
        want.approve(_strategy, uint256(-1));
    }

    function updateMarketId() 
    external 
    onlyAutorized 
    {
        _setMarketIdFromTokenAddress();
    }

    function setSOLO(address _solo) 
    external 
    onlyAutorized
    {   
        want.approve(SOLO, 0);
        SOLO = _solo;
        want.approve(SOLO, uint256(-1));
    }

    // Flash loan DXDY
    // amount desired is how much we are willing for position to change
    function doDyDxFlashLoan(
        bool _deficit,
        uint256 _amountDesired
    ) 
    external 
    returns(uint256) 
    {
        require(msg.sender == address(strategy), "not strategy!");
        uint256 amount = _amountDesired;
        ISoloMargin solo = ISoloMargin(SOLO);

        // Not enough want in DyDx. So we take all we can.
        uint256 amountInSolo = want.balanceOf(SOLO);
        if (amountInSolo < amount) {
            amount = amountInSolo;
        }
        // we need to overcollateralise on way back
        uint256 repayAmount = amount.add(2); 

        bytes memory data = abi.encode(_deficit, amount, repayAmount);

        // 1. Withdraw $
        // 2. Call callFunction(...)
        // 3. Deposit back $
        Actions.ActionArgs[] memory operations = new Actions.ActionArgs[](3);

        operations[0] = _getWithdrawAction(dyDxMarketId, amount);
        operations[1] = _getCallAction(
            // Encode custom data for callFunction
            data
        );
        operations[2] = _getDepositAction(dyDxMarketId, repayAmount);

        Account.Info[] memory accountInfos = new Account.Info[](1);
        accountInfos[0] = _getAccountInfo();
        
        solo.operate(accountInfos, operations);

        emit Leverage(_amountDesired, amount, _deficit, SOLO);

        return amount;
    }
    
    function _setMarketIdFromTokenAddress() internal {
        ISoloMargin solo = ISoloMargin(SOLO);

        uint256 numMarkets = solo.getNumMarkets();

        address curToken;
        for (uint256 i = 0; i < numMarkets; i++) {
            curToken = solo.getMarketTokenAddress(i);

            if (curToken == address(want)) {
                dyDxMarketId = i;
                return;
            }
        }

        revert("No marketId found for provided token");
    }

    function callFunction(
        address sender,
        Account.Info memory account,
        bytes memory data
    ) 
    external
    override
    {
        (bool deficit, uint256 amount, uint256 repayAmount) = abi.decode(data, (bool, uint256, uint256));
        require(msg.sender == SOLO, "NOT_SOLO");

        _loanLogic(deficit, amount, repayAmount);    
    }

    //called by flash loan
    function _loanLogic(
        bool deficit,
        uint256 amount,
        uint256 repayAmount
    ) 
    internal 
    {   
        emit Debug(3333);
        want.transfer(address(strategy), want.balanceOf(address(this)));
        strategy.useLoanTokens(deficit, amount, repayAmount);
    }
}
