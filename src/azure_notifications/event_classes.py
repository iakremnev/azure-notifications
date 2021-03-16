"Notification event classes"
from dataclasses import dataclass
from typing import Optional


@dataclass
class TFSEvent:
    title: str
    event_type: str
    trigger: str
    url: str


@dataclass
class WorkItemEvent(TFSEvent):
    changed_by: str
    assigned_to: str
    # new_status:


@dataclass
class BuildCompletedEvent(TFSEvent):
    requested_for: str


@dataclass
class PullRequestEvent(TFSEvent):
    initiator: str
    pr_author: str
    vote: Optional[str] = None
    reviewer: Optional[str] = None
    commits: Optional[int] = None
    status: Optional[str] = None


@dataclass
class PullRequestCommentEvent(TFSEvent):
    # pr_author: str
    commenter: str
    text: str
