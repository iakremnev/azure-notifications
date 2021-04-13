import json
import pytest
import glob
from slack_sdk.web.async_client import AsyncWebClient

import azure_notifications.worker as main
from azure_notifications.config import SLACK_BOT_TOKEN
from azure_notifications.event_classes import TFSEvent


slack_event_jsons = glob.glob("data/json/*.json")
# slack_event_jsons = ["data/json/1616490112.017700.json"]


@pytest.fixture(scope="session")
def mute_slack_client():

    async def await_200(*args, **kwargs):
        class Response:
            def __init__(self) -> None:
                self.status_code = 200
        return Response()

    client = AsyncWebClient(SLACK_BOT_TOKEN)
    client.chat_postMessage = await_200
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize("json_path", slack_event_jsons)
async def test_service(mute_slack_client, json_path):
    with open(json_path) as f:
        event = json.load(f)
    headers, plain_text, html_url = main.preprocess_slack_event(event)
    event, response = await main.work(mute_slack_client, headers, plain_text, html_url)
    assert isinstance(event, TFSEvent), event
    assert response.status_code == 200
