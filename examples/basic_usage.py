"""
Basic usage example for Drekord.

This script demonstrates common operations:
- Logging in and getting bot info
- Reading messages from a channel
- Sending a message with an embed
- Listing guilds and channels


"""

import asyncio
import drekord


TOKEN = "YOUR_BOT_TOKEN" # better to use .env instead of string but u get the point
CHANNEL_ID = 6777777777777777777  


async def main():
    # Create the client as an async context manager
    async with drekord.Client(token=TOKEN) as client:

        #  Get the current bot user 
        me = await client.users.me()
        print(f"Logged in as: {me.username} (ID: {me.id})")
        print(f"Bot? {me.bot}")
        print()

        #  List the bot's guilds 
        guilds = await client.guilds.list()
        print(f"The bot is in {len(guilds)} guild(s):")
        for guild in guilds:
            print(f"  - {guild.name} (ID: {guild.id})")
        print()

        #  List channels in the first guild 
        if guilds:
            first_guild = guilds[0]
            channels = await client.guilds.channels(first_guild.id).list()
            text_channels = [c for c in channels if c.type == 0]
            print(f"Text channels in {first_guild.name}:")
            for ch in text_channels:
                print(f"  #{ch.name} (ID: {ch.id})")
            print()

        #  Read the last 5 messages from a channel 
        messages = await client.messages.channel(CHANNEL_ID).list(limit=5)
        print(f"Last {len(messages)} messages in channel {CHANNEL_ID}:")
        for msg in messages:
            author = msg.author.display_name() if msg.author else "Unknown"
            print(f"  [{author}] {msg.content}")
        print()

        #  Send a message with an embed 
        embed = drekord.Embed(
            title="Hello from Drek! 🎉",
            description="This message was sent using the Drekord library.",
            color="#5865F2",  # Discord blurple owo
        )
        embed.set_footer(text="Drekord v0.1.0")

        sent_msg = await client.messages.channel(CHANNEL_ID).send(
            content="Check out this embed:",
            embeds=[embed],
        )
        print(f"Sent message ID: {sent_msg.id}")
        print(f"Message content: {sent_msg.content}")

        #  Edit the message we just sent 
        await client.messages.channel(CHANNEL_ID).edit(
            sent_msg.id,
            content="This message has been edited",
        )
        print("Message edited.")

        #  Get a specific user 
        user = await client.users.get(472390873733136385)
        print(f"\nFetched user: {user.username} (ID: {user.id})")
        if user.avatar:
            print(f"Avatar URL: {user.avatar_url()}")

        #  Raw request (escape hatch) 
        gateway = await client.request("GET", "/gateway")
        print(f"\nGateway URL: {gateway.get('url')}")


if __name__ == "__main__":
    asyncio.run(main())
