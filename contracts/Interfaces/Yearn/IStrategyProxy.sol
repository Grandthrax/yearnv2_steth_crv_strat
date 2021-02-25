pragma solidity >=0.6.12;

interface IStrategyProxy {
    function withdraw(
        address _gauge,
        address _token,
        uint256 _amount
    ) external returns (uint256);

    function balanceOf(address _gauge) external view returns (uint256);

    function withdrawAll(address _gauge, address _token) external returns (uint256);

    function deposit(address _gauge, address _token) external;

    function harvest(address _gauge) external;

    function lock() external;
    function claimRewards(address _gauge, address _token) external;

    function approveStrategy(address _gauge, address _strategy) external;
}