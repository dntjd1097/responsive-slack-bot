import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import asyncio
from config import *

#app_token = os.environ["SLACK_APP_TOKEN"]
#bot_token = os.environ["SLACK_BOT_TOKEN"]

# Initialize the Slack API client and the bot app
client = WebClient(token=bot_token)
app = App(token=bot_token)
attachments = [
    {
        "fallback": "Upgrade your Slack client to use messages like these.",
        "color": "#3AA3E3",
        "attachment_type": "default",
        "callback_id": "attend",
        "actions": [
            {"name": "attend_button", "text": "참석", "type": "button", "value": "attend"}
        ],
    },
    {
        "fallback": "Upgrade your Slack client to use messages like these.",
        "color": "#990F02",
        "attachment_type": "default",
        "callback_id": "nonattend",
        "actions": [
            {
                "name": "nonattend_button",
                "text": "불참",
                "type": "button",
                "value": "nonattend",
            }
        ],
    },
]
# Define the message to send
message = {"channel": "#bot-lab", "text": "버튼눌러바 ㅋ \n참석: \n불참석:", "attachments": attachments}

# Send the message to the channel

def get_data(payload):
    channel_id = payload["channel"]["id"]
    
    user_id = payload["user"]["id"]
    user_name = payload["user"]["name"]
    message_ts = payload["message_ts"]
    message_text = payload["original_message"]["text"]
    comment = f"<@{user_id}>"
    start = message_text.find("참석:")
    insert = message_text.find(comment)
    end = message_text.find("불참석:")
    index = message_text.find("참석:") + 3
    find_index = message_text.find(comment) + 3
    end_index = message_text.find("불참석:") + 4
    return channel_id,user_id,user_name,message_ts,message_text,comment,start,insert,end,index,find_index,end_index

def update(channel_id,message_ts,new_text):
    response = client.chat_update(
                channel=channel_id,
                ts=message_ts,
                text=new_text,
                attachments=attachments,
            )

async def attend_edit_message(payload):
    
    channel_id,user_id,user_name,message_ts,message_text,comment,start,insert,end,index,find_index,end_index=get_data(payload)
    
    new_text = message_text[:index] + comment + message_text[index:]
    
    try:
        if start < insert < end:
            return
        elif (end<insert) :
            message_text=message_text.replace(comment,"")
            new_text = message_text[:index] + comment + message_text[index:]
            update(channel_id,message_ts,new_text)
        elif insert < 0:
            update(channel_id,message_ts,new_text)
    
    except AttributeError as e:
        print(f"Error updating message: {e}")
    except SlackApiError as e:
        print(f"Error updating message: {e}")
    print(new_text)


async def nonattend_edit_message(payload):
    channel_id,user_id,user_name,message_ts,message_text,comment,start,insert,end,index,find_index,end_index=get_data(payload)
    new_text = message_text[:end_index] + comment + message_text[end_index:]
    
    try:
        if end < insert:
            return
        elif end>insert>-1:
            message_text=message_text.replace(comment,"")
            new_text = message_text[:end_index] + comment + message_text[end_index:]
            update(channel_id,message_ts,new_text)
        elif insert < 0:
            update(channel_id,message_ts,new_text)

    except AttributeError as e:
        print(f"Error updating message: {e}")
    except SlackApiError as e:
        print(f"Error updating message: {e}")


# Add the listener for the button click

@app.action("attend")
def handle_attent_edit_button_click(ack, body, logger):
    ack()
    logger.info(body)
    asyncio.run(attend_edit_message(body))

@app.action("nonattend")
def handle_nonattent_edit_button_click(ack, body, logger):
    ack()
    logger.info(body)
    asyncio.run(nonattend_edit_message(body))
    

#response = client.chat_postMessage(**message)
if __name__ == "__main__":
    # Start the bot
    handler = SocketModeHandler(app_token=app_token, app=app)
    handler.start()
