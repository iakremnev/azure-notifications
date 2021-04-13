"Notification event classes"
from dataclasses import dataclass
import re
from typing import Optional

from .config import slack_users


@dataclass
class TFSEvent:
    """Base class for all TFS events"""

    item_title: str  # Work item title, PR title, etc.
    trigger: str
    subscriber: str
    url: str

    @property
    def link(self) -> str:
        return f"<{self.url}|{self.item_title}>"

    @staticmethod
    def from_text(cls, pattern, text, **known_fields):
        match = re.match(pattern, text)
        known_fields.update({k: v.strip() for k, v in match.groupdict().items()})
        return cls(**known_fields)

    def to_markdown(self) -> str:
        raise NotImplementedError


@dataclass
class WorkItemEvent(TFSEvent):
    """Currently supports only 'assigned to' events"""

    changed_by: str
    assigned_to: str

    @classmethod
    def from_text(cls, text, **known_fields):
        pattern = (
            r"Azure DevOps Server Product Backlog Item \d+ was assigned to you (?P<item_title>.+) View work item "
            r"Changed By (?P<changed_by>(\w+ ){3})"
            r"Assigned To (?P<assigned_to>(\w+ ){3})"
        )
        return super().from_text(cls, pattern, text, **known_fields)

    def to_markdown(self) -> str:
        changed_by = f"<@{slack_users[self.changed_by]}>"
        if self.subscriber == self.assigned_to:
            assigned_to = "тебя"
            emoji = ":ya_v_ahue:"
        else:
            assigned_to = f"<@{slack_users[self.assigned_to]}>"
            emoji = ""
        return " ".join([changed_by, "повесил на", assigned_to, "таску", self.link, emoji])


@dataclass
class BuildCompletedEvent(TFSEvent):
    status: str

    @classmethod
    def from_text(cls, text, **known_fields):
        pattern = (
            r"Azure DevOps Server Build (.*) (?P<status>succeeded|failed).*"
            r"Pull request Title (?P<item_title>.*) Source branch"
        )
        return super().from_text(cls, pattern, text, **known_fields)

    def to_markdown(self) -> str:
        if self.status == "succeeded":
            status = "успешно завершилась :white_check_mark:"
        else:
            status = "упала :x:"
        return f"Сборка {self.link} {status}"


@dataclass
class PullRequestEvent(TFSEvent):
    """Base class for specific events in PRs"""

    initiator: str

    @property
    def initiator_id(self):
        return f"<@{slack_users[self.initiator]}>"


@dataclass
class PullRequestReviewerAddedEvent(PullRequestEvent):
    reviewer: str

    @classmethod
    def from_text(cls, text, **known_fields):
        pattern = r"Azure DevOps Server (?P<item_title>.*) (?P<reviewer>(\w+ ){3})was added as a reviewer"
        return super().from_text(cls, pattern, text, **known_fields)

    def to_markdown(self) -> str:
        if self.reviewer == self.subscriber:
            reviewer = "тебя"
        else:
            reviewer = f"<@{slack_users[self.reviewer]}>"
        return f"{self.initiator_id} просит {reviewer} посмотреть пиар {self.link} :eyes:"


@dataclass
class PullRequestVoteEvent(PullRequestEvent):
    vote: str

    @classmethod
    def from_text(cls, text, **known_fields):
        vote_options = [
            "approved the changes",
            "has approved with suggestions",
            "is waiting for the author to respond",
            "has rejected the changes",
            "reset their vote",
        ]
        vote_options = "|".join(vote_options)
        pattern = fr"Azure DevOps Server (?P<item_title>.*) (?P<initiator>(\w+ ){{3}})(?P<vote>{vote_options})"
        return super().from_text(cls, pattern, text, **known_fields)

    def to_markdown(self) -> str:
        if self.vote == "approved the changes":
            return f"{self.initiator_id} аппрувнул пиар {self.link} :spinning_gorilla:"

        elif self.vote == "has approved with suggestions":
            return f"{self.initiator_id} поставил аппрув к пиару {self.link}, но есть один нюанс :hmmm:"

        elif self.vote == "is waiting for the author to respond":
            return f"{self.initiator_id} ждёт тебя к ответу в пиаре {self.link} :coolstorybob:"

        if self.vote == "has rejected the changes":
            return f"{self.initiator_id} поставил реджект к пиару {self.link} :pepe-rage:"

        elif self.vote == "reset their vote":
            return f"{self.initiator_id} снял свой голос с пиара {self.link} :slightly_frowning_face:"

        else:
            raise NotImplementedError


@dataclass
class PullRequestPushEvent(PullRequestEvent):
    commits: int

    @classmethod
    def from_text(cls, text, **known_fields):
        pattern = r"Azure DevOps Server (?P<item_title>.*) (?P<initiator>(\w+ ){3})pushed new changes.*Commits (?P<commits>\d+)"
        return super().from_text(cls, pattern, text, **known_fields)

    def to_markdown(self) -> str:
        return f"{self.initiator_id} запушил {self.commits} коммитов в {self.link} :factory_worker:"


@dataclass
class PullRequestCommentEvent(PullRequestEvent):
    action: str
    text: Optional[str] = None

    @classmethod
    def from_text(cls, text, **known_fields):
        comment_actions = ["commented", "replied", "deleted a comment", "edited a comment"]
        comment_actions = "|".join(comment_actions)
        pattern = fr"Azure DevOps Server (?P<item_title>.*) (?P<initiator>(\w+ ){{3}})has (?P<action>{comment_actions})"
        return super().from_text(cls, pattern, text, **known_fields)

    def to_markdown(self) -> str:
        if self.text is not None:
            quote_text = ">" + self.text.replace("\n", ">\n")

        if self.action == "commented":
            return f"{self.initiator_id} оставил пажилой коммент к пиару {self.link}:\n{quote_text}"

        elif self.action == "replied":
            return f"{self.initiator_id} ответил на вопросик в пиаре {self.link}:\n{quote_text}"

        elif self.action == "deleted a comment":
            return f"{self.initiator_id} взял свои слова обратно в пиаре {self.link} :pasportist:"

        elif self.action == "edited a comment":
            return (
                f"{self.initiator_id} поправился в обсуждении пиара {self.link}.\n"
                "Прошу выслать курьеру допник с изменением до вечера :dreamy_kacher:"
            )

        raise NotImplementedError


@dataclass
class PullRequestStatusUpdateEvent(PullRequestEvent):
    status: str

    @classmethod
    def from_text(cls, text, **known_fields):
        pattern = r"Azure DevOps Server (?P<item_title>.*) (?P<initiator>(\w+ ){3})(?P<status>completed|abandoned) the pull request"
        if pattern is None:
            raise NotImplementedError(text)
        return super().from_text(cls, pattern, text, **known_fields)

    def to_markdown(self) -> str:
        if self.status == "completed":
            return f"{self.initiator} завершил пиар {self.link} :ronaldo:"
        elif self.status == "abandoned":
            return f"{self.initiator} забросил пиар {self.link} :crying_cat_face:"
        raise NotImplementedError
