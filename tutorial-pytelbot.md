# Introduction

About a month ago I was asked if I could make a Telegram bot for a friend to help him automate a few functions in his group. I was excited about the project because I think bot creation is a really fun area of programming, and I had been previously pretty excited by how easy the Telegram API is to work with. When I program for my personal projects like this, I prefer to use Python; I find it easy to use, easy to understand, and generally more than enough to suit my needs. There are even helpful libraries like telepot (which I will be using in this tutorial) that automate a lot of the more complicated functions. Unfortunately, when I wanted to make my Telegram bot a little more useful by running it as a webhook instead of a standalone loop, things got tougher and tutorials got less useful.

As it turns out, making a webhook bot in Python is way easier than I was giving it credit for. After searching through probably 50 pages I've gathered the most helpful, least outdated, and most complete pages I found, and I'm going to try my hand at writing my own tutorial on making a Python Telegram bot. This tutorial will be using telepot and Flask to create a bot with and without using a webhook, using a self-signed certificate for the webhook portion.

## What is a Bot? (something something electric sheep)

A 'bot' is a program or process operating as if it were a user. There are a few use-cases for bots, but the one we'll be looking at today is as a Telegram user. Telegram has an API to make automated users a very simple process. They appear and behave almost exactly as if they were users, and can have a lot of the same powers and priviledges in Telegram groups, channels, and chats as users have, while also having a very dynamic programmatic backend that a developer can do whatever they want with.

## The Telegram API

Telegram provides a very useful set of bot features and functions, as well as a pretty in-depth guide on how to use them on their website. For this tutorial we will only be using a few bot functions. For more information on these topics see the links at the end of the tutorial.

## Assumptions

This tutorial assumes you have already created a bot, and that you have access to the bot's token. It also assumes you're using python 3, and have installed telepot and Flask.

## Why Webhooks? (Seriously, what a hassle)

Telegram provides two ways to get bot updates, one is by calling getUpdates and the other is a webhook. Calling getUpdates sends a request to the Telegram servers, fetching the most recent information from your bot and giving it to you for processing. While this is helpful, it isn't what Telegram prefers for bots, and eventually a getUpdates loop will shut off on its own. A webhook on the other hand is essentially a bot as a server, and when it's set up Telegram is given the server address to automatically push all bot updates to via HTTPS, which can then processed by the bot code. It's a frustrating process when you don't know what's going on, but to put it simply Telegram wants to automatically send information to you instead of getting a bunch of requests from you all the time. 

## Flask and Telepot

Flask is a very useful and very easy server library written in Python, which we will be using to host our bot. Flask is intended for development purposes and not for production servers.
Telepot is a library written to make interfacing with the Telegram bot API simple, and despite some personal complications with setting up a webhook, I consider it the most useful tool for making a Telegram bot out there.

## It's my Fault

Even though I have access to my friend's server, I do not have access to his SSL license for anything I run on the site, which definitely complicated the process of setting up the SSL-necessary webhook. If you already have a server with SSL set up, great! However, this tutorial will be specifically covering setting up a webhook with self-signed certificates rather than a trusted SSL certificate setup.

# The Code (no webhook)

Both the Flask and telepot documentations are very well constructed, and give great quick tutorials on how to set them up. In this tutorial I will be very brief with both, as I reccommend you read the original documentations. The first thing we are going to do is create a file, I'll be calling it bot-nowebhook.py but you can call yours whatever you want. The first thing we're going to do is import everything we're going to need.
```python
import sys # required to accept user arguments
import time # required to pace the main program loop
import telepot # the bot library we will be using
from telepot.loop import MessageLoop # message loop from telepot
from pprint import pprint # optional, for blanket message handling
```

After the imports, we will be setting up the message handling function. Telegram messages will be sent to the bot as a python dictionary, with a lot of data that can be used and handled in a variety of ways. For now, though, we're just going to print the data using pprint. For more detailed information on message handling, I would recommend referencing the telepot documentation.
```python
# messages the bot receives will be passed to this function
def handle(msg):
	pprint(msg)
```

Once our message handling is set up we'll take the first user argument as the bot's token, using telepot to then set up the bot.
```python
# takes the first argument and uses it as the bot key
TOKEN = sys.argv[1]
# creates the bot using the given token
bot = telepot.Bot(TOKEN)
```

