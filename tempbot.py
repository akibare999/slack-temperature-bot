import os
import re
import time
from slackclient import SlackClient

# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

# regexp for temperatures
p = re.compile('.*?(-?[\d]*\.?[\d]*) ?([CFcf])\\b')

# instantiate Slack and Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def get_temperature_message(temp, scale):
    '''
        Receives a temperature and scale (C or F).
        Converts to the other one, and makes a message.
    '''
    try:
        temp = float(temp)
    except ValueError:
        return ''
    if scale in "cC":
        temp = (1.8 * temp) + 32
        return ("That would be %.1f in F" % temp)
    elif scale in "fF":
        temp = (temp - 32) / 1.8
        return ("That would be %.1f in C" % temp)
    else:
        return ''


def parse_slack_output(slack_rtm_output):
    '''
        The Slack Real Time Messaging API is an events firehose.
        This parsing function returns None unless a message is 
        directed at the Bot, based on its ID.
    '''
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and p.match(output['text']):
                (temp, scale) = p.match(output['text']).groups()
                print ("FOUND A MESSAGE TO PROCESS: %s %s" % (temp, scale))
                message = get_temperature_message(temp, scale)
                print ("GOT MESSAGE BACK")
                if message:
                    slack_client.api_call("chat.postMessage", 
                                      channel=output['channel'],
                                      text=message, as_user=True)
            try:
                print(output)
            except Exception as e:
                print("BURP!")
#{u'text': u"wow it's 49F out right now", u'ts': u'1485111015.030469', u'user': u'U08LRH2MC', u'team': u'T08LQ2PJA', u'type': u'message', u'channel': u'C08LQA0SH'}

#           if output and 'text' in output and AT_BOT in output['text']:
#               # return text after the @mention, whitespace removed
#               return output['text'].split(AT_BOT)[1].strip().lower(), \
#                      output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print ("Starterbot connected and running!")
        while True:
            try:
                command, channel = parse_slack_output(slack_client.rtm_read())
            except ConnectionResetError as e:
                if slack_client.rtm_connect():
                    print ("Starterbot RE-connected and running!")
                    continue
                
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

# {u'text': u'<@U3URB1YN9> hey dude', u'ts': u'1485108617.030452', u'user': u'U08LRH2MC', u'team': u'T08LQ2PJA', u'type': u'message', u'channel': u'C08LQA0SH'}
