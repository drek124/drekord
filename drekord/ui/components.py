"""Discord Components V2 component classes.

Every component subclass implements ``to_dict() -> dict[str, Any]`` to
serialize itself into the JSON payload Discord expects. Components are
fully object-oriented — no raw dicts are needed from the caller.

Component type IDs (from Discord API):
    1  ActionRow
    2  Button
    3  StringSelect
    5  UserSelect
    6  RoleSelect
    7  MentionableSelect
    8  ChannelSelect
    9  Section
    10 TextDisplay
    11 Thumbnail
    12 MediaGallery
    13 File
    14 Separator
    17 Container
"""

from __future__ import annotations

from typing import Any


def _parse_color(value: int | str | None) -> int | None:
    """Parse a color value into an int."""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    hex_str = value.lstrip("#").lstrip("0x")
    return int(hex_str, 16)


# ======================================================================
# Base
# ======================================================================

class Component:
    """Base class for all Components V2 components."""

    # Subclasses should override this with the Discord component type ID
    _type: int = 0

    def __init__(self, *, id: int | None = None):
        self._id = id

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"type": self._type}
        if self._id is not None:
            data["id"] = self._id
        return data

    def __repr__(self) -> str:
        return f"<{type(self).__name__}>"


# ======================================================================
# Data helper classes
# ======================================================================

class UnfurledMediaItem:
    """Represents an unfurled media item (URL or attachment reference)."""

    def __init__(self, url: str):
        self._url = url

    def to_dict(self) -> dict[str, Any]:
        return {"url": self._url}

    def __repr__(self) -> str:
        return f"<UnfurledMediaItem url='{self._url}'>"


class MediaGalleryItem:
    """A single item in a MediaGallery."""

    def __init__(
        self,
        media: str | UnfurledMediaItem,
        *,
        description: str | None = None,
        spoiler: bool = False,
    ):
        if isinstance(media, str):
            self._media = UnfurledMediaItem(media)
        else:
            self._media = media
        self._description = description
        self._spoiler = spoiler

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"media": self._media.to_dict()}
        if self._description is not None:
            data["description"] = self._description
        if self._spoiler:
            data["spoiler"] = True
        return data

    def __repr__(self) -> str:
        return f"<MediaGalleryItem description='{self._description}'>"


class SelectOption:
    """A single option in a select menu."""

    def __init__(
        self,
        label: str,
        value: str,
        *,
        description: str | None = None,
        emoji: dict[str, Any] | None = None,
        default: bool = False,
    ):
        self._label = label
        self._value = value
        self._description = description
        self._emoji = emoji
        self._default = default

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "label": self._label,
            "value": self._value,
        }
        if self._description is not None:
            data["description"] = self._description
        if self._emoji is not None:
            data["emoji"] = self._emoji
        if self._default:
            data["default"] = True
        return data

    def __repr__(self) -> str:
        return f"<SelectOption label='{self._label}' value='{self._value}'>"


# ======================================================================
# Content components
# ======================================================================

class TextDisplay(Component):
    """Markdown text content component (type 10).

    Usage::

        td = TextDisplay("## Hello World")
        td = TextDisplay("Some *italic* text", id=42)
    """

    _type = 10

    def __init__(self, content: str, *, id: int | None = None):
        super().__init__(id=id)
        self._content = content

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        self._content = value

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["content"] = self._content
        return data

    def __repr__(self) -> str:
        preview = self._content[:50]
        return f"<TextDisplay content='{preview}...'>" if len(self._content) > 50 else f"<TextDisplay content='{preview}'>"