Once the bot is set up, we'll run the MessageLoop function from telepot. The arguments for the function will be our bot and our message handling function. This function will not work if there is an active webhook running, and will stop working if a webhook is activated for any reason, even by Telegram. My bot shut down every few days when a webhook automatically turned itself back on. You can call the deleteWebhook command to temporarily solve this issue, though eventually it's recommended that you set up a webhook instead of using this loop.
```python
# optional, deletes any existing webhook
bot.deleteWebhook()
# begins the message loop
MessageLoop(bot, handle).run_as_thread()
```

Because we want the program to run indefinitely, we will be adding a loop at the end of the file that will run forever.
```python
# Keep the program running forever
while 1:
	time.sleep(10)
```

And that's it! you can run this from a terminal by typing `python bot-nowebhook.py`_`yourtokenhere`_. When your bot notices any messages sent to it, the message data will be printed to the console in full. This method works well as a way to test bot funtionality before setting up the more intense webhook bot.

# The Code (webhook)

The next bot will be a little more complicated to set up. We'll assume before we begin that you've followed the tutorial [here](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https) in order to set up a self signed certificate wherever you are hosting your bot. Make sure that the common name (CN) of your certificate is the url or public ip of the bot host. This is required by Telegram for their webhook setup. I placed certificate.pem and privkey.pem in a subdirectory called cert. As before, the first thing we'll be doing is importing libraries. This time we will also be importing Flask so we can run the bot as a server.
```python
import sys # required to accept user arguments
import telepot # the bot library we will be using
from telepot.loop import OrderedWebhook # the telepot webhook
from pprint import pprint # optional, for blanket message handling
from flask import Flask, request # server with request processing
```
Once we have our libraries are imported, we're going to set up out message handling function. This can be anything, but as above we will simply be printing incoming message data to the console.
```python
# messages the bot receives will be passed to this function
def handle(msg):
	pprint(msg)
```
Unlike the above code, this bot will accept more arguments when it's run. The first argument will still be the token of the Telegram bot, but there are now two more arguments. The second argument will be the port the server is going to run on, which telegram requires to be port 443, 80, 88, or 8443. The third argument will be the url which Telegram will be sending data to.
```python
# takes the first argument and uses it as the bot key
TOKEN = sys.argv[1]
# uses the second argument as the port the server will run on
# note: Telegram requires bots be run on port 443, 80, 88, or 8443
PORT = int(sys.argv[2])
# the third argument is the url that Telegram will send data to
URL = sys.argv[3]
```
Next we'll be setting up the Flask server and the Telegram bot webhook. I recommend reading up on both Flask and telepot to understand this section better.
```python
# set up basic flask server
app = Flask(__name__)
# set up telegram bot using given token
bot = telepot.Bot(TOKEN)
# delete any existing webhook
bot.deleteWebhook()
# creates webhook, using handle function to handle chat messages
webhook = OrderedWebhook(bot, {'chat': handle,})
```
Once we have the Flask server set up, we will set up the /webhook route to receive GET and POST requests from Telegram automatically, feeding them to the bot's webhook
```python
# uses Flask to accept Telegram GET and POST requests at /webhook
@app.route("/webhook", methods=['GET', 'POST'])
def get_data():
	webhook.feed(request.data)
	return 'OK'
```
Once all that is set up all that's left to do is start both the webhook process and the server itself, both of which we'll be using our certification we created to do. We will be feeding the public key to the bot as an argument, which Telegram requires to interact with webhooks running on self-signed servers. We will also be using the complete key pair to start the Flask server with ssl.
```python
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
```
And that's all! Once it's started with the command `python bot-webhook.py`_`token port url`_ the flask server and webhook will begin running, and newly received messages from the bot will be printed to the console. Unlike the previous method, this webhook bot should run indefinitely with no interruptions from Telegram.

# References

[Flask Documentation](https://flask.palletsprojects.com/en/1.1.x/)

[Self-Signed Certificates](https://www.devdungeon.com/content/creating-self-signed-ssl-certificates-openssl)

[SSL using Flask](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https)

[Telegram Webhooks](https://core.telegram.org/bots/webhooks)

[Telepot Documentation](https://telepot.readthedocs.io/en/latest/reference.html)

[Webhooks with Telepot](https://github.com/nickoala/telepot/tree/master/examples/webhook)