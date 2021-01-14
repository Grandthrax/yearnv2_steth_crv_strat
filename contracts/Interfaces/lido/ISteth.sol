// SPDX-License-Identifier: MIT

pragma solidity 0.6.12;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface ISteth is IERC20 {
    function submit(address) external payable returns (uint256);

}