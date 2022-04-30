

drop table phala_user_pid;
create table phala_user_pid (
    chat_id numeric,
    pid int,
    notify boolean,
    Primary Key(chat_id, pid)
);
ALTER TABLE phala_user_pid ADD COLUMN notify boolean;
ALTER TABLE phala_user_pid ALTER COLUMN chat_id TYPE numeric;



drop table phala_pid_owner_info;
create table phala_pid_owner_info (
    pid int,
    owner_address varchar(1000),
    commission int,
    owner_reward numeric,
    cap numeric,
    total_stake numeric,
    free_stake numeric,
    releasing_stake numeric
);

drop table phala_stake_pool;
create table phala_stake_pool (
    pid int,
    worker_pubkey varchar(1000),
    worker_binding varchar(1000),
    Primary Key(pid, worker_pubkey)
);

drop table phala_mining_miners;
create table phala_mining_miners (
    worker_pubkey varchar(1000),
    state varchar(100),
    p_init int,
    p_instant int,
    total_reward numeric,
    Primary Key(worker_pubkey)
);
ALTER TABLE phala_mining_miners ADD COLUMN mining_start_time numeric;
ALTER TABLE phala_mining_miners ADD COLUMN challenge_time_last numeric;
ALTER TABLE phala_mining_miners ADD COLUMN cool_down_start numeric;
