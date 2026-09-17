"""
Components V2 example for Drekord.

Demonstrates building rich, structured messages using the
drekord.ui LayoutView system (Discord's COMPONENTS_V2).
"""

import asyncio

import drekord
from drekord.ui import (
    LayoutView,
    Container,
    TextDisplay,
    Separator,
    ActionRow,
    Button,
    Section,
    Thumbnail,
    MediaGallery,
    MediaGalleryItem,
    File,
    StringSelect,
    SelectOption,
)


TOKEN = "YOUR_BOT_TOKEN"
CHANNEL_ID = 67777777777777777777 


async def main():
    async with drekord.Client(token=TOKEN) as client:

        #  1. Simple text display 
        view = LayoutView()
        view.add_item(TextDisplay("# Hello from Drekord! 🎉"))
        view.add_item(TextDisplay("This message uses **Components V2**"))
        await client.messages.channel(CHANNEL_ID).send(view=view)
        print("Sent simple text display.")

        #  2. Container with accent color 
        view = LayoutView()
        container = Container(
            TextDisplay("## Server Stats"),
            Separator(),
            TextDisplay("**Members:** 1,234\n**Online:** 567\n**Channels:** 42"),
            accent_color="#5865F2",
        )
        view.add_item(container)
        await client.messages.channel(CHANNEL_ID).send(view=view)
        print("Sent container with accent color.")

        #  3. Section with thumbnail 
        view = LayoutView()
        section = Section(
            TextDisplay("## Game Update v2.0"),
            TextDisplay("New features, bug fixes, and more!"),
            accessory=Thumbnail(
                media="https://example.com/update-banner.png",
                description="Update banner",
            ),
        )
        view.add_item(section)
        await client.messages.channel(CHANNEL_ID).send(view=view)
        print("Sent section with thumbnail.")

        #  4. Buttons 
        view = LayoutView()
        container = Container(
            TextDisplay("## Vote below!"),
            Separator(),
        )

        row = ActionRow()
        row.add_item(Button(label="Yes", style=3, custom_id="vote_yes"))
        row.add_item(Button(label="No", style=4, custom_id="vote_no"))
        row.add_item(Button(label="Info", style=2, custom_id="vote_info"))
        container.add_item(row)

        # Link button in its own action row
        link_row = ActionRow()
        link_row.add_item(Button(
            label="Learn More",
            style=5,
            url="https://example.com",
        ))
        container.add_item(link_row)

        view.add_item(container)
        await client.messages.channel(CHANNEL_ID).send(view=view)
        print("Sent buttons.")

        #  5. Select menu 
        view = LayoutView()
        container = Container(
            TextDisplay("## Choose your class:"),
        )
        row = ActionRow()
        row.add_item(StringSelect(
            custom_id="class_select",
            options=[
                SelectOption("Warrior", "warrior", description="Tanky melee fighter"),
                SelectOption("Mage", "mage", description="Ranged magic damage"),
                SelectOption("Rogue", "rogue", description="Fast and stealthy"),
                SelectOption("Healer", "healer", description="Support your team"),
            ],
            placeholder="Select a class...",
            min_values=1,
            max_values=1,
        ))
        container.add_item(row)
        view.add_item(container)
        await client.messages.channel(CHANNEL_ID).send(view=view)
        print("Sent select menu.")

        #  6. Media gallery 
        view = LayoutView()
        view.add_item(TextDisplay("## Screenshot gallery"))
        gallery = MediaGallery(
            MediaGalleryItem(
                "https://example.com/screenshot1.png",
                description="Main menu",
            ),
            MediaGalleryItem(
                "https://example.com/screenshot2.png",
                description="In-game combat",
            ),
            MediaGalleryItem(
                "https://example.com/screenshot3.png",
                description="Character customization",
                spoiler=True,
            ),
        )
        view.add_item(gallery)
        await client.messages.channel(CHANNEL_ID).send(view=view)
        print("Sent media gallery.")

        #  7. File component 
        view = LayoutView()
        view.add_item(TextDisplay("## Download the patch notes:"))
        view.add_item(File(media="attachment://patch_notes.pdf"))
        # Note: You'd also pass the actual file in the files parameter:
        # await client.messages.channel(CHANNEL_ID).send(
        #     view=view,
        #     files=[("patch_notes.pdf", open("patch_notes.pdf", "rb"), "application/pdf")],
        # )
        print("(File component example — not sent without actual file)")

        #  8. Complex nested layout 
        view = LayoutView()

        # Header container
        header = Container(
            TextDisplay("# 🎮 Weekly Tournament"),
            TextDisplay("Sign up now for this weekend's tournament!"),
            accent_color="#57F287",
        )
        view.add_item(header)

        view.add_item(Separator(spacing=2))

        # Info container
        info = Container(
            TextDisplay("## Details"),
            TextDisplay("**Date:** Saturday, 8 PM UTC\n**Prize:** $500\n**Format:** 5v5"),
            accent_color="#FEE75C",
        )
        view.add_item(info)

        view.add_item(Separator())

        # Action buttons
        action_row = ActionRow()
        action_row.add_item(Button(label="Sign Up", style=1, custom_id="signup"))
        action_row.add_item(Button(label="Rules", style=2, custom_id="rules"))
        action_row.add_item(Button(label="Discord", style=5, url="https://example.com/discord"))
        view.add_item(action_row)

        await client.messages.channel(CHANNEL_ID).send(view=view)
        print("Sent complex nested layout.")


if __name__ == "__main__":
    asyncio.run(main())
