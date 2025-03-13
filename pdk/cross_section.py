from gdsfactory import typings
from gdsfactory.component import Component
from gdsfactory.config import CONF, ErrorType
from gdsfactory.cross_section import (
    CrossSection,
    cross_section,
    xsection,
    port_names_electrical,
    port_types_electrical,
)


def metal_routing_w(
    width: float = 50,
    layer: typings.LayerSpec = "W_GATE",
    radius: float | None = None,
    port_names: typings.IOPorts = port_names_electrical,
    port_types: typings.IOPorts = port_types_electrical,
    **kwargs,
) -> CrossSection:
    """Return Metal Strip cross_section."""
    return cross_section(
        width=width,
        layer=layer,
        radius=radius,
        port_names=port_names,
        port_types=port_types,
        **kwargs,
    )


def metal_routing_ni(
    width: float = 50,
    layer: typings.LayerSpec = "NI_CONTACTS",
    radius: float | None = None,
    port_names: typings.IOPorts = port_names_electrical,
    port_types: typings.IOPorts = port_types_electrical,
    **kwargs,
) -> CrossSection:
    """Return Metal Strip cross_section."""
    return cross_section(
        width=width,
        layer=layer,
        radius=radius,
        port_names=port_names,
        port_types=port_types,
        **kwargs,
    )
