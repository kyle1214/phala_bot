#t.me/phala_stat_bot
#5376761158:AAGStIJnf0lP4IrRC0W8DSoDJGnecp13ypI
import psycopg2

def get_connection():
    return psycopg2.connect(host='127.0.0.1', dbname='substake', user='substake', password='substake!', port='5432')

PHA_BOT_CONV_FILE='phalabot'
PHA_TELEGRAM_API_KEY="5376761158:AAGStIJnf0lP4IrRC0W8DSoDJGnecp13ypI" #phala_stat_bot