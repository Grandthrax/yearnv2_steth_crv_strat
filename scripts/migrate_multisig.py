import warnings
import csv
from collections import Counter
from copy import copy
from typing import List, Union
from decimal import Decimal

from eth_account.messages import encode_defunct
from eth_account import Account
import click
import requests
import toml
from brownie import Contract, CurveZap, Wei, accounts, chain, history, interface, network, rpc, web3
from brownie.exceptions import BrownieEnvironmentWarning
from brownie.network.transaction import TransactionReceipt
from eth_abi import encode_abi
from eth_utils import is_address
from gnosis.eth import EthereumClient
from gnosis.safe import Safe, SafeOperation
from gnosis.safe.multi_send import MultiSend, MultiSendOperation, MultiSendTx
from gnosis.safe.safe_tx import SafeTx

warnings.simplefilter("ignore", BrownieEnvironmentWarning)

SAFE_API = "https://safe-transaction.mainnet.gnosis.io/api/v1/"


def get_signer(account=None):