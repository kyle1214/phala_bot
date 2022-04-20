from substrateinterface import SubstrateInterface
import logging

"""
substrate = SubstrateInterface(
    url="wss://khala.api.onfinality.io/public-ws"
)

def get_worker_account_id_from_pubkey(worker_pubkey:str):

    result = substrate.query(
        module='PhalaMining',
        storage_function='WorkerBindings',
        params=[worker_pubkey]
    )
    print(f"get_worker_account_id_from_pubkey::{result}")
    
    return result
    
def get_worker_mining_info(worker_account_id:str, substrate:SubstrateInterface):
    result = substrate.query(
        module='PhalaMining',
        storage_function='Miners',
        params=[worker_account_id]
    )
    #logging.info(f"get_worker_account_id_from_pubkey::{result}")
    return result

def get_operation_account_from_worker(worker_pubkey:str, substrate:SubstrateInterface):
    result = substrate.query(
        module='PhalaRegistry',
        storage_function='Workers',
        params=[worker_pubkey]
    )
    #logging.info(f"get_worker_account_id_from_pubkey::{result}")
    return result
"""
def get_pool_info(pool_id:int):
    url = "wss://khala.api.onfinality.io/public-ws"
    substrate = SubstrateInterface(
        url=url
    )   
    result = substrate.query(
        module='PhalaStakePool',
        storage_function='StakePools',
        params=[pool_id]
    )
    logging.info(f"get_pool_info::{result}")
    return result


