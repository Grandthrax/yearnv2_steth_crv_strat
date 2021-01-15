// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

import "./interfaces/curve/Curve.sol";
import "./interfaces/lido/ISteth.sol";

import "@openzeppelin/contracts/math/Math.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

import {
    SafeERC20,
    SafeMath,
    IERC20,
    Address
} from "@openzeppelin/contracts/token/ERC20/SafeERC20.sol";

interface IYVault{
    function deposit(uint256 amount, address recipient) external;
    function withdraw(uint256 maxShares) external;
}

contract ZapSteth is Ownable {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    IYVault public yVault = IYVault(address(0xdCD90C7f6324cfa40d7169ef80b12031770B4325));
    ISteth public stETH =  ISteth(address(0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84));
    ICurveFi public StableSwapSTETH = ICurveFi(address(0xDC24316b9AE028F1497c275EB9192a3Ea0f67022));

    IERC20 public want =  IERC20(address(0x06325440D014e39736583c165C2963BA99fAf14E));

    constructor() public Ownable() {
        want.safeApprove(address(yVault), uint256(-1));
        stETH.approve(address(StableSwapSTETH), uint256(-1));
    }

    //we get eth
    receive() external payable {}

    function updateVaultAddress(address _vault) external onlyOwner {
      yVault = IYVault(_vault); 
    }

    //slippage allowance is out of 1000. 20 is 2%

    function zapEthIn(uint256 slippageAllowance) external payable{
        uint256 balanceBegin = address(this).balance;

        if(balanceBegin == 0) return;

        uint256 balance2 = stETH.submit{value: balance/2}(strategist);
        uint256 balanceMid = address(this).balance;
        balance2 = stETH.balanceOf(address(this));

        StableSwapSTETH.add_liquidity{value: balanceMid}([balanceMid, balance2], 0);

        uint256 outAmount = want.balanceOf(address(this));

        require(outAmount.mul(slippageAllowance.add(10000)).div(10000) >= balanceBegin, "TOO MUCH SLIPPAGE");

        yVault.deposit(outAmount, msg.sender);
    }

    function zapStEthIn(uint256 stEthAmount, uint256 slippageAllowance) external {

        stETH.transferFrom(msg.sender, address(this), stEthAmount);

        uint256 balanceBegin = stETH.balanceOf(address(this));

        require(balanceBegin >= stEthAmount, "STEH NOT RECEIVED");

        if(balanceBegin == 0) return;

        StableSwapSTETH.add_liquidity([0, balanceBegin], 0);

        uint256 outAmount = want.balanceOf(address(this));

        require(outAmount.mul(slippageAllowance.add(10000)).div(10000) >= balanceBegin, "TOO MUCH SLIPPAGE");

    }

    function zapEthOut(uint256 lpTokenAmount, uint256 slippageAllowance) external {

    }

    function zapStEthOut(uint256 lpTokenAmount, uint256 slippageAllowance) external {

    }

}