"""
Basic usage example for Drekord v2.0.

This script demonstrates common operations with the new discord.py-inspired API:
- Logging in and getting bot info
- Reading messages from a channel
- Sending a message with an embed
- Listing guilds and channels
"""

import asyncio
import drekord


TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_ID = 6777777777777777777


async def main():
    async with drekord.Client(token=TOKEN) as client:

        #  Get the current bot user
        me = await client.me()
        print(f"Logged in as: {me.username} (ID: {me.id})")
        print(f"Bot? {me.bot}")
        print()

        #  List the bot's guilds
        guilds = await client.fetch_guilds()
        print(f"The bot is in {len(guilds)} guild(s):")
        for guild in guilds:
            print(f"  - {guild.name} (ID: {guild.id})")
        print()

        #  List channels in the first guild
        if guilds:
            first_guild = guilds[0]
            channels = await first_guild.fetch_channels()
            text_channels = [c for c in channels if c.type == 0]
            print(f"Text channels in {first_guild.name}:")
            for ch in text_channels:
                print(f"  #{ch.name} (ID: {ch.id})")
            print()

        #  Read the last 5 messages from a channel
        channel = await client.fetch_channel(CHANNEL_ID)
        messages = await channel.fetch_messages(limit=5)
        print(f"Last {len(messages)} messages in #{channel.name}:")
        for msg in messages:
            author = msg.author.display_name if msg.author else "Unknown"
            print(f"  [{author}] {msg.content}")
        print()

        #  Send a message with an embed
        embed = drekord.Embed(
            title="Hello from Drek! 🎉",
            description="This message was sent using the Drekord library.",
            color="#5865F2",
        )
        embed.set_footer(text="Drekord v2.0.0")

        sent_msg = await channel.send("Check out this embed:", embeds=[embed])
        print(f"Sent message ID: {sent_msg.id}")
        print(f"Message content: {sent_msg.content}")

        #  Edit the message we just sent
        await sent_msg.edit(content="This message has been edited")
        print("Message edited.")

        #  Get a specific user
        user = await client.fetch_user(472390873733136385)
        print(f"\nFetched user: {user.username} (ID: {user.id})")
        if user.avatar:
            print(f"Avatar URL: {user.avatar_url()}")

        #  Raw request (escape hatch)
        gateway = await client.request("GET", "/gateway")
        print(f"\nGateway URL: {gateway.get('url')}")


if __name__ == "__main__":
    asyncio.run(main())
