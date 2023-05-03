import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import asyncio
import html

try:
    from config import *
except ModuleNotFoundError:
    app_token = os.environ["SLACK_APP_TOKEN"]
    bot_token = os.environ["SLACK_BOT_TOKEN"]


# Initialize the Slack API client and the bot app
client = WebClient(token=bot_token)
app = App(token=bot_token)
attachments = [
    {"type": "divider"},
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
message = {
    "channel": "#bot-lab",
    "text": "버튼눌러바 ㅋ \n참석: \n불참석:",
    "attachments": attachments,
}


def update(channel_id, message_ts, text, new_text):
    response = client.chat_update(
        channel=channel_id,
        ts=message_ts,
        text=text,
        blocks=new_text,
        attachments=attachments,
    )


async def get_message(payload, a):
    channel_id = payload["channel"]["id"]

    user_id = payload["user"]["id"]
    user_name = payload["user"]["name"]
    message_ts = payload["message_ts"]
    text = payload["original_message"]["text"]
    comment = f"<@{user_id}>, "
    data = payload["original_message"]["blocks"]

    context_block_index = None
    if a == 1:
        status = "참석:"
        op_status = "불참:"
        op_ps_status = "*불참*"
        ps_status = "*참석*"
    elif a == 0:
        status = "불참:"
        op_status = "참석:"
        ps_status = "*불참*"
        op_ps_status = "*참석*"
    insert = {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": "*참석*\n 0 *(명)*"},
            {"type": "mrkdwn", "text": "*불참*\n 0 *(명)*"},
        ],
    }
    # print(data)
    for block in data:
        try:
            # 참석 클릭 시
            # print(block)

            if "divider" in data[-1]["type"]:
                data.append(insert)

            if op_status in block["elements"][0]["text"]:
                if block["elements"][0]["text"].find(comment) > 0:
                    block["elements"][0]["text"] = block["elements"][0]["text"].replace(
                        comment, ""
                    )
                    for person in data[-1]["fields"]:
                        if person["text"].find(op_ps_status) == 0:
                            person["text"] = person["text"].split()
                            person["text"][0] += "\n"
                            if int(person["text"][1]) > 0:
                                person["text"][1] = str(int(person["text"][1]) - 1)

                            person["text"] = " ".join(person["text"])

            if status in block["elements"][0]["text"]:
                if comment in block["elements"][0]["text"]:
                    pass
                else:
                    # pass
                    block["elements"][0]["text"] += comment
                    for person in data[-1]["fields"]:
                        if person["text"].find(ps_status) == 0:
                            person["text"] = person["text"].split()
                            person["text"][0] += "\n"

                            person["text"][1] = str(int(person["text"][1]) + 1)
                            person["text"] = " ".join(person["text"])
            print(block["elements"][0]["text"])

        except KeyError as e:
            pass

    def unescape(input):
        return html.unescape(input)

    for item in data:
        for key in item.keys():
            if isinstance(item[key], str):
                item[key] = unescape(item[key])
            elif isinstance(item[key], dict):
                for sub_key in item[key].keys():
                    if isinstance(item[key][sub_key], str):
                        item[key][sub_key] = unescape(item[key][sub_key])
    print(user_id)
    update(channel_id, message_ts, text, data)


@app.action("attend")
def handle_attent_edit_button_click(ack, body, logger):
    ack()
    logger.info(body)
    asyncio.run(get_message(body, 1))
    # asyncio.run(attend_edit_message(body))


@app.action("nonattend")
def handle_nonattent_edit_button_click(ack, body, logger):
    ack()
    logger.info(body)
    asyncio.run(get_message(body, 0))
    # asyncio.run(nonattend_edit_message(body))


# response = client.chat_postMessage(**message)
if __name__ == "__main__":
    # Start the bot
    handler = SocketModeHandler(app_token=app_token, app=app)
    handler.start()
