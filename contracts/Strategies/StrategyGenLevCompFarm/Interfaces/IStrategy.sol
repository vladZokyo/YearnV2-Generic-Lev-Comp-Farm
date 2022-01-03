// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.6.12;

interface IStrategy {

    function vault() external view returns (address);

    function want() external view returns (address);

    function strategist() external view returns (address);

    function useLoanTokens(
        bool deficit,
        uint256 amount,
        uint256 repayAmount
    )
    external;
}