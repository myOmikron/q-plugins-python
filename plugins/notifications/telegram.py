import argparse

__help__ = "Send notifications via telegram to a known user."
__requirements__ = ["requests"]


def send_message(config, utils, debug):
    import requests

    uri = f"https://api.telegram.org/bot{config.bot_token}/sendMessage"
    data_dict = {
        "chat_id": config.user_id,
        "text": config.message,
    }
    requests.post(uri, data=data_dict)


def execute(utils, debug=False):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--user-id",
        action="store",
        dest="user_id",
        required=True,
        help="Telegram ID of the specified user."
    )
    parser.add_argument(
        "--bot-token",
        action="store",
        dest="bot_token",
        required=True,
        help="Token of the telegram bot."
    )
    parser.add_argument(
        "--message",
        action="store",
        dest="message",
        required=True,
        help="Message to send."
    )
    config = parser.parse_known_args()[0]
    send_message(config, utils, debug)
