from multiprocessing import pool
from substrateinterface import SubstrateInterface
import logging
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
        for key in context.user_data.keys():
            reply_text += f'\t🧰 {key}\n'
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
    for owner_account in real_account_list:
        json_result = info_from_subscan.get_account_balance(owner_account)
        total_balance = json_result['data']['account']['balance']
        balance_lock = json_result['data']['account']['balance_lock']
        reserved = float(json_result['data']['account']['reserved'])/10**12
        free_balance = float(total_balance) - float(balance_lock) -  float(reserved)
        total_amount = float(total_balance) * float(curr_price)
        
        total_balance = '{:.3f}'.format(float(total_balance))
        balance_lock = '{:.3f}'.format(float(balance_lock))
        reserved = '{:.3f}'.format(float(reserved))
        free_balance = '{:.3f}'.format(float(free_balance))
        total_amount = '{:.3f}'.format(float(total_amount))
        
        reply_text += f'🧰 {short_addr2(owner_account)} \n'
        reply_text += f'---------\n'
        reply_text += f' 🛎 Total: {total_balance} \n'
        reply_text += f' 🔒 Locked: {balance_lock} \n'
        reply_text += f' 🔒 Reserved: {reserved} \n'
        reply_text += f' 💰 Free: {free_balance} \n'
        reply_text += f' 🚀 Price: ${curr_price} \n'
        reply_text += f'--\n'
        reply_text += f' 💵 Total_amount: ${total_amount} \n'
        reply_text += f'---------\n'
        
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
        for miner in miner_list:
            worker_pubkey = miner[0]
            result = info_from_db.get_worker_status(worker_pubkey)
            
            if result:
                status = result.get('state')
                if status == 'MiningIdle':
                    status = 'Mining'
                p_instant = result.get('p_instant')
                mined = float(result.get('total_reward')) / 10**12
                mined = '{:.3f}'.format(float(mined))
                logging.info(f"worker_status::{status}:{p_instant}:{mined}")
                reply_text += f" 🔐 {short_addr2(worker_pubkey)}\n"
                reply_text += f" ⚙️ Status : {status}\n"
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
    
    for pid in pid_list:
        result = info_from_db.get_pool_info(pid)
        owner_address = result['owner_address']
        commission = result['commission']
        owner_reward = result['owner_reward']
        cap = result['cap']
        total_stake = result['total_stake']
        free_stake = result['free_stake']
        releasing_stake = result['releasing_stake']
        
        commission = '{:.0f}'.format(float(commission)/10**4)
        owner_reward = '{:.3f}'.format(float(owner_reward/10**12))
        if cap == -1:
            cap = '∞'
        else:
            cap = '{:.3f}'.format(float(cap/10**12))
        total_stake = '{:.3f}'.format(float(total_stake/10**12))
        free_stake = '{:.3f}'.format(float(free_stake/10**12))
        releasing_stake = '{:.3f}'.format(float(releasing_stake/10**12))
        
        reply_text += f"🌀 PID : {pid}\n"
        reply_text += f" -- \n"
        reply_text += f" 🧰 Owner: {short_addr2(owner_address)}\n"
        reply_text += f" ⚖️ Commission: {commission}%\n"
        reply_text += f" 💎 Own rewards: {owner_reward} \n"
        reply_text += f" 🧢 Cap : {cap} \n"
        reply_text += f" 🍥 Delegated: {total_stake} \n"
        reply_text += f" 💰 Free Delegation: {free_stake} \n"
        reply_text += f" ⏱️ Releasing Stake: {releasing_stake} \n\n"
        
    update.message.reply_text(reply_text, reply_markup=get_ref_url_inlinebutton())
    return TYPING_SEARCHING   

def set_notify(update: Update, context: CallbackContext) -> int:
    reply_text = '📣 Notify function will be added soon 📣 \n'
    reply_text += ' 최대한 빨리 추가하겠습니다..쫌만 쉴게요...😴😴😴 \n'
    
    chat_id = update.message.from_user.id
    
    update.message.reply_text(reply_text, reply_markup=get_ref_url_inlinebutton())
    return TYPING_SEARCHING  

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
                #CallbackQueryHandler(set_register_notify, pattern='^On_|^Of_'),
                MessageHandler(Filters.regex('^Back🔙$'),start),
                #MessageHandler(Filters.regex('^Notify⏰$'),set_notify),
                #MessageHandler(Filters.regex('start'), start),
                #MessageHandler(Filters.regex('^Total Balance$'),total_balance),
                #MessageHandler(Filters.regex('^Recent Rewards$'),recent_rewards),
                #MessageHandler(Filters.regex('^Delegation Status$'),delegation_status),
                #MessageHandler(Filters.regex('^Collator Status$'),collator_status),
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^Support🆘$'), support)],
        name="my_conversation",
        persistent=True,
    )
    
    dispatcher.add_handler(conv_handler)

    #show_data_handler = CommandHandler('show_data', show_data)
    #dispatcher.add_handler(show_data_handler)
    #dispatcher.add_error_handler(error_handler)
    
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':

        main()

