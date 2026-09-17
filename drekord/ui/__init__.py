"""
drekord.ui — Discord Components V2 layout system.

Build rich, structured messages using Discord's COMPONENTS_V2 system.
All components are fully object-oriented — no raw dicts needed.

Usage::

    from drekord.ui import (
        LayoutView, Container, TextDisplay, Separator,
        ActionRow, Button, Section, Thumbnail,
        MediaGallery, MediaGalleryItem, File,
        StringSelect, SelectOption,
    )

    view = LayoutView()
    container = Container(
        TextDisplay("## Hello World"),
        Separator(),
        accent_color="#5865F2",
    )
    view.add_item(container)

    action_row = ActionRow()
    action_row.add_item(Button(label="Click Me", style=1, custom_id="btn_1"))
    container.add_item(action_row)

    await client.messages.channel(ch).send(view=view)
"""

from .view import LayoutView
from .components import (
    # Base
    Component,
    # Layout
    ActionRow,
    Section,
    Container,
    Separator,
    # Content
    TextDisplay,
    Thumbnail,
    MediaGallery,
    File,
    # Interactive
    Button,
    StringSelect,
    UserSelect,
    RoleSelect,
    MentionableSelect,
    ChannelSelect,
    # Data helpers
    MediaGalleryItem,
    SelectOption,
    UnfurledMediaItem,
)

__all__ = [
    "LayoutView",
    # Layout components
    "ActionRow",
    "Section",
    "Container",
    "Separator",
    # Content components
    "TextDisplay",
    "Thumbnail",
    "MediaGallery",
    "File",
    # Interactive components
    "Button",
    "StringSelect",
    "UserSelect",
    "RoleSelect",
    "MentionableSelect",
    "ChannelSelect",
    # Data helpers
    "MediaGalleryItem",
    "SelectOption",
    "UnfurledMediaItem",
]
