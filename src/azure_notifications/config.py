import os
from enum import Enum

import pandas as pd

SERVER_PORT = int(os.getenv("PORT") or 3000)
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")


class Event(Enum):
    PULL_REQUEST = "ms.vss-code.git-pullrequest-event"
    BUILD_COMPLETED = "ms.vss-build.build-completed-event"
    PR_COMMENT = "ms.vss-code.git-pullrequest-comment-event"
    WORK_ITEM_CHANGED = "ms.vss-work.workitem-changed-event"


# This dictionary is used only for lookup
event_triggers = {
    Event.BUILD_COMPLETED: ["Successfully Completed", "Failed"],
    Event.PR_COMMENT: ["CommentNotification"],
    Event.PULL_REQUEST: [
        "StatusUpdateNotification",
        "ReviewerVoteNotification",
        "ReviewersUpdateNotification",
        "PushNotification",
    ],
    Event.WORK_ITEM_CHANGED: ["FieldChanged,AssignedToChanged"],
}

# slack_user_ids = pd.read_csv(os.getenv("SLACK_USER_IDS"), index_col="tfs_name")[
#     "id"
# ].to_dict()
# slack_user_ids = {
#     key: value for key, value in slack_user_ids.items() if not pd.isna(key)
# }
