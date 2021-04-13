import os

import pandas as pd

SERVER_PORT = int(os.getenv("PORT") or 3000)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
BOT_SERVICE_CHANNEL = os.getenv("BOT_SERVICE_CHANNEL")

slack_users = pd.read_csv(os.getenv("SLACK_USER_IDS"), index_col="tfs_name")
slack_users = {name: uid for name, uid in slack_users["id"].to_dict().items() if not pd.isna(name)}
slack_ims = {}
