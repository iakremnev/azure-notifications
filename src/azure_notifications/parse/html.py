import re
from functools import singledispatch

from bs4 import BeautifulSoup

import azure_notifications.event_classes as events
from azure_notifications.config import Event

# Some classes to support single dispatch method


class WorkItemHtml(str):
    pass


class PullRequestHtml(str):
    pass


class PullRequestCommentHtml(str):
    pass


class BuildCompletedHtml(str):
    pass


@singledispatch
def parse_payload(html: str, **known_fields):
    raise NotImplementedError


@parse_payload.register
def parse_work_item(html: WorkItemHtml, **known_fields):
    soup = BeautifulSoup(html, "lxml")
    title: str = soup.find("div").text.strip()
    info = soup.find_all("span", class_="active")
    assert len(info) == 2
    changed_by: str = info[0].text.strip()
    assigned_to: str = info[1].text.strip()
    url: str = soup.find("a", class_="mobile-button btn-primary").get("href")

    fields = {
        "title": title,
        "changed_by": changed_by,
        "assigned_to": assigned_to,
        "url": url,
        "event_type": Event.WORK_ITEM_CHANGED.value,
    }
    fields.update(known_fields)
    return events.WorkItemEvent(**fields)


@parse_payload.register
def parse_pr_comment(html: PullRequestCommentHtml, **known_fields):
    soup = BeautifulSoup(html, "lxml")
    title = soup.find("td", class_="sub-title").text.strip()
    url = soup.find("a").get("href")  # Lucky it's the first
    text = soup.find_all("p")[-1].text.strip()

    fields = {
        "title": title,
        "url": url,
        "text": text,
        "event_type": Event.PR_COMMENT.value,
    }
    fields.update(known_fields)
    return events.PullRequestCommentEvent(**fields)


@parse_payload.register
def parse_build_completed(html: BuildCompletedHtml, **known_fields):
    soup = BeautifulSoup(html, "lxml")
    title = soup.find("td", text="Title").next_sibling.next_sibling.a
    title, url = title.text.strip(), title.get("href")
    requested_for: str = soup.find(
        "td", text="Requested for"
    ).next_sibling.next_sibling.text.strip()

    fields = {
        "title": title,
        "requested_for": requested_for,
        "url": url,
        "event_type": Event.BUILD_COMPLETED.value,
    }
    fields.update(known_fields)
    return events.BuildCompletedEvent(**fields)


@parse_payload.register
def parse_pr(html: PullRequestHtml, **known_fields):
    soup = BeautifulSoup(html, "lxml")
    title = soup.find("td", class_="sub-title").text.strip()
    url = soup.find("a").get("href")  # Lucky it's the first
    initiator = known_fields["initiator"]

    subject = known_fields.pop("subject")
    pr_author = re.fullmatch(r".*\((.+)\)", subject)[1]

    fields = {
        "title": title,
        "url": url,
        "pr_author": pr_author,
        "event_type": Event.PULL_REQUEST.value,
    }

    trigger = known_fields["trigger"]

    if trigger == "PushNotification":
        n_commits = int(
            soup.find("td", text="Commits").next_sibling.next_sibling.text.strip()
        )
        fields["commits"] = n_commits

    elif trigger == "ReviewerVoteNotification":
        # Table parsing parkour
        row_iter = soup.find("a", text=initiator).parent.next_siblings
        for _ in range(4):
            vote = next(row_iter)
        vote = vote.text.strip()
        fields["vote"] = vote

    elif trigger == "ReviewersUpdateNotification":
        message: str = soup.find("td", class_="title").text.strip()
        reviewer, status = re.match(r"(.+) was (\w+)", message).groups()
        if status != "added":
            raise NotImplementedError
        fields["reviewer"] = reviewer
        fields["status"] = status

    elif trigger == "StatusUpdateNotification":
        message = soup.find("div")
        if "completed" in message.text:
            fields["status"] = "Completed"
        else:
            raise NotImplementedError

    else:
        raise NotImplementedError

    fields.update(known_fields)
    return events.PullRequestEvent(**fields)
