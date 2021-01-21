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

interface IYVault is IERC20 {
    function deposit(uint256 amount, address recipient) external;
    function withdraw() external;
}

contract ZapSteth is Ownable {
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    IYVault public yVault = IYVault(address(0xdCD90C7f6324cfa40d7169ef80b12031770B4325));
    ISteth public stETH =  ISteth(address(0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84));

    //slippage allowance is out of 10000. 20 is 2%
    ICurveFi public StableSwapSTETH = ICurveFi(address(0xDC24316b9AE028F1497c275EB9192a3Ea0f67022));

    IERC20 public want =  IERC20(address(0x06325440D014e39736583c165C2963BA99fAf14E));

    uint256 public constant DEFAULT_SLIPPAGE = 50;
    bool private _noReentry = false;

    constructor() public Ownable() {
        want.safeApprove(address(yVault), uint256(-1));
        want.safeApprove(address(StableSwapSTETH), uint256(-1));
        stETH.approve(address(StableSwapSTETH), uint256(-1));
    }

    //we get eth
    receive() external payable {    
        if(_noReentry){
            return;
        }
        _zapEthIn(DEFAULT_SLIPPAGE);
    }

    function updateVaultAddress(address _vault) external onlyOwner {
      yVault = IYVault(_vault); 
      want.safeApprove(_vault, uint256(-1));
    }

    function zapEthIn(uint256 slippageAllowance) external payable{
        if(_noReentry){
            return;
        }

        _zapEthIn(slippageAllowance);
    }

    function _zapEthIn(uint256 slippageAllowance) internal {
        uint256 balanceBegin = address(this).balance;

        if(balanceBegin < 2) return;

        uint256 halfBal = balanceBegin.div(2);


        //test if we should buy instead of mint
        uint256 out = StableSwapSTETH.get_dy(0,1,halfBal);

        if(out < halfBal){
           stETH.submit{value: halfBal}(owner());
        }

         
        uint256 balanceMid = address(this).balance;
        uint256 balance2 = stETH.balanceOf(address(this));

        StableSwapSTETH.add_liquidity{value: balanceMid}([balanceMid, balance2], 0);

        uint256 outAmount = want.balanceOf(address(this));

        require(outAmount.mul(slippageAllowance.add(10000)).div(10000) >= balanceBegin, "TOO MUCH SLIPPAGE");

        yVault.deposit(outAmount, msg.sender);
    }

    function zapStEthIn(uint256 stEthAmount, uint256 slippageAllowance) external {

        require(stEthAmount != 0, "0 stETH");

        stETH.transferFrom(msg.sender, address(this), stEthAmount);

        uint256 balanceBegin = stETH.balanceOf(address(this));
        require(balanceBegin >= stEthAmount, "NOT ALL stETH RECEIVED");

        StableSwapSTETH.add_liquidity([0, balanceBegin], 0);

        uint256 outAmount = want.balanceOf(address(this));

        require(outAmount.mul(slippageAllowance.add(10000)).div(10000) >= balanceBegin, "TOO MUCH SLIPPAGE");

        yVault.deposit(outAmount, msg.sender);
    }

    function zapEthOut(uint256 lpTokenAmount, uint256 slippageAllowance) external {
        _zapOut(lpTokenAmount, slippageAllowance, 0);

    }
    function zapStEthOut(uint256 lpTokenAmount, uint256 slippageAllowance) external {
        _zapOut(lpTokenAmount, slippageAllowance, 1);
    }

    //There should never be any tokens in this contract
    function rescueTokens(address token, uint256 amount) external onlyOwner {

        if(token == address(0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE)){
            amount = Math.min(address(this).balance, amount);
            msg.sender.transfer(amount);
        }else{

            IERC20 want = IERC20(token);
            amount = Math.min(want.balanceOf(address(this)), amount);
            want.safeTransfer(msg.sender, amount);
        }
    }

    function _zapOut(uint256 lpTokenAmount, uint256 slippageAllowance, int128 zero_if_eth) internal {
        require(yVault.balanceOf(msg.sender) >= lpTokenAmount, "NOT ENOUGH BALANCE");
        yVault.transferFrom(msg.sender, address(this), lpTokenAmount);

        yVault.withdraw();

        uint256 balance = want.balanceOf(address(this));
        require(balance > 0, "no balance");
        
        _noReentry = true;
        StableSwapSTETH.remove_liquidity_one_coin(balance, zero_if_eth, 0);
        _noReentry = false;

        uint256 endBalance;
        if(zero_if_eth == 0){
            endBalance = address(this).balance;
            msg.sender.transfer(endBalance);
        }else{
            endBalance = stETH.balanceOf(address(this));
            stETH.transfer(msg.sender, endBalance);
        }

        require(endBalance.mul(slippageAllowance.add(10000)).div(10000) >= balance, "TOO MUCH SLIPPAGE");

        uint256 leftover = yVault.balanceOf(address(this));
        if(leftover >0){
            yVault.transfer(msg.sender, endBalance);
        }
        
    }

}