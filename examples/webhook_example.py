"""
Webhook usage example for Drekord v2.0.

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
        webhooks = await client.fetch_webhooks(CHANNEL_ID)
        print(f"Found {len(webhooks)} webhook(s) in channel {CHANNEL_ID}")

        #  Create a new webhook
        webhook = await client.create_webhook(CHANNEL_ID, name="Drekord Webhook")
        print(f"Created webhook: {webhook.name} (ID: {webhook.id})")

        #  Execute the webhook (send a message)
        msg = await webhook.execute("Hello from a webhook! 🪝", username="Drekord Bot")
        if msg:
            print(f"Webhook sent message ID: {msg.id}")

        #  Execute with embeds
        embed = drekord.Embed(
            title="Webhook Embed",
            description="Embeds work with webhooks too!",
            color=0x57F287,
        )
        await webhook.execute(
            embeds=[embed],
            username="Drekord Bot",
        )
        print("Sent webhook embed.")

        #  Edit the webhook
        await webhook.edit({"name": "Renamed Webhook"})
        print("Webhook renamed.")

        #  Clean up
        await webhook.delete()
        print("Webhook deleted.")


if __name__ == "__main__":
    asyncio.run(main())
