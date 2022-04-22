import logging
import math
from xmlrpc.client import Boolean
import common

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

def insert_user_pid(chat_id:int, pool_id:int):
    try:
        conn = common.get_connection()
        with conn:
            with conn.cursor() as cur:
                query_string = f"INSERT INTO phala_user_pid ( chat_id, pid ) VALUES({chat_id},{pool_id})"
                cur.execute(query_string)
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def insert_pid_owner_info(pool_id:int, owner_address:str, commission:int, owner_reward:int, cap:int, total_stake:int, free_stake:int, releasing_stake:int ):
    try:
        conn = common.get_connection()
        with conn:
            with conn.cursor() as cur:
                if cap == None:
                    cap = -1
                query_string = f"INSERT INTO phala_pid_owner_info ( pid, owner_address, commission, owner_reward, cap, total_stake, free_stake, releasing_stake )" \
                        f"VALUES({pool_id}, '{owner_address}', {commission}, {owner_reward}, {cap}, {total_stake}, {free_stake}, {releasing_stake})"
                cur.execute(query_string)
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def insert_phala_stake_pool(pid:int, worker_pubkey:str):
    try:
        conn = common.get_connection()
        with conn:
            with conn.cursor() as cur:
                query_string = f"INSERT INTO phala_stake_pool ( pid, worker_pubkey )" \
                        f"VALUES({pid}, '{worker_pubkey}')"
                cur.execute(query_string)
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
        
def get_pid_from_chat_id(chat_id:int):
    try:
        conn = common.get_connection()
        with conn:
            with conn.cursor() as cur:
                query_string = f"SELECT pid from phala_user_pid WHERE chat_id={chat_id} "
                cur.execute(query_string)
                pid_list = cur.fetchall()
                
                return pid_list
    except Exception as e:
        raise e
    finally:
        conn.close()

def get_owner_address_by_pid(pid:int):
    try:
        conn = common.get_connection()
        with conn:
            with conn.cursor() as cur:
                query_string = f"SELECT owner_address from phala_pid_owner_info WHERE pid={pid} "

                cur.execute(query_string)
                owner_address = cur.fetchone()[0]
                
                return owner_address
    except Exception as e:
        raise e
    finally:
        conn.close()

def del_user_pid_info(pid:int):
    try:
        conn = common.get_connection()
        with conn:
            with conn.cursor() as cur:
                query_string = f"DELETE FROM phala_stake_pool WHERE  pid = {pid}"
                cur.execute(query_string)
                query_string = f"DELETE FROM phala_user_pid WHERE  pid = {pid}"
                cur.execute(query_string)
                query_string = f"DELETE FROM phala_pid_owner_info WHERE  pid = {pid}"
                cur.execute(query_string)
                
            conn.commit()
    except Exception as e:
        raise e
    finally:
        conn.close()

def get_worker_pubkey_by_pid(pid:int):
    try:
        conn = common.get_connection()
        with conn:
            with conn.cursor() as cur:
                query_string = f"SELECT worker_pubkey from phala_stake_pool WHERE pid={pid} "

                cur.execute(query_string)
                owner_address = cur.fetchall()
                
                return owner_address
    except Exception as e:
        raise e
    finally:
        conn.close()
    
def get_worker_status(worker_pubkey:str):
    try:
        conn = common.get_connection()
        with conn:
            with conn.cursor() as cur:
                query_string = f"SELECT state, p_instant, total_reward, mining_start_time, challenge_time_last, cool_down_start from phala_mining_miners WHERE worker_pubkey='{worker_pubkey}' "

                cur.execute(query_string)
                result = cur.fetchall()
                
                if not result:
                    return False
                   
                return_value = {
                    'state': result[0][0],
                    'p_instant': result[0][1],
                    'total_reward': result[0][2],
                    'mining_start_time': result[0][3],
                    'challenge_time_last': result[0][4],
                    'cool_down_start': result[0][5]
                }

                return return_value
    except Exception as e:
        raise e
    finally:
        conn.close()
    
def get_pool_info(pid:str):
    try:
        conn = common.get_connection()
        with conn:
            with conn.cursor() as cur:
                query_string = f"SELECT owner_address, commission, owner_reward, cap, total_stake, free_stake, releasing_stake " \
                    f"from phala_pid_owner_info WHERE pid='{pid}' "

                cur.execute(query_string)
                result = cur.fetchall()
                
                if not result:
                    return False
                   
                return_value = {
                    'owner_address': result[0][0],
                    'commission': result[0][1],
                    'owner_reward': result[0][2],
                    'cap': result[0][3],
                    'total_stake': result[0][4],
                    'free_stake': result[0][5],
                    'releasing_stake': result[0][6]
                }

                return return_value
    except Exception as e:
        raise e
    finally:
        conn.close()

def get_user_notify_info(chat_id:int, pid:int) -> bool:
    conn = common.get_connection()
    with conn:
        with conn.cursor() as cur:
            query_string = f"SELECT notify FROM phala_user_pid WHERE chat_id={chat_id} AND pid={pid}"
            cur.execute(query_string)
            notify_info = cur.fetchone()
            if notify_info == None:
                return False
            else:
                notify_info = bool(notify_info[0])
    return notify_info

def set_user_notify_info(chat_id:int, pid:int, notify:Boolean):
    conn = common.get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                query_string = f"UPDATE phala_user_pid SET notify = {notify} " \
                        f"WHERE chat_id = {chat_id} AND pid = {pid}"
                cur.execute(query_string)
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
        
def get_all_registered_chat_id():
    conn = common.get_connection()
    with conn:
        with conn.cursor() as cur:
            query_string = f"SELECT DISTINCT chat_id FROM phala_user_pid"
            cur.execute(query_string)
            result = cur.fetchall()
            tmp = []
            for row in result:
                chat_id = row[0]
                tmp.append(chat_id)
    conn.close()
    return tmp

def get_noti_pid_from_chat_id(chat_id:int):
    try:
        conn = common.get_connection()
        with conn:
            with conn.cursor() as cur:
                query_string = f"SELECT pid from phala_user_pid WHERE chat_id={chat_id} AND notify=True"
                cur.execute(query_string)
                pid_list = cur.fetchall()
                
                return pid_list
    except Exception as e:
        raise e
    finally:
        conn.close()

def get_noti_worker_status(worker_pubkey:str):
    try:
        conn = common.get_connection()
        with conn:
            with conn.cursor() as cur:
                query_string = f"SELECT state, p_instant from phala_mining_miners WHERE worker_pubkey='{worker_pubkey}' AND (state != 'MiningIdle' OR p_instant = 0)"
                cur.execute(query_string)
                pid_list = cur.fetchall()
                
                return pid_list
    except Exception as e:
        raise e
    finally:
        conn.close()