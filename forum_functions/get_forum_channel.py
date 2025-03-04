from bot.client_instance import get_client
from discord.ext.commands import Bot
from discord import Guild, ForumChannel
from tools.checks import check_guild, check_forum_channel
from settings.config import GUILD_ID, FORUM_CHANNEL_ID
from typing import Optional

def get_forum_channel() -> Optional[ForumChannel]:
    """Retorna forum_channel, se possível"""

    client: Optional[Bot] = get_client()

    try:
        guild: Optional[Guild] = check_guild(client, GUILD_ID)
        forum_channel: Optional[ForumChannel] = (
            check_forum_channel(guild, FORUM_CHANNEL_ID)
        )

        assert guild and forum_channel
    except (AttributeError, AssertionError):
        return None

    return forum_channel
