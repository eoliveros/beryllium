from decimal import Decimal
from typing import Optional
import logging
from pyln.client.lightning import RpcError

import assets
from ln import LnRpc

logger = logging.getLogger(__name__)

def funds_available(asset: str, l2_network: Optional[str], amount_dec: Decimal) -> bool:
    if asset != assets.BTC.symbol or l2_network != assets.BTCLN.symbol:
        return False
    rpc = LnRpc()
    funds = rpc.list_funds()
    sats = assets.asset_dec_to_int(asset, amount_dec * Decimal('1.01')) # add a 1% buffer for fees
    logger.info('required: %d sats, largest channel: %d sats', sats, funds['sats_largest_channel'])
    return funds['sats_largest_channel'] > sats

def withdrawals_supported(asset: str, l2_network: Optional[str]):
    return asset == assets.BTC.symbol and l2_network == assets.BTCLN.symbol

def withdrawal_create(asset: str, l2_network: Optional[str], amount_dec: Decimal, recipient: str):
    assert withdrawals_supported(asset, l2_network)
    rpc = LnRpc()
    try:
        result = rpc.decode_pay(recipient)
        amount_sat = assets.asset_dec_to_int(asset, amount_dec)
        if amount_sat != result['amount_sat']:
            logger.error('ln pay amount does not match: %d, %d', amount_sat, result['amount_sat'])
            return None, 'pay amount does not match'
        result = rpc.pay(recipient)
        if not result:
            logger.error('ln pay failed: %s', recipient)
            return None, 'pay failed'
        logger.info('ln pay made: %s', result['payment_hash'])
        return result['payment_hash'], None
    except RpcError as e:
        logger.error('ln pay error: %s', e.error)
        return None, e.error

def withdrawal_completed(wallet_reference: str) -> bool:
    rpc = LnRpc()
    result = rpc.pay_status_from_hash(wallet_reference)
    if not result and len(result['pays']) != 1:
        logger.error('ln pay not found: %s', wallet_reference)
        return False
    pay = result['pays'][0]
    complete = pay['status'] == 'complete'
    logger.info('ln pay complete: %s', complete)
    return complete
