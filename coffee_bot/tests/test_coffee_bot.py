""" Main test of the coffee bot"""
import os
import logging
import pytest

from telethon import TelegramClient
from telethon.sessions import StringSession
from pytest import mark
from coffee_bot.password import PASSWORD


# Set up constans
logger = logging.getLogger(__name__)

#  API ID, hash and session string here
API_ID = int(os.environ["TELEGRAM_APP_ID"])
API_HASH = os.environ["TELEGRAM_APP_HASH"]
SESSION_STR = os.environ["TELETHON_SESSION"]

#  Bot username
BOT_USERNAME = os.environ["BOT_USERNAME"]


logger.debug('Using api id "%s" and hash "%s"', API_ID, API_HASH)
logger.debug('Using session string "%s"', SESSION_STR)


@pytest.fixture(scope="session")
async def client() -> TelegramClient:
    # Connect to the server
    await self.client.connect()
    # Issue a high level command to start receiving message
    await self.client.get_me()
    # Fill the entity cache
    await self.client.get_dialogs()

    yield TelegramClient(
        StringSession(SESSION_STR), API_ID, API_HASH,
        sequential_updates=True
    )

    await self.client.disconnect()
    await self.client.disconnected


#  @mark.asyncio
#  async def test_subscribtion(client: TelegramClient):
#      # Create a conversation
#      with client.conversation(BOT_USERNAME, timeout=5) as conv:
#          # Send a command
#          await conv.send_message('/start')
#          # Get response
#          resp: Message = await conv.get_response()
#          # Make assertions
#          assert "@myReplicaLikeBot" in resp.raw_text
#          assert "👍" in resp.raw_text
#          assert "👎" in resp.raw_text
#          await conv.send_message('/subscribe')
#          await conv.send_message(str(PASSWORD))
#          resp: Message = await conv.get_response()
#          print(resp)
