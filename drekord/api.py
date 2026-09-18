"""Drekord v2.0 API — this module is deprecated.

In v2.0, all API methods live directly on the Client and on model objects:

    channel = await client.fetch_channel(channel_id)
    await channel.send("Hello!")

    user = await client.fetch_user(user_id)
    print(user.display_name)

See ``client.py`` and ``models.py`` for the current implementation.
"""
