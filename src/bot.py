from asyncio import Event
from os import getenv

from corded import CordedClient, GatewayEvent, Intents, Route
from loguru import logger


bot = CordedClient(token=getenv("TOKEN"), intents=Intents.default(), shard_count=1, shard_ids=[0])
allow = [int(c) for c in getenv("EXCLUDE_CHANNELS").split(";")]
guild = int(getenv("MAIN_GUILD"))
channels = {}

ready = Event()
ready.clear()

async def delete_message(channel_id: int, message_id: int) -> None:
    route = Route("/channels/{channel_id}/messages/{message_id}", channel_id=channel_id, message_id=message_id)

    await bot.http.request("delete", route, expect="response")

@bot.middleware
async def filter(event: GatewayEvent) -> GatewayEvent:
    if event.t and event.t.lower() in ("message_create", "message_update"):
        if event.typed_data["channel_id"] in allow:
            return
    return event

@bot.on("ready")
async def on_ready(_event: GatewayEvent) -> None:
    logger.info("Bot is ready!")

@bot.on("guild_create")
async def on_guild_create(event: GatewayEvent) -> None:
    logger.info("Received guild data for " + str(event.typed_data["id"]))

    if ready.is_set():
        return

    global guild

    data = event.typed_data

    if data["id"] == guild:
        logger.info("Populating guild info...")
        guild = data

        for channel in data["channels"]:
            channels[channel["id"]] = channel

        ready.set()
        logger.info("Guild is ready!")

@bot.on("message_create")
async def on_message_create(event: GatewayEvent) -> None:
    await ready.wait()

    data = event.typed_data
    channel = channels.get(data["channel_id"])

    if not channel:
        return

    if any([
        data["content"] != channel["name"],
        data.get("sticker_items"),
        data.get("attachments"),
        data.get("embeds"),
    ]):
        await delete_message(data["channel_id"], data["id"])
        logger.info(f"Deleted message from: {data['author']['id']}, content: {data['content']}")

@bot.on("message_update")
async def on_message_update(event: GatewayEvent) -> None:
    await ready.wait()

    data = event.typed_data
    channel = channels.get(data["channel_id"])

    if not channel:
        return

    await delete_message(data["channel_id"], data["id"])
    logger.info(f"Deleted message from: {data['author']['id']}, edited.")
