from substrateinterface import SubstrateInterface
import logging
import common
import datetime

url = "wss://khala.api.onfinality.io/public-ws"
substrate = SubstrateInterface(
    url=url
)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

def update_phala_stake_pool_info():
    try:
        conn = common.get_connection()
        with conn:
            with conn.cursor() as cur:
                query_string = f"SELECT pid FROM phala_user_pid"
                cur.execute(query_string)
                pid_list = cur.fetchall()
                
                query_string = "DELETE FROM phala_stake_pool"
                cur.execute(query_string)
                
                for pid in pid_list:
                    result = substrate.query(
                        module='PhalaStakePool',
                        storage_function='StakePools',
                        params=[pid[0]]
                    )
                    result_pid = result['workers']
                    for worker_pubkey in result_pid:
                        result = substrate.query(
                            module='PhalaMining',
                            storage_function='WorkerBindings',
                            params=[worker_pubkey.value]
                        )

                        worker_binding = result
                        query_string = f"INSERT INTO phala_stake_pool ( pid, worker_pubkey, worker_binding ) VALUES({pid[0]},'{worker_pubkey}', '{worker_binding}')" \
                                    f"ON CONFLICT ( pid, worker_pubkey ) " \
                                    f"DO UPDATE SET  worker_binding = {worker_binding}" 
                        logging.info(f"update_phala_stake_pool_info::{query_string}")
                        cur.execute(query_string)
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def insert_worker_status():
    try:
        conn = common.get_connection()
        with conn:
            with conn.cursor() as cur:
                query_string = f"SELECT worker_binding, worker_pubkey FROM phala_stake_pool"
                cur.execute(query_string)
                miner_list = cur.fetchall()
                
                query_string = "DELETE FROM phala_mining_miners"
                cur.execute(query_string)
                
                for miner in miner_list:
                    result = substrate.query(
                        module='PhalaMining',
                        storage_function='Miners',
                        params=[miner[0]]
                    )

                    worker_pubkey = miner[1]
                    state = result['state']
                    p_init = result['benchmark']['p_init']
                    p_instant = result['benchmark']['p_instant']
                    total_reward = result['stats']['total_reward']
                    
                    mining_start_time = result['benchmark']['mining_start_time'].value
                    challenge_time_last = result['benchmark']['challenge_time_last'].value
                    cool_down_start = result['cool_down_start'].value
                    
                    logging.info(f"insert_worker_status:result:{result}")
                    print(f"mining_start_time: {datetime.datetime.fromtimestamp(mining_start_time)}")
                    print(f"challenge_time_last: {datetime.datetime.fromtimestamp(challenge_time_last)}")
                    print(f"cool_down_start: {datetime.datetime.fromtimestamp(cool_down_start)}")
                    
                    query_string = f"INSERT INTO phala_mining_miners ( worker_pubkey, state, p_init, p_instant, total_reward, mining_start_time, challenge_time_last, cool_down_start ) " \
                        f"VALUES('{worker_pubkey}', '{state}', {p_init}, {p_instant}, {total_reward}, {mining_start_time}, {challenge_time_last}, {cool_down_start})"
                    logging.info(f"insert_worker_status::{query_string}")
                    cur.execute(query_string)
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
def insert_pool_info():
    try:
        conn = common.get_connection()
        with conn:
            with conn.cursor() as cur:
                query_string = f"SELECT pid FROM phala_user_pid"
                cur.execute(query_string)
                pid_list = cur.fetchall()
                
                query_string = "DELETE FROM phala_pid_owner_info"
                cur.execute(query_string)
                
                for pid in pid_list:
                    pool_id = pid[0]
                    logging.info(f"insert_pool_info:pid:{pool_id}")
                    result = substrate.query(
                        module='PhalaStakePool',
                        storage_function='StakePools',
                        params=[pool_id]
                    )
                    owner_address = result['owner'].value
                    commission = result['payout_commission'].value
                    owner_reward = result['owner_reward']
                    cap = result['cap'].value
                    total_stake = result['total_stake'].value
                    free_stake = result['free_stake'].value
                    releasing_stake = result['releasing_stake'].value
                    worker_list = result['workers']
                    if cap == None:
                        cap = -1
                    if commission == None:
                        commission = 0
                    query_string = f"INSERT INTO phala_pid_owner_info ( pid, owner_address, commission, owner_reward, cap, total_stake, free_stake, releasing_stake )" \
                            f"VALUES({pool_id}, '{owner_address}', {commission}, {owner_reward}, {cap}, {total_stake}, {free_stake}, {releasing_stake})"

                    logging.info(f"insert_pool_info::{query_string}")
                    cur.execute(query_string)
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
        
                
if __name__ == '__main__':
    update_phala_stake_pool_info()
    insert_worker_status()
    insert_pool_info()