from multiprocessing import pool
from substrateinterface import SubstrateInterface
import logging
import datetime
import threading
import worker, common, info_from_db, info_from_subscan
from telegram import Bot, InputTextMessageContent, ParseMode, ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    PicklePersistence,
    CallbackContext,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
CHOICE, REGISTER, DELETING, TYPING_SEARCHING, SEARCHING, TYPING_REPLY, NOTIFYING = range(7)

reply_keyboard = [
    ['Register🔖','Search🔎'],['Delete⛔','Support🆘']
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)

def get_ref_url_inlinebutton() -> InlineKeyboardMarkup:
    keyboard = [
        #[
        #    InlineKeyboardButton("SubStake.app✨", url='https://substake.app/moonbeam/active')
        #],
        [
            InlineKeyboardButton("Staking DApp", url='https://app.phala.network/mining/'),
        ]
    ]       
    return InlineKeyboardMarkup(keyboard)

def get_pidlist_by_chatid(chat_id):
    result = info_from_db.get_pid_from_chat_id(chat_id)
    pid_list = list()
    
    for tmp in result:
        pid_list.append(tmp[0])
        
    return pid_list

def short_addr2(collator_address:str) -> str:
    collator_address = collator_address[:17] + "..." + collator_address[len(collator_address)-15:]
    return collator_address

def short_addr(collator_address:str) -> str:
    print(collator_address)
    collator_address = collator_address[:6] + "..." + collator_address[len(collator_address)-6:]
    return collator_address

def support(update: Update, context: CallbackContext) -> None: 
    reply_text = f'SubStake✨ Team \n\n' \
                 f' Any issues? Please feel free to let us know. \n\n' \
                 f' 📡 [SubStake Support Channel](https://t.me/substake_support) \n' \
                 f' 📡 [Phala Korean Community Channel](https://t.me/phalakorean) \n' 
    update.message.reply_text(
        reply_text, parse_mode='Markdown'
    )

def error_handler(update: object, context: CallbackContext) -> int:
    
    logging.error(msg=f'Exception while handling an update:[{update.message.from_user.first_name}][{update.message.from_user.id}]', exc_info=context.error)
    
    message = (
        f'An exception was raised while prcessing\n'
        f'Please /start bot again'
    )
    keyboard = [
        ["/start","Support🆘"]
    ]
    
    update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return ConversationHandler.END
        
