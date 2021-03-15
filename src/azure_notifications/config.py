from enum import Enum

SMTP_SERVER_PORT = 8025


class Event(Enum):
    PULL_REQUEST = "ms.vss-code.git-pullrequest-event"
    BUILD_COMPLETED = "ms.vss-build.build-completed-event"
    PR_COMMENT = "ms.vss-code.git-pullrequest-comment-event"
    WORK_ITEM_CHANGED = "ms.vss-work.workitem-changed-event"


event_triggers = {
    Event.BUILD_COMPLETED: ["Successfully Completed", "Failed"],
    Event.PR_COMMENT: ["CommentNotification"],
    Event.PULL_REQUEST: [
        "StatusUpdateNotification",
        "ReviewerVoteNotification",
        "PushNotification",
    ],
    Event.WORK_ITEM_CHANGED: ["FieldChanged,AssignedToChanged"],
}
