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


def update(channel_id, message_ts, text, new_text):
    response = client.chat_update(
        channel=channel_id,
        ts=message_ts,
        text=text,
        blocks=new_text,
    )


async def get_message(payload, a):
    channel_id = payload["channel"]["id"]
    user_id = payload["user"]["id"]
    user_name = payload["user"]["name"]
    message_ts = payload["container"]["message_ts"]
    text = payload["message"]["text"]
    comment = f"<@{user_id}>, "
    data = payload["message"]["blocks"]

    if a == 1:
        status = "*참석*\n "
        op_status = "*불참*\n "
        op_ps_status = "*불참인원*"
        ps_status = "*참석인원*"
    elif a == 0:
        status = "*불참*\n "
        op_status = "*참석*\n "
        ps_status = "*불참인원*"
        op_ps_status = "*참석인원*"
    insert = {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": "*참석인원*\n 0 *(명)*"},
            {"type": "mrkdwn", "text": "*불참인원*\n 0 *(명)*"},
        ],
    }
    # print(data)
    if "divider" in data[-2]["type"]:
        data.insert(-1, insert)
    for block in data:
        try:
            if "section" in block["type"]:
                for a in block["fields"]:
                    if op_status in a["text"]:
                        a["text"] = a["text"].replace(comment, "")
                        for person in data[-2]["fields"]:
                            if person["text"].find(op_ps_status) == 0:
                                person["text"] = person["text"].split()
                                person["text"][0] += "\n"
                                if int(person["text"][1]) > 0:
                                    person["text"][1] = str(a["text"].count("@"))

                                person["text"] = " ".join(person["text"])
                    if status in a["text"]:
                        if comment in a["text"]:
                            pass
                        else:
                            # pass
                            a["text"] += comment

                            for person in data[-2]["fields"]:
                                if person["text"].find(ps_status) == 0:
                                    person["text"] = person["text"].split()
                                    person["text"][0] += "\n"
                                    person["text"][1] = str(a["text"].count("@"))
                                    person["text"] = " ".join(person["text"])

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

    update(channel_id, message_ts, text, data)


@app.action("attend")
def handle_attent_edit_button_click(ack, body, logger):
    ack()
    logger.info(body)
    asyncio.run(get_message(body, 1))


@app.action("nonattend")
def handle_nonattent_edit_button_click(ack, body, logger):
    ack()
    logger.info(body)
    asyncio.run(get_message(body, 0))
    # asyncio.run(nonattend_edit_message(body))


if __name__ == "__main__":
    # Start the bot
    handler = SocketModeHandler(app_token=app_token, app=app)
    handler.start()
