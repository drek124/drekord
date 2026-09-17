"""LayoutView — the root container for Components V2 messages.

A LayoutView holds a list of top-level components and serializes them
into the ``components`` array of a Discord message payload. It also
auto-sets the ``IS_COMPONENTS_V2`` flag (``1 << 15 = 32768``).
"""

from __future__ import annotations

from typing import Any

from .components import Component

# Discord Components V2 flag
IS_COMPONENTS_V2 = 32768

# Maximum total components (including nested) in a LayoutView
_MAX_COMPONENTS = 40


class LayoutView:
    """Root container for a Components V2 message.

    Usage::

        view = LayoutView()
        view.add_item(TextDisplay("Hello!"))
        view.add_item(Container(
            TextDisplay("Inside a container"),
            Separator(),
            accent_color=0x5865F2,
        ))

        await client.messages.channel(ch).send(view=view)

    You can also pass components directly to the constructor::

        view = LayoutView(
            TextDisplay("Hello!"),
            Separator(),
        )
    """

    def __init__(self, *components: Component):
        self._items: list[Component] = list(components)

    def add_item(self, component: Component) -> LayoutView:
        """Add a top-level component to this view.

        Returns ``self`` for chaining.
        """
        self._items.append(component)
        return self

    def remove_item(self, index: int) -> LayoutView:
        """Remove a top-level component by index.

        Returns ``self`` for chaining.
        """
        if 0 <= index < len(self._items):
            self._items.pop(index)
        return self

    def clear_items(self) -> LayoutView:
        """Remove all top-level components.

        Returns ``self`` for chaining.
        """
        self._items.clear()
        return self

    @property
    def items(self) -> list[Component]:
        """Return the list of top-level components."""
        return list(self._items)

    def _count_components(self) -> int:
        """Recursively count all components (including nested ones)."""
        total = 0
        for item in self._items:
            total += 1
            # Count children of parent components
            if hasattr(item, "_children"):
                total += len(item._children)
                for child in item._children:
                    if hasattr(child, "_children"):
                        total += len(child._children)
                    if hasattr(child, "accessory") and child.accessory is not None:
                        total += 1
            if hasattr(item, "_components"):
                total += len(item._components)
            if hasattr(item, "_items"):
                total += len(item._items)
        return total

    def to_payload(self) -> dict[str, Any]:
        """Serialize the view into a message payload dict.

        Returns a dict with ``flags`` and ``components`` keys, ready to
        merge into a ``send()`` call.
        """
        count = self._count_components()
        if count > _MAX_COMPONENTS:
            raise ValueError(
                f"LayoutView exceeds the {_MAX_COMPONENTS} component limit "
                f"(found {count}). Reduce the number of components."
            )

        return {
            "flags": IS_COMPONENTS_V2,
            "components": [item.to_dict() for item in self._items],
        }

    def __repr__(self) -> str:
        return f"<LayoutView items={len(self._items)}>"
