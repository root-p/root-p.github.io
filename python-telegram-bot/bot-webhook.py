import sys # required to accept user arguments
import telepot # the bot library we will be using
from telepot.loop import OrderedWebhook # the telepot webhook
from pprint import pprint # optional, for blanket message handling
from flask import Flask, request # server with request processing

# messages the bot receives will be passed to this function
def handle(msg):
	pprint(msg)

# takes the first argument and uses it as the bot key
TOKEN = sys.argv[1]
# uses the second argument as the port the server will run on
# note: Telegram requires bots be run on port 443, 80, 88, or 8443
PORT = int(sys.argv[2])
# the third argument is the url that Telegram will send data to
URL = sys.argv[3]

# set up basic flask server
app = Flask(__name__)
# set up telegram bot using given token
bot = telepot.Bot(TOKEN)
# delete any existing webhook
bot.deleteWebhook()
# creates webhook, using handle function to handle chat messages
webhook = OrderedWebhook(bot, {'chat': handle,})

# uses Flask to accept Telegram GET and POST requests at /webhook
@app.route("/webhook", methods=['GET', 'POST'])
def get_data():
	webhook.feed(request.data)
	return 'OK'

if __name__ == '__main__':
	# initializes webhook, passing the cert public key file
	bot.setWebhook(URL, certificate=open('./cert/certificate.pem'))
	# runs the webhook continuously in the background
	webhook.run_as_thread()
	# starts the server, using the self signed cert for authentication
	app.run(
		host='0.0.0.0', 
		port=PORT, 
		ssl_context=('./cert/certificate.pem', './cert/privkey.pem'), 
		debug=True
	)