def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation, display any stored data and ask user for input."""
    user = update.message.from_user
    reply_text = ''
    chat_id = update.message.from_user.id

    pid_list = get_pidlist_by_chatid(chat_id)
        
    if pid_list:
        reply_text +=  "Your registered PID(s): \n"
        for key in pid_list:
            reply_text += f'\t🌀 {key}\n'
    else:
        reply_text += f'Hello {user.first_name}\nWelcome to Phala miner check bot Provided by SubStake✨ \n\n'
        reply_text += 'Bot doesn\'t have any your wallet information\n'
        reply_text += 'Please register your Pool ID first\n'
        
    
    logging.info(":::start:" + str(context.user_data))

    update.message.reply_text(reply_text, reply_markup=markup)

    return CHOICE
def register_address(update: Update, context: CallbackContext) -> int:
    """Show new choice of buttons"""
    chat_id = update.message.from_user.id
    keyboard = [
        [
            "Back🔙"
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, input_field_placeholder=f'Type Your POOL ID', resize_keyboard=True)
    
    reply_text = f'Input Your PID. It will take a few seconds while check your account.\n\n'
    
    result = info_from_db.get_pid_from_chat_id(chat_id)
    pid_list = list()
    for tmp in result:
        pid_list.append(tmp[0])
    
    
    if pid_list:
        reply_text +=  f'You have registered {len(pid_list)} PID(s): \n'
        for key in pid_list:
            reply_text += f'\t🌀 {key}\n'
        reply_text +=  f'Please input your PID if you want to add more.'
    
    update.message.reply_text(
        text=reply_text
             , reply_markup=reply_markup
    )
    return TYPING_REPLY

def received_information(update: Update, context: CallbackContext) -> int:
    """Store info provided by user and ask for the next category."""
    pool_id = update.message.text
    logging.info("received_information::text: " + pool_id)
    
    chat_id = update.message.from_user.id
    
    result = info_from_db.get_pid_from_chat_id(chat_id)
    pid_list = list()
    
    for tmp in result:
        pid_list.append(tmp[0])
      
    if int(pool_id) in pid_list:
        update.message.reply_text(
        f'You already registered PID: {pool_id}',
        reply_markup=markup, 
        )
        return CHOICE
    
    result = worker.get_pool_info(pool_id)
    reply_text = 'Not registered..'
    if not result == None:
        pool_id = result['pid']
        owner_address = result['owner'].value
        commission = result['payout_commission'].value
        owner_reward = result['owner_reward']
        cap = result['cap'].value
        total_stake = result['total_stake'].value
        free_stake = result['free_stake'].value
        releasing_stake = result['releasing_stake'].value
        worker_list = result['workers']
        
        info_from_db.insert_pid_owner_info(pool_id, owner_address, commission, owner_reward, cap, total_stake, free_stake, releasing_stake)
        info_from_db.insert_user_pid(chat_id, pool_id)
        
        reply_text = f" 🌀 PID : {pool_id}\n"
        reply_text += f" 🧰 Owner Address : {short_addr(owner_address)}\n"
        reply_text += f" ⚖️ Commission : {commission/10**4}%\n"
        reply_text += f" 🖥️ Worker\n"
        for miner in worker_list:
            reply_text += f"  ⚒️ {short_addr2(miner.value)}\n"
            info_from_db.insert_phala_stake_pool(pool_id, miner)
        reply_text += "\n🌟 Pool succefully registered\n"
    update.message.reply_text(
        reply_text,
        reply_markup=markup, 
    )
    return CHOICE

def delete(update: Update, context: CallbackContext) -> int:
    chat_id = update.message.from_user.id

    pid_list = get_pidlist_by_chatid(chat_id)
        
    if not pid_list:
        update.message.reply_text(text='You didn\'t register any PID yet. Please register your PID first.')
        return CHOICE
    
    logging.info(f"delete::pid_list")
    reply_text = f'Please select address to delete.'
    keyboard = []
    
    for pid in pid_list:
        keyboard_list =[]
        keboard_text = f'{pid}'
        keyboard_list.append(f"PID : {keboard_text}")
        keyboard.append(keyboard_list) 
        logging.info("delete::keyboard_data:"+(keboard_text)) 
        
    keyboard.append(["Delete All⛔", "Back🔙"])
    logging.info("delete::keyboard_list:"+str(keyboard))        
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)        
    update.message.reply_text(reply_text,reply_markup=reply_markup)
    
    return DELETING

def delete_address(update: Update, context: CallbackContext) -> int:
    text = update.message.text
   
    text = text[6:]
    logging.info("delete_address::text:"+text)
    info_from_db.del_user_pid_info(int(text))

    update.message.reply_text(
        text=f'{text} is deleted..\n',
        reply_markup=markup, 
    )
    return CHOICE       

def delete_all(update: Update, context: CallbackContext) -> int:
    
    chat_id = update.message.from_user.id

    pid_list = get_pidlist_by_chatid(chat_id)
        
    if not pid_list:
        update.message.reply_text(text='You didn\'t register any PID yet. Please register your PID first.')
        return CHOICE
    
    for pid in pid_list:
        info_from_db.del_user_pid_info(int(pid))
    update.message.reply_text(text="Delete all success!", reply_markup=markup)
    
    return CHOICE

def search(update: Update, context: CallbackContext) -> int:
    
    chat_id = update.message.from_user.id

    pid_list = get_pidlist_by_chatid(chat_id)
        
    if not pid_list:
        update.message.reply_text(text='You didn\'t register any PID yet. Please register your PID first.')
        return CHOICE
    
    reply_text = f'Please select .'
    keyboard = []
    keyboard.append(["Total Balance", "Worker Status"])
    keyboard.append(["Set Notify","Pool Info"])
    keyboard.append(["Back🔙","Support🆘"])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(reply_text,reply_markup=reply_markup)
    return TYPING_SEARCHING

def total_balance(update: Update, context: CallbackContext) -> int:
    reply_text = ''
    chat_id = update.message.from_user.id

    pid_list = get_pidlist_by_chatid(chat_id)
    real_account_list = list()
    
    curr_price = info_from_subscan.get_current_price()
    for pid in pid_list:
        owner_account = info_from_db.get_owner_address_by_pid(pid)
        logging.info(f"get_total_balance:owner_account:{owner_account}")
        if not owner_account in real_account_list:
            real_account_list.append(owner_account)
    grand_total = 0        
    for owner_account in real_account_list:
        json_result = info_from_subscan.get_account_balance(owner_account)
        total_balance = json_result['data']['account']['balance']
        balance_lock = json_result['data']['account']['balance_lock']
        reserved = float(json_result['data']['account']['reserved'])/10**12
        free_balance = float(total_balance) - float(balance_lock) -  float(reserved)
        total_amount = float(total_balance) * float(curr_price)
        grand_total += total_amount
        total_balance = '{:.2f}'.format(float(total_balance))
        balance_lock = '{:.2f}'.format(float(balance_lock))
        reserved = '{:.2f}'.format(float(reserved))
        free_balance = '{:.2f}'.format(float(free_balance))
        total_amount = '{:.2f}'.format(float(total_amount))
        
        reply_text += f'🧰 {short_addr2(owner_account)} \n'
        reply_text += f'---------\n'
        reply_text += f' 🛎 Total: {total_balance} PHA\n'
        reply_text += f' 🔒 Locked: {balance_lock} PHA\n'
        reply_text += f' 🔒 Reserved: {reserved} PHA\n'
        reply_text += f' 💰 Free: {free_balance} PHA\n'
        reply_text += f' 🚀 Price: ${curr_price} \n'
        reply_text += f'--\n'
        reply_text += f' 💵 Amount: ${total_amount} \n'
        reply_text += f'---------\n\n'
        
    grand_total = '{:.3f}'.format(float(grand_total))
    reply_text += f' 💸 Total Amount: ${grand_total}\n'
    update.message.reply_text(reply_text, reply_markup=get_ref_url_inlinebutton())    
    return TYPING_SEARCHING

def worker_status(update: Update, context: CallbackContext) -> int:
    reply_text = ''
    chat_id = update.message.from_user.id

    pid_list = get_pidlist_by_chatid(chat_id)
    for pid in pid_list:
        miner_list = info_from_db.get_worker_pubkey_by_pid(pid)
        reply_text += f"\n🌀 PID : {pid}\n"
        reply_text += f" -- \n"
        emoji = '⚙️'
        for miner in miner_list:
            worker_pubkey = miner[0]
            result = info_from_db.get_worker_status(worker_pubkey)
            
            if result:
                status = result.get('state')
                if status == 'MiningIdle':
                    status = 'Mining '
                    emoji = '🟢'
                elif status == 'MiningUnresponsive':
                    status = "Unresponsive "
                    emoji = '🔴'
                elif status == "MiningCoolingDown":
                    status = "CoolingDown "
                    emoji = '🔵'
                p_instant = result.get('p_instant')
                mined = float(result.get('total_reward')) / 10**12
                mined = '{:.3f}'.format(float(mined))
                logging.info(f"worker_status::{status}:{p_instant}:{mined}")
                reply_text += f" 🔐 {short_addr2(worker_pubkey)}\n"
                reply_text += f" {emoji} Status : {status}\n"
                reply_text += f" 🌡️ P_inst : {p_instant}\n"
                reply_text += f" ⚒️ Mined : {mined} PHA\n\n"
            else :
                reply_text = ' 🕐 Miner information is not updated yet. Please try again 5 mins later.\n\n'
            
    update.message.reply_text(reply_text, reply_markup=get_ref_url_inlinebutton())
    return TYPING_SEARCHING        

def pool_info(update: Update, context: CallbackContext) -> int:
    reply_text = ''
    chat_id = update.message.from_user.id

    pid_list = get_pidlist_by_chatid(chat_id)
    total_own_rewards = 0
    for pid in pid_list:
        result = info_from_db.get_pool_info(pid)
        owner_address = result['owner_address']
        commission = result['commission']
        owner_reward = result['owner_reward']
        cap = result['cap']
        total_stake = result['total_stake']
        free_stake = result['free_stake']
        releasing_stake = result['releasing_stake']
        
        total_own_rewards += owner_reward
        
        commission = '{:.0f}'.format(float(commission)/10**4)
        owner_reward = '{:.2f}'.format(float(owner_reward/10**12))
        if cap == -1:
            cap = '∞'
        else:
            cap = '{:.2f}'.format(float(cap/10**12))
        total_stake = '{:.2f}'.format(float(total_stake/10**12))
        free_stake = '{:.2f}'.format(float(free_stake/10**12))
        releasing_stake = '{:.2f}'.format(float(releasing_stake/10**12))
        
        reply_text += f"🌀 PID : {pid}\n"
        reply_text += f" -- \n"
        reply_text += f" 🧰 {short_addr2(owner_address)}\n"
        reply_text += f" ⚖️ Commission: {commission}%\n"
        reply_text += f" 💎 Own rewards: {owner_reward} PHA \n"
        reply_text += f" 🧢 Cap : {cap} PHA \n"
        reply_text += f" 🍥 Delegated: {total_stake} PHA \n"
        reply_text += f" 💰 Free Delegation: {free_stake} PHA \n"
        reply_text += f" ⏱️ Releasing Stake: {releasing_stake} PHA \n\n"
        
    reply_text += f" -----\n"
    total_own_rewards = '{:.3f}'.format(float(total_own_rewards/10**12))
    reply_text += f" 💵 Claimable Rewards: {total_own_rewards} PHA"
    update.message.reply_text(reply_text, reply_markup=get_ref_url_inlinebutton())
    return TYPING_SEARCHING   

def set_notify(update: Update, context: CallbackContext) -> int:
    inline_keyboard = []
    chat_id = update.message.from_user.id

    pid_list = get_pidlist_by_chatid(chat_id)
    for pid in pid_list:
        notify_bool = info_from_db.get_user_notify_info(chat_id, pid)
        logging.info(f'set_noti_on::notify_bool:{bool(notify_bool)}:chat_id:{chat_id}:{pid}')
 
        if notify_bool:
            keyboard_text = f'\t🟢{pid}'
            keyboard = [InlineKeyboardButton(keyboard_text, callback_data=f'Of_{pid}'),]
        else:
            keyboard_text = f'\t🔴{pid}'
            keyboard = [InlineKeyboardButton(keyboard_text, callback_data=f'On_{pid}'),]
        
        inline_keyboard.append(keyboard)
        
    inline_keyboard.append(
            [
                InlineKeyboardButton("All On", callback_data='On_All'),
                InlineKeyboardButton("All Off", callback_data='Of_All'),
            ])
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    
    update.message.reply_text(
        text="Please select address which is notification to set.",
        reply_markup=reply_markup
    )
    return NOTIFYING

def set_register_notify(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    
    chat_id = query.from_user.id
    pid = query.data[3:]
    on_off = query.data[0:2]
    logging.info(f'set_noti_on::chat_id:{chat_id}:{on_off}:{pid}')
    reply_text = '👀 Registered PID for Notification :\n--\n'
    
    if on_off.startswith("On") :
        if pid.startswith("All"):
            pid_list = get_pidlist_by_chatid(chat_id)
            for pid_key in pid_list:
                info_from_db.set_user_notify_info(chat_id, pid_key, True)
                reply_text += f"🌀 PID : {pid_key}\n"
        else :
            info_from_db.set_user_notify_info(chat_id, pid, True)
            reply_text += f"🌀 PID : {pid}\n"

        reply_text += "---------\n"
        reply_text += f"💬 Bot will notify you when..\n"
        reply_text += f"\t👉 Miner status is changed to \"Not Mining\".\n"
        reply_text += f"\t👉 P Instant value is changed to \"0\".\n"
        reply_text += "---------\n"
        
    elif on_off.startswith("Of"):
        if pid.startswith("All"):
            pid_list = get_pidlist_by_chatid(chat_id)
            for pid_key in pid_list:
                info_from_db.set_user_notify_info(chat_id, pid_key, False)
                reply_text += f"🌀 PID : {pid_key}\n"
        else:
            info_from_db.set_user_notify_info(chat_id, pid, False)
            reply_text += f"🌀 PID : {pid}\n"
    
        reply_text += "---------\n"
        reply_text += f"💬 ❗Bot will NOT Notify❗ \n"
        reply_text += "---------\n"   
    
    query.edit_message_text(
        text=reply_text
    )
    
    return TYPING_SEARCHING

def send_status_notification():
    msg_text = "🔔 Status Change Alert 🔔\n"
    msg_text += "--\n"
    chat_id_list = info_from_db.get_all_registered_chat_id()
    for chat_id in chat_id_list:
        pid_list = info_from_db.get_noti_pid_from_chat_id(chat_id)
        for pid in pid_list:
            pid = pid[0]
            #msg_text += f"{pid}\n"
            miner_list = info_from_db.get_worker_pubkey_by_pid(pid)
            for miner in miner_list:
                miner = miner[0]
                miner_status_list = info_from_db.get_noti_worker_status(miner)
                for miner_status in miner_status_list:
                    status = miner_status[0]
                    p_instant = miner_status[1]
                    
                    msg_text += f" 🌀 PID: {pid}\n"
                    msg_text += f" ⛏️ Worker: {short_addr(miner)}\n"
                    msg_text += f" 🌡️ P Instant: {p_instant}\n"
                    msg_text += f" ⚙️ Current Status: {status}\n"
                    
        msg_text += "------\n"
        
        d = datetime.datetime.now()
        interval = d.minute % 10
        logging.info(f"send_status_notification:{chat_id}:{pid}:time:{d}:mins:{d.minute}:{interval}")
        if not interval == 0:                      
            BOT.send_message(chat_id=chat_id,text=msg_text)


def main() -> None:
    """Run the bot."""        
    # Create the Updater and pass it your bot's token.
    BOT_CONV_FILE = common.PHA_BOT_CONV_FILE
    TELEGRAM_API_KEY = common.PHA_TELEGRAM_API_KEY
    persistence = PicklePersistence(filename=BOT_CONV_FILE)
    updater = Updater(TELEGRAM_API_KEY, persistence=persistence)
    
    # Check updataed data and send notification using Thread.
    global BOT
    BOT = updater.bot
    
    notify_thread = threading.Thread(target=send_status_notification)
    notify_thread.start()
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOICE: [
                MessageHandler(Filters.regex('start'), start),
                MessageHandler(Filters.regex('^Back🔙$'), start),
                MessageHandler(Filters.regex('^Register🔖$'), register_address),
                MessageHandler(Filters.regex('^Search🔎$'), search),
                MessageHandler(Filters.regex('^Delete⛔$'), delete),
                
            ],
            REGISTER: [
                MessageHandler(Filters.regex('start'), start),
                MessageHandler(Filters.regex('^Back🔙$'), start),
            ],
            TYPING_REPLY: [
                MessageHandler(Filters.regex('start'), start),
                MessageHandler(Filters.regex('^Back🔙$'),start),
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Support🆘$')),
                    received_information,
                ),
                
            ],
            DELETING: [ 
                MessageHandler(Filters.regex('start'), start),
                MessageHandler(Filters.regex('^Back🔙$'), start),
                MessageHandler(Filters.regex('^PID'),delete_address),
                MessageHandler(Filters.regex('^Delete All⛔$'),delete_all),

            ],
            TYPING_SEARCHING: [
                MessageHandler(Filters.regex('start'), start),
                MessageHandler(Filters.regex('^Total Balance$'),total_balance),
                MessageHandler(Filters.regex('^Worker Status$'),worker_status),
                MessageHandler(Filters.regex('^Pool Info$'),pool_info),
                #MessageHandler(Filters.regex('^Collator Status$'),collator_status),
                MessageHandler(Filters.regex('^Set Notify$'),set_notify),
                MessageHandler(Filters.regex('^Back🔙$'),start),
            ],
            NOTIFYING: [
                CallbackQueryHandler(set_register_notify, pattern='^On_|^Of_'),
                MessageHandler(Filters.regex('^Back🔙$'),start),
                MessageHandler(Filters.regex('^Set Notify$'),set_notify),
                MessageHandler(Filters.regex('start'), start),
                MessageHandler(Filters.regex('^Total Balance$'),total_balance),
                MessageHandler(Filters.regex('^Worker Status$'),worker_status),
                MessageHandler(Filters.regex('^Pool Info$'),pool_info),
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^Support🆘$'), support)],
        name="my_conversation",
        persistent=True,
    )
    
    dispatcher.add_handler(conv_handler)

    #show_data_handler = CommandHandler('show_data', show_data)
    #dispatcher.add_handler(show_data_handler)
    dispatcher.add_error_handler(error_handler)
    
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':

        main()

