# Drekord Discord API Wrapper

A lightweight, async Discord REST API wrapper for Python.

BTW, Drekord is **not** a bot framework (like `discord.py`). It is a pure REST API client designed to be integrated into any async application that needs to interact with the Discord API, without maintaining a persistent WebSocket connection.

## Features
- **Pure REST:** No WebSocket gateway; just API calls
- **Fully async:** Built on `aiohttp` for clean `async/await` usage
- **Object-oriented:** Making it ez to use x)
- **Rate-limit aware:** Automatic retry on rate limits and transient errors


## Installation

```bash
pip install drekord
```

Or from source:

```bash
git clone https://github.com/drek124/drekord.git
cd drekord
pip install -e .
```

## Quick Start

```python
import asyncio
import drekord


async def main():
    async with drekord.Client(token="YOUR_BOT_TOKEN") as client:
        # Get the current bot user
        me = await client.users.me()
        print(f"Logged in as {me.username}")

        # Send a message to a channel
        msg = await client.messages.channel(CHANNEL_ID).send(
            content="Hello from Drekord! 🎉"
        )
        print(f"Sent message {msg.id}")

        # Read the last 10 messages
        messages = await client.messages.channel(CHANNEL_ID).list(limit=10)
        for m in messages:
            print(f"{m.author.username}: {m.content}")


asyncio.run(main())
```

## API Overview

All API access is through resource classes on the `Client`:

```python
client.users       # UsersResource
client.guilds      # GuildResource
client.messages    # MessagesResource
client.channels    # ChannelResource
client.webhooks    # WebhooksResource
client.invites     # InvitesResource
client.emojis      # EmojiResource
```

### Users

```python
# Current bot user
me = await client.users.me()

# Get any user
user = await client.users.get(user_id)

# Create a DM
dm_channel = await client.users.dm(user_id)

# Edit the bot's username/avatar
me = await client.users.edit({"username": "new_name"})
```

### Messages

```python
# List messages in a channel
messages = await client.messages.channel(channel_id).list(limit=50)

# Send a message
msg = await client.messages.channel(channel_id).send(
    content="Hello!",
    embeds=[{"title": "My Embed", "description": "With an embed!"}],
)

# Edit a message
msg = await client.messages.channel(channel_id).edit(message_id, content="Edited!")

# Delete a message
await client.messages.channel(channel_id).delete(message_id)

# Pin / unpin
await client.messages.channel(channel_id).pin(message_id)
await client.messages.channel(channel_id).unpin(message_id)

# Bulk delete
await client.messages.bulk_delete(channel_id, [msg1_id, msg2_id, msg3_id])
```

### Guilds

```python
# List bot's guilds
guilds = await client.guilds.list()

# Get a guild
guild = await client.guilds.get(guild_id)
print(f"{guild.name} has {guild.approximate_member_count} members")

# Edit guild settings
await client.guilds.edit(guild_id, {"name": "New Name"})

# Leave a guild
await client.guilds.leave(guild_id)
```

### Guild Sub-Resources

```python
# Channels
channels = await client.guilds.channels(guild_id).list()
new_channel = await client.guilds.channels(guild_id).create({
    "name": "new-channel",
    "type": 0,  # text channel
})

# Members
members = await client.guilds.members(guild_id).list(limit=100)
member = await client.guilds.members(guild_id).get(user_id)

# Roles
roles = await client.guilds.roles(guild_id).list()
new_role = await client.guilds.roles(guild_id).create({"name": "Moderator", "color": 0xFF0000})

# Emojis
emojis = await client.guilds.emojis(guild_id).list()
```

### Channels

```python
channel = await client.channels.get(channel_id)

# Edit a channel
channel = await client.channels.edit(channel_id, {"name": "renamed"})

# Set permissions
await client.channels.set_permissions(channel_id, overwrite_id, allow="1024", deny="0")

# Trigger typing indicator
await client.channels.typing(channel_id)
```

### Webhooks

```python
# List webhooks in a channel
webhooks = await client.webhooks.channel_webhooks(channel_id)

# Create a webhook
webhook = await client.webhooks.create(channel_id, name="My Webhook")

# Execute a webhook (send via webhook)
await client.webhooks.execute(
    webhook.id,
    token=webhook.token,
    content="Posted via webhook!",
    username="Drekord Bot",
)

# Delete a webhook
await client.webhooks.delete(webhook.id)
```

### Raw Requests (Escape Hatch)

For endpoints not yet covered:

```python
data = await client.request("GET", "/gateway")
data = await client.request("POST", "/channels/123/threads", json={"name": "Thread"})
```

## Error Handling

Drekord raises typed exceptions for all error cases:

```python
import drekord

try:
    msg = await client.messages.channel(channel_id).send(content="Hello!")
except drekord.ForbiddenError:
    print("I don't have permission to send messages here!")
except drekord.NotFoundError:
    print("Channel not found!")
except drekord.RateLimitedError as e:
    print(f"Rate limited! Retry after {e.retry_after}s")
except drekord.HTTPError as e:
    print(f"HTTP error {e.status_code}: {e}")
```

### Exception Hierarchy

```
DrekordError
  └── HTTPError
        ├── BadRequestError      (400)
        ├── UnauthorizedError    (401)
        ├── ForbiddenError       (403)
        ├── NotFoundError        (404)
        ├── RateLimitedError     (429)
        └── DiscordServerError   (5xx)
```

## Models

All API responses are returned as model objects with typed properties:

```python
user = await client.users.get(user_id)
print(user.id)            # int
print(user.username)      # str
print(user.global_name)   # str | None
print(user.bot)           # bool
print(user.avatar_url())  # str | None

guild = await client.guilds.get(guild_id)
print(guild.name)         # str
print(guild.icon_url())   # str | None
print(guild.roles)        # list[Role]
```

Models also support dict-style access for unmapped fields:

```python
user_data = user.raw           # Get the raw dict
custom = user.get("custom_status")  # Access any field
```

## License

MIT
