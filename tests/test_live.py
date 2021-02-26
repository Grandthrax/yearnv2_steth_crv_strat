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

def test_opsss_lvie(currency,live_strategy, chain,live_vault, whale,gov, samdev,strategist, interface):
    strategy = live_strategy
    vault = live_vault
    strategist = samdev
    gov = samdev

    currency.approve(vault, 2 ** 256 - 1, {"from": whale} )
    #whalebefore = currency.balanceOf(whale)
   # whale_deposit  = 100 *1e18
    #vault.deposit(whale_deposit, {"from": whale})
    strategy.harvest({'from': strategist})

    genericStateOfStrat(strategy, currency, vault)
    genericStateOfVault(vault, currency)
    assets = vault.totalAssets()
    print("Share price: ", vault.pricePerShare()/1e18)

    chain.sleep(2592000)
    chain.mine(1)

    strategy.harvest({'from': strategist})
    steth = interface.ERC20('0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84')

    print("steth = ", steth.balanceOf(strategy)/1e18)
    print("eth = ", strategy.balance()/1e18)

    genericStateOfStrat(strategy, currency, vault)
    genericStateOfVault(vault, currency)

    print("\nEstimated APR: ", "{:.2%}".format(((vault.totalAssets()-assets)*12)/(assets)))

   # vault.withdraw({"from": whale})
    print("\nWithdraw")
    genericStateOfStrat(strategy, currency, vault)
    genericStateOfVault(vault, currency)
  # print("Whale profit: ", (currency.balanceOf(whale) - whalebefore)/1e18)


def test_migrate_live(currency,Strategy, ychad, voter_proxy, live_strategy,live_vault, chain,samdev, interface):
    strategy = live_strategy
    vault = live_vault
    strategist = samdev
    gov = samdev

    #strategy.harvest({'from': strategist})

    genericStateOfStrat(strategy, currency, vault)
    genericStateOfVault(vault, currency)


    strategy2 = strategist.deploy(Strategy, vault)
    ppsBefore = vault.pricePerShare()
    #strategy2 = Strategy.at('0xebfC9451d19E8dbf36AAf547855b4dC789CA793C')

    

    vault.migrateStrategy(strategy, strategy2, {'from': ychad})
    voter_proxy.approveStrategy(strategy2.gauge(), strategy2, {"from": ychad})


    assert vault.pricePerShare() == ppsBefore
    vault.setManagementFee(0, {'from': ychad})
    strategy2.harvest({'from': strategist})
    assert vault.pricePerShare() >= ppsBefore
    ppsBefore = vault.pricePerShare()
    strategy.harvest({'from': strategist})
    assert vault.pricePerShare() >= ppsBefore
    print(vault.pricePerShare() - ppsBefore)
    before = vault.totalAssets()

    chain.sleep(86400)
    chain.mine(1)

    strategy2.harvest({'from': strategist})
    #strategy2.harvest({'from': strategist})


    steth = interface.ERC20('0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84')
    ldo = interface.ERC20('0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32')
    genericStateOfStrat(strategy, currency, vault)
    genericStateOfStrat(strategy2, currency, vault)
    genericStateOfVault(vault, currency)
    stethbal = steth.balanceOf(strategy)
    ethbal = strategy.balance()
    wantBal = currency.balanceOf(strategy)
    ldoBal = ldo.balanceOf(strategy)
    print("steth1 = ", stethbal/1e18)
    print("eth1 = ", ethbal/1e18)
    print("want1 = ", wantBal/1e18)
    print("ldo1 = ", wantBal/1e18)
    stethbal = steth.balanceOf(strategy2)
    ethbal = strategy2.balance()
    wantBal = currency.balanceOf(strategy2)
    ldoBal = ldo.balanceOf(strategy2)
    print("steth2 = ", stethbal/1e18)
    print("eth2 = ", ethbal/1e18)
    print("want2 = ", wantBal/1e18)
    print("ldo2 = ", wantBal/1e18)

    print("\nEstimated APR: ", "{:.2%}".format(((vault.totalAssets()-before)*365)/(before)))

    strategy3 = strategist.deploy(Strategy, vault)
    vault.migrateStrategy(strategy2, strategy3, {'from': ychad})
    voter_proxy.approveStrategy(strategy3.gauge(), strategy3, {"from": ychad})
    strategy3.harvest({'from': strategist})
    genericStateOfStrat(strategy3, currency, vault)
    genericStateOfStrat(strategy2, currency, vault)
    genericStateOfVault(vault, currency)