class Thumbnail(Component):
    """Small image accessory for a Section (type 11).

    Usage::

        thumb = Thumbnail(media="https://example.com/img.png")
        thumb = Thumbnail(media="attachment://image.png", description="Alt text", spoiler=True)
    """

    _type = 11

    def __init__(
        self,
        media: str | UnfurledMediaItem,
        *,
        description: str | None = None,
        spoiler: bool = False,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if isinstance(media, str):
            self._media = UnfurledMediaItem(media)
        else:
            self._media = media
        self._description = description
        self._spoiler = spoiler

    @property
    def media(self) -> UnfurledMediaItem:
        return self._media

    @property
    def description(self) -> str | None:
        return self._description

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["media"] = self._media.to_dict()
        if self._description is not None:
            data["description"] = self._description
        if self._spoiler:
            data["spoiler"] = True
        return data

    def __repr__(self) -> str:
        return f"<Thumbnail>"


class MediaGallery(Component):
    """Display a gallery of 1-10 images/media (type 12).

    Usage::

        gallery = MediaGallery(
            MediaGalleryItem("https://example.com/img1.png", description="First image"),
            MediaGalleryItem("https://example.com/img2.png", spoiler=True),
        )
    """

    _type = 12

    def __init__(self, *items: MediaGalleryItem, id: int | None = None):
        super().__init__(id=id)
        self._items = list(items)

    def add_item(self, item: MediaGalleryItem) -> MediaGallery:
        """Add a media gallery item. Returns self for chaining."""
        self._items.append(item)
        return self

    @property
    def items(self) -> list[MediaGalleryItem]:
        return list(self._items)

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["items"] = [item.to_dict() for item in self._items]
        return data

    def __repr__(self) -> str:
        return f"<MediaGallery items={len(self._items)}>"


class File(Component):
    """Display an attached file (type 13).

    Only supports the ``attachment://`` protocol for the media URL.

    Usage::

        f = File(media="attachment://report.pdf")
        f = File(media="attachment://image.png", spoiler=True)
    """

    _type = 13

    def __init__(
        self,
        media: str | UnfurledMediaItem,
        *,
        spoiler: bool = False,
        id: int | None = None,
    ):
        super().__init__(id=id)
        if isinstance(media, str):
            self._media = UnfurledMediaItem(media)
        else:
            self._media = media
        self._spoiler = spoiler

    @property
    def media(self) -> UnfurledMediaItem:
        return self._media

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["file"] = self._media.to_dict()
        if self._spoiler:
            data["spoiler"] = True
        return data

    def __repr__(self) -> str:
        return f"<File>"


# ======================================================================
# Layout components
# ======================================================================

class Separator(Component):
    """Vertical spacing/divider between components (type 14).

    Usage::

        sep = Separator()
        sep = Separator(spacing=2, divider=True)
    """

    _type = 14

    def __init__(
        self,
        *,
        spacing: int = 1,
        divider: bool = True,
        id: int | None = None,
    ):
        super().__init__(id=id)
        self._spacing = spacing
        self._divider = divider

    @property
    def spacing(self) -> int:
        return self._spacing

    @spacing.setter
    def spacing(self, value: int) -> None:
        self._spacing = value

    @property
    def divider(self) -> bool:
        return self._divider

    @divider.setter
    def divider(self, value: bool) -> None:
        self._divider = value

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        if not self._divider:
            data["divider"] = False
        if self._spacing != 1:
            data["spacing"] = self._spacing
        return data

    def __repr__(self) -> str:
        return f"<Separator spacing={self._spacing} divider={self._divider}>"


class ActionRow(Component):
    """Container for interactive components (buttons, selects) (type 1).

    Usage::

        row = ActionRow()
        row.add_item(Button(label="Yes", style=3, custom_id="yes"))
        row.add_item(Button(label="No", style=4, custom_id="no"))

        # Or with select:
        row = ActionRow()
        row.add_item(StringSelect(
            custom_id="pick",
            options=[
                SelectOption("Option 1", "opt1"),
                SelectOption("Option 2", "opt2"),
            ],
        ))
    """

    _type = 1

    def __init__(self, *components: Component, id: int | None = None):
        super().__init__(id=id)
        self._children: list[Component] = list(components)

    def add_item(self, component: Component) -> ActionRow:
        """Add an interactive component (Button or Select). Returns self."""
        self._children.append(component)
        return self

    def remove_item(self, index: int) -> ActionRow:
        """Remove a component by index. Returns self."""
        if 0 <= index < len(self._children):
            self._children.pop(index)
        return self

    @property
    def children(self) -> list[Component]:
        return list(self._children)

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["components"] = [c.to_dict() for c in self._children]
        return data

    def __repr__(self) -> str:
        return f"<ActionRow children={len(self._children)}>"


class Section(Component):
    """Layout component that pairs text content with an accessory (type 9).

    The accessory can be a Button or a Thumbnail.

    Usage::

        section = Section(
            TextDisplay("## Patch Notes"),
            TextDisplay("Version 1.2 released!"),
            accessory=Thumbnail(media="https://example.com/patch.png"),
        )
    """

    _type = 9

    def __init__(
        self,
        *components: TextDisplay | str,
        accessory: Button | Thumbnail | None = None,
        id: int | None = None,
    ):
        super().__init__(id=id)
        # Auto-wrap strings in TextDisplay
        self._components: list[TextDisplay] = []
        for c in components:
            if isinstance(c, str):
                self._components.append(TextDisplay(c))
            else:
                self._components.append(c)
        self._accessory = accessory

    @property
    def accessory(self) -> Button | Thumbnail | None:
        return self._accessory

    @accessory.setter
    def accessory(self, value: Button | Thumbnail | None) -> None:
        self._accessory = value

    def add_text(self, content: str | TextDisplay) -> Section:
        """Add a TextDisplay to this section. Returns self."""
        if isinstance(content, str):
            self._components.append(TextDisplay(content))
        else:
            self._components.append(content)
        return self

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["components"] = [c.to_dict() for c in self._components]
        if self._accessory is not None:
            data["accessory"] = self._accessory.to_dict()
        return data

    def __repr__(self) -> str:
        return f"<Section components={len(self._components)} accessory={self._accessory is not None}>"


class Container(Component):
    """Visually groups components with an optional accent color bar (type 17).

    Usage::

        container = Container(
            TextDisplay("## This is a container!"),
            Separator(),
            TextDisplay("Hello world!"),
            accent_color="#5865F2",
        )

        # Or build incrementally:
        container = Container(accent_color=0x5865F2)
        container.add_item(TextDisplay("Hello!"))
    """

    _type = 17

    def __init__(
        self,
        *components: Component | str,
        accent_color: int | str | None = None,
        spoiler: bool = False,
        id: int | None = None,
    ):
        super().__init__(id=id)
        self._children: list[Component] = []
        for c in components:
            if isinstance(c, str):
                self._children.append(TextDisplay(c))
            else:
                self._children.append(c)
        self._accent_color = _parse_color(accent_color)
        self._spoiler = spoiler

    @property
    def accent_color(self) -> int | None:
        return self._accent_color

    @accent_color.setter
    def accent_color(self, value: int | str | None) -> None:
        self._accent_color = _parse_color(value)

    @property
    def spoiler(self) -> bool:
        return self._spoiler

    @spoiler.setter
    def spoiler(self, value: bool) -> None:
        self._spoiler = value

    def add_item(self, component: Component | str) -> Container:
        """Add a child component. Strings are auto-wrapped in TextDisplay. Returns self."""
        if isinstance(component, str):
            self._children.append(TextDisplay(component))
        else:
            self._children.append(component)
        return self

    def remove_item(self, index: int) -> Container:
        """Remove a child component by index. Returns self."""
        if 0 <= index < len(self._children):
            self._children.pop(index)
        return self

    def clear_items(self) -> Container:
        """Remove all child components. Returns self."""
        self._children.clear()
        return self

    @property
    def children(self) -> list[Component]:
        return list(self._children)

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["components"] = [c.to_dict() for c in self._children]
        if self._accent_color is not None:
            data["accent_color"] = self._accent_color
        if self._spoiler:
            data["spoiler"] = True
        return data

    def __repr__(self) -> str:
        return f"<Container children={len(self._children)} accent_color={self._accent_color}>"


# ======================================================================
# Interactive components
# ======================================================================

class Button(Component):
    """A clickable button (type 2).

    Must be placed inside an ActionRow or a Section's accessory.

    Styles:
        1 = Primary (blue)
        2 = Secondary (gray)
        3 = Success (green)
        4 = Danger (red)
        5 = Link (navigates to URL)
        6 = Premium (purchasable SKU)

    Usage::

        btn = Button(label="Click Me", style=1, custom_id="my_button")
        btn = Button(label="Visit", style=5, url="https://example.com")
        btn = Button(sku_id="123456", style=6)  # Premium button
    """

    _type = 2

    # Style constants
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5
    PREMIUM = 6

    def __init__(
        self,
        *,
        label: str | None = None,
        style: int = 1,
        custom_id: str | None = None,
        url: str | None = None,
        sku_id: str | None = None,
        emoji: dict[str, Any] | None = None,
        disabled: bool = False,
        id: int | None = None,
    ):
        super().__init__(id=id)
        self._label = label
        self._style = style
        self._custom_id = custom_id
        self._url = url
        self._sku_id = sku_id
        self._emoji = emoji
        self._disabled = disabled

    @property
    def label(self) -> str | None:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        self._label = value

    @property
    def style(self) -> int:
        return self._style

    @style.setter
    def style(self, value: int) -> None:
        self._style = value

    @property
    def custom_id(self) -> str | None:
        return self._custom_id

    @custom_id.setter
    def custom_id(self, value: str) -> None:
        self._custom_id = value

    @property
    def disabled(self) -> bool:
        return self._disabled

    @disabled.setter
    def disabled(self, value: bool) -> None:
        self._disabled = value

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["style"] = self._style
        if self._label is not None:
            data["label"] = self._label
        if self._custom_id is not None:
            data["custom_id"] = self._custom_id
        if self._url is not None:
            data["url"] = self._url
        if self._sku_id is not None:
            data["sku_id"] = self._sku_id
        if self._emoji is not None:
            data["emoji"] = self._emoji
        if self._disabled:
            data["disabled"] = True
        return data

    def __repr__(self) -> str:
        if self._url:
            return f"<Button label='{self._label}' url='{self._url}'>"
        return f"<Button label='{self._label}' style={self._style} custom_id='{self._custom_id}'>"


class StringSelect(Component):
    """Select menu for picking from text options (type 3).

    Must be placed inside an ActionRow.

    Usage::

        select = StringSelect(
            custom_id="pick_option",
            options=[
                SelectOption("Option 1", "opt1", description="First option"),
                SelectOption("Option 2", "opt2", description="Second option"),
            ],
            placeholder="Choose an option...",
            min_values=0,
            max_values=2,
        )
    """

    _type = 3

    def __init__(
        self,
        *,
        custom_id: str,
        options: list[SelectOption],
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        id: int | None = None,
    ):
        super().__init__(id=id)
        self._custom_id = custom_id
        self._options = options
        self._placeholder = placeholder
        self._min_values = min_values
        self._max_values = max_values
        self._disabled = disabled

    @property
    def custom_id(self) -> str:
        return self._custom_id

    @property
    def options(self) -> list[SelectOption]:
        return list(self._options)

    def add_option(self, option: SelectOption) -> StringSelect:
        """Add an option. Returns self."""
        self._options.append(option)
        return self

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["custom_id"] = self._custom_id
        data["options"] = [o.to_dict() for o in self._options]
        if self._placeholder is not None:
            data["placeholder"] = self._placeholder
        if self._min_values != 1:
            data["min_values"] = self._min_values
        if self._max_values != 1:
            data["max_values"] = self._max_values
        if self._disabled:
            data["disabled"] = True
        return data

    def __repr__(self) -> str:
        return f"<StringSelect custom_id='{self._custom_id}' options={len(self._options)}>"


class UserSelect(Component):
    """Select menu for picking users (type 5).

    Must be placed inside an ActionRow.
    """

    _type = 5

    def __init__(
        self,
        *,
        custom_id: str,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        id: int | None = None,
    ):
        super().__init__(id=id)
        self._custom_id = custom_id
        self._placeholder = placeholder
        self._min_values = min_values
        self._max_values = max_values
        self._disabled = disabled

    @property
    def custom_id(self) -> str:
        return self._custom_id

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["custom_id"] = self._custom_id
        if self._placeholder is not None:
            data["placeholder"] = self._placeholder
        if self._min_values != 1:
            data["min_values"] = self._min_values
        if self._max_values != 1:
            data["max_values"] = self._max_values
        if self._disabled:
            data["disabled"] = True
        return data

    def __repr__(self) -> str:
        return f"<UserSelect custom_id='{self._custom_id}'>"


class RoleSelect(Component):
    """Select menu for picking roles (type 6).

    Must be placed inside an ActionRow.
    """

    _type = 6

    def __init__(
        self,
        *,
        custom_id: str,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        id: int | None = None,
    ):
        super().__init__(id=id)
        self._custom_id = custom_id
        self._placeholder = placeholder
        self._min_values = min_values
        self._max_values = max_values
        self._disabled = disabled

    @property
    def custom_id(self) -> str:
        return self._custom_id

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["custom_id"] = self._custom_id
        if self._placeholder is not None:
            data["placeholder"] = self._placeholder
        if self._min_values != 1:
            data["min_values"] = self._min_values
        if self._max_values != 1:
            data["max_values"] = self._max_values
        if self._disabled:
            data["disabled"] = True
        return data

    def __repr__(self) -> str:
        return f"<RoleSelect custom_id='{self._custom_id}'>"


class MentionableSelect(Component):
    """Select menu for picking users or roles (type 7).

    Must be placed inside an ActionRow.
    """

    _type = 7

    def __init__(
        self,
        *,
        custom_id: str,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        id: int | None = None,
    ):
        super().__init__(id=id)
        self._custom_id = custom_id
        self._placeholder = placeholder
        self._min_values = min_values
        self._max_values = max_values
        self._disabled = disabled

    @property
    def custom_id(self) -> str:
        return self._custom_id

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["custom_id"] = self._custom_id
        if self._placeholder is not None:
            data["placeholder"] = self._placeholder
        if self._min_values != 1:
            data["min_values"] = self._min_values
        if self._max_values != 1:
            data["max_values"] = self._max_values
        if self._disabled:
            data["disabled"] = True
        return data

    def __repr__(self) -> str:
        return f"<MentionableSelect custom_id='{self._custom_id}'>"


class ChannelSelect(Component):
    """Select menu for picking channels (type 8).

    Must be placed inside an ActionRow.

    Usage::

        select = ChannelSelect(
            custom_id="pick_channel",
            channel_types=[0, 2],  # text, voice
        )
    """

    _type = 8

    def __init__(
        self,
        *,
        custom_id: str,
        channel_types: list[int] | None = None,
        placeholder: str | None = None,
        min_values: int = 1,
        max_values: int = 1,
        disabled: bool = False,
        id: int | None = None,
    ):
        super().__init__(id=id)
        self._custom_id = custom_id
        self._channel_types = channel_types
        self._placeholder = placeholder
        self._min_values = min_values
        self._max_values = max_values
        self._disabled = disabled

    @property
    def custom_id(self) -> str:
        return self._custom_id

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data["custom_id"] = self._custom_id
        if self._channel_types is not None:
            data["channel_types"] = self._channel_types
        if self._placeholder is not None:
            data["placeholder"] = self._placeholder
        if self._min_values != 1:
            data["min_values"] = self._min_values
        if self._max_values != 1:
            data["max_values"] = self._max_values
        if self._disabled:
            data["disabled"] = True
        return data

    def __repr__(self) -> str:
        return f"<ChannelSelect custom_id='{self._custom_id}'>"
