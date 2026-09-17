"""
Webhook usage example for Drekord.

Demonstrates creating and executing webhooks to send messages
without needing bot permissions in the channel.
"""

import asyncio

import drekord


TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_ID = 6777777777777777777


async def main():
    async with drekord.Client(token=TOKEN) as client:

        #  List existing webhooks 
        webhooks = await client.webhooks.channel_webhooks(CHANNEL_ID)
        print(f"Found {len(webhooks)} webhook(s) in channel {CHANNEL_ID}")

        #  Create a new webhook 
        webhook = await client.webhooks.create(
            CHANNEL_ID,
            name="Drekord Webhook",
        )
        print(f"Created webhook: {webhook.name} (ID: {webhook.id})")

        #  Execute the webhook (send a message) 
        msg = await client.webhooks.execute(
            webhook.id,
            token=webhook.token,
            content="Hello from a webhook! 🪝",
            username="Drekord Bot",
        )
        if msg:
            print(f"Webhook sent message ID: {msg.id}")

        #  Execute with embeds 
        embed = drekord.Embed(
            title="Webhook Embed",
            description="Embeds work with webhooks too!",
            color=0x57F287,
        )
        await client.webhooks.execute(
            webhook.id,
            token=webhook.token,
            embeds=[embed],
            username="Drekord Bot",
        )
        print("Sent webhook embed.")

        #  Edit the webhook 
        await client.webhooks.edit(webhook.id, {"name": "Renamed Webhook"})
        print("Webhook renamed.")

        #  Clean up 
        await client.webhooks.delete(webhook.id)
        print("Webhook deleted.")


if __name__ == "__main__":
    asyncio.run(main())
