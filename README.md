# Drekord Discord API Wrapper

A lightweight, async Discord REST API wrapper for Python.

> **Drekord is NOT a bot framework** (like `discord.py`). It is a pure REST API client designed to be integrated into any async application that needs to interact with the Discord API, without maintaining a persistent WebSocket connection.

## Features
- **Pure REST:** No WebSocket gateway; just API calls x)
- **Fully async:** Built on `aiohttp` for clean `async/await` usage
- **Object-Oriented:** Call methods directly on channels, messages, users, guilds, etc.
- **discord.py-inspired:** Familiar API if you've used discord.py before
- **Rate-limit awareness:** Automatic retry on rate limits and transient errors

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
        me = await client.me()
        print(f"Logged in as {me.username}")

        # Fetch a channel and send a message
        channel = await client.fetch_channel(CHANNEL_ID)
        msg = await channel.send(content="Hello from Drekord! 🎉")
        print(f"Sent message {msg.id}")

        # Read the last 10 messages
        messages = await channel.fetch_messages(limit=10)
        for m in messages:
            print(f"{m.author.username}: {m.content}")


asyncio.run(main())
```

## API Overview

### Client Methods

Top-level `fetch_*` methods on the client:

```python
await client.me()                              # Current bot user
await client.fetch_user(user_id)               # Any user
await client.fetch_channel(channel_id)         # Any channel
await client.fetch_message(channel_id, msg_id) # A specific message
await client.fetch_guilds()                    # List bot's guilds
await client.fetch_guild(guild_id)             # A specific guild
await client.fetch_member(guild_id, user_id)   # A guild member
await client.fetch_webhook(webhook_id)         # A webhook
await client.fetch_webhooks(channel_id)        # Webhooks in a channel
```

### Channels

```python
channel = await client.fetch_channel(channel_id)

# Send messages
msg = await channel.send(content="Hello!", tts=False)
msg = await channel.send(embeds=[embed])
msg = await channel.send(view=layout_view)  # Components V2

# Read messages
messages = await channel.fetch_messages(limit=50)
message = await channel.fetch_message(message_id)

# Edit the channel
channel = await channel.edit(name="renamed", topic="New topic")

# Delete the channel
await channel.delete()

# Typing indicator
await channel.typing()

# Invites
invites = await channel.fetch_invites()
```

### Messages

```python
message = await channel.fetch_message(msg_id)

# Edit
await message.edit(content="Edited!")

# Delete
await message.delete(reason="Cleanup requested")

# Pin/Unpin
await message.pin()
await message.unpin()

# Reactions
await message.add_reaction("👍")
await message.remove_reaction("👍")

# Crosspost (announcements)
await message.crosspost()
```

### Users

```python
user = await client.fetch_user(user_id)

# Properties
print(user.username)
print(user.display_name)  # global_name or username
print(user.avatar_url())

# Create DM
dm_channel = await user.create_dm()

# Re-fetch
user = await user.fetch()
```

### Guilds

```python
guild = await client.fetch_guild(guild_id)

# Properties
print(guild.name)

# Fetch sub-resources
channels = await guild.fetch_channels()
members = await guild.fetch_members(limit=100)
roles = await guild.fetch_roles()
emojis = await guild.fetch_emojis()
bans = await guild.fetch_bans()
audit_logs = await guild.fetch_audit_logs(limit=50)

# Create
new_channel = await guild.create_channel({"name": "new-channel", "type": 0})
new_role = await guild.create_role({"name": "Moderator", "color": 0xFF0000})

# Edit
guild = await guild.edit({"name": "New Name"})

# Leave / Delete
await guild.leave()
await guild.delete()
```

### Members

```python
member = await client.fetch_member(guild_id, user_id)

# Properties
print(member.display_name)
print(member.roles)
print(member.joined_at)

# Actions
await member.kick(reason="Rule violation")
await member.ban(reason="Spam", delete_message_days=7)
await member.edit(nick="New Nick", roles=[role_id1, role_id2])
```

### Webhooks

```python
webhook = await client.fetch_webhook(webhook_id)

# Execute (send)
await webhook.execute(content="Hello!", username="Bot")
await webhook.execute(embeds=[embed], wait=True)

# Edit
await webhook.edit({"name": "New Name"})

# Delete
await webhook.delete()
```

### Embeds

```python
embed = drekord.Embed(
    title="Hello",
    description="World",
    color=0x5865F2,
)
embed.set_thumbnail(url="https://example.com/thumb.png")
embed.add_field(name="Field 1", value="Value 1", inline=True)
embed.set_footer(text="Footer text")

await channel.send(embeds=[embed])
```

### Components V2

```python
from drekord.ui import (
    LayoutView, Container, TextDisplay, Separator,
    ActionRow, Button, Section, Thumbnail,
)

view = LayoutView()
view.add_item(Container(
    TextDisplay("## Hello World"),
    Separator(),
    ActionRow(
        Button(label="Click Me", style=1, custom_id="btn_1"),
    ),
    accent_color="#5865F2",
))

await channel.send(view=view)
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
    msg = await channel.send(content="Hello!")
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
user = await client.fetch_user(user_id)
print(user.id)            # int
print(user.username)      # str
print(user.display_name)  # str (global_name or username)
print(user.bot)           # bool
print(user.avatar_url())  # str | None

channel = await client.fetch_channel(channel_id)
print(channel.id)         # int
print(channel.name)       # str | None
print(channel.type_name)  # str ("text", "voice", etc.)

message = await channel.fetch_message(msg_id)
print(message.content)    # str
print(message.author)     # User | None
print(message.embeds)     # list[Embed]
```

## License

MIT
