// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import {Account}
from "../../GeneralInterfaces/DyDx/ISoloMargin.sol";

interface IFlashLoanPlugin {

    function setAaveLendingPoolAddressesProvider(
        address _aaveLendginPoolAddressesProvider) external;

    function setSOLO(address _solo) external;

    function doDyDxFlashLoan(
        bool _deficit,
        uint256 _amountDesired
    ) 
    external 
    returns(uint256);

    function callFunction(
        address sender,
        Account.Info memory account,
        bytes memory data
    ) 
    external;

    function doAaveFlashLoan(
        bool deficit, 
        uint256 _flashBackUpAmount
    ) 
    external 
    returns (uint256 amount);
    
    function executeOperation(
        address _reserve,
        uint256 _amount,
        uint256 _fee,
        bytes calldata _params
    ) 
    external;

    function updateMarketId() 
    external;
}
