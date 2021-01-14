from itertools import count
from brownie import Wei, reverts
import eth_abi
from brownie.convert import to_bytes
from useful_methods import genericStateOfStrat,genericStateOfVault
import random
import brownie

# TODO: Add tests here that show the normal operation of this strategy
#       Suggestions to include:
#           - strategy loading and unloading (via Vault addStrategy/revokeStrategy)
#           - change in loading (from low to high and high to low)
#           - strategy operation at different loading levels (anticipated and "extreme")

def test_opsss(currency,strategy, chain,vault, whale,gov,strategist, interface):
    rate_limit = 1_000_000_000 *1e18
    debt_ratio = 10_000
    vault.addStrategy(strategy, debt_ratio, rate_limit, 1000, {"from": gov})

    currency.approve(vault, 2 ** 256 - 1, {"from": whale} )
    whalebefore = currency.balanceOf(whale)
    whale_deposit  = 100 *1e18
    vault.deposit(whale_deposit, {"from": whale})
    strategy.harvest({'from': strategist})

    genericStateOfStrat(strategy, currency, vault)
    genericStateOfVault(vault, currency)

    chain.sleep(2592000)
    chain.mine(1)

    strategy.harvest({'from': strategist})
    steth = interface.ERC20('0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84')

    print("steth = ", steth.balanceOf(strategy)/1e18)
    print("eth = ", strategy.balance()/1e18)

    genericStateOfStrat(strategy, currency, vault)
    genericStateOfVault(vault, currency)

    print("\nEstimated APR: ", "{:.2%}".format(((vault.totalAssets()-100*1e18)*12)/(100*1e18)))

    vault.withdraw({"from": whale})
    print("\nWithdraw")
    genericStateOfStrat(strategy, currency, vault)
    genericStateOfVault(vault, currency)
    print("Whale profit: ", (currency.balanceOf(whale) - whalebefore)/1e18)


def test_migrate(currency,Strategy, strategy, chain,vault, whale,gov,strategist, interface):
    rate_limit = 1_000_000_000 *1e18
    debt_ratio = 10_000
    vault.addStrategy(strategy, debt_ratio, rate_limit, 1000, {"from": gov})

    currency.approve(vault, 2 ** 256 - 1, {"from": whale} )
    whale_deposit  = 100 *1e18
    vault.deposit(whale_deposit, {"from": whale})
    strategy.harvest({'from': strategist})

    genericStateOfStrat(strategy, currency, vault)
    genericStateOfVault(vault, currency)

    chain.sleep(2592000)
    chain.mine(1)

    strategy.harvest({'from': strategist})

    genericStateOfStrat(strategy, currency, vault)
    genericStateOfVault(vault, currency)

    print("\nEstimated APR: ", "{:.2%}".format(((vault.totalAssets()-100*1e18)*12)/(100*1e18)))


    strategy2 = strategist.deploy(Strategy, vault)
    vault.migrateStrategy(strategy, strategy2, {'from': gov})
    genericStateOfStrat(strategy, currency, vault)
    genericStateOfStrat(strategy2, currency, vault)
    genericStateOfVault(vault, currency)

def test_reduce_limit(currency,Strategy, strategy, chain,vault, whale,gov,strategist, interface):
    rate_limit = 1_000_000_000 *1e18
    debt_ratio = 10_000
    vault.addStrategy(strategy, debt_ratio, rate_limit, 1000, {"from": gov})

    currency.approve(vault, 2 ** 256 - 1, {"from": whale} )
    whale_deposit  = 100 *1e18
    vault.deposit(whale_deposit, {"from": whale})
    strategy.harvest({'from': strategist})

    genericStateOfStrat(strategy, currency, vault)
    genericStateOfVault(vault, currency)

    vault.revokeStrategy(strategy, {'from': gov})

    strategy.harvest({'from': strategist})

    genericStateOfStrat(strategy, currency, vault)
    genericStateOfVault(vault, currency)

   