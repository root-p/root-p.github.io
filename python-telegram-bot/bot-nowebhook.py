import sys # required to accept user arguments
import time # required to pace the main program loop
import telepot # the bot library we will be using
from telepot.loop import MessageLoop # message loop from telepot
from pprint import pprint # optional, for blanket message handling

# messages the bot receives will be passed to this function
def handle(msg):
	pprint(msg)

# takes the first argument and uses it as the bot key
TOKEN = sys.argv[1]

# creates the bot using the given token
bot = telepot.Bot(TOKEN)

# begins the message loop
MessageLoop(bot, handle).run_as_thread()

# Keep the program running forever
while 1:
	time.sleep(10)
