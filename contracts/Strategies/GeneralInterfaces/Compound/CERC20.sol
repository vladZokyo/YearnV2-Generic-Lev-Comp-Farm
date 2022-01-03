// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.6.12;

interface CERC20 {
    function mint(uint mintAmount) external returns (uint);

    function redeemUnderlying(uint redeemAmount) external returns (uint);

    function borrow(uint borrowAmount) external returns (uint);

    function repayBorrow(uint repayAmount) external returns (uint);

    function borrowBalanceCurrent(address account) external returns (uint);

    function exchangeRateCurrent() external returns (uint);

    function balanceOf(address account) external view returns (uint);

    function decimals() external view returns (uint);

    function underlying() external view returns (address);
}
