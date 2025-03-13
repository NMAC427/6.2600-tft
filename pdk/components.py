import gdsfactory as gf

from pdk.cross_section import metal_routing_ni, metal_routing_w
from pdk.layer_map import LAYER


@gf.cell
def resistor(
    length=100,
    width=20,
):
    layer = LAYER.W_GATE
    c = gf.Component()

    pad_size = (12, width)
    resistor = c << gf.components.resistance_meander(
        pad_size=pad_size,
        num_squares=length,
        width=2,
        res_layer=layer,
        pad_layer=layer,
    )

    v1 = c << via(pad_size)
    v2 = c << via(pad_size)

    v1.y = resistor.y
    v2.y = resistor.y
    v1.xmin = resistor.xmin
    v2.xmax = resistor.xmax

    c.add_port(
        "bot_e1",
        center=(resistor.xmin, resistor.y),
        orientation=180,
        width=width,
        layer=LAYER.W_GATE,
        port_type="electrical",
    )
    c.add_port(
        "bot_e2",
        center=(resistor.xmax, resistor.y),
        orientation=0,
        width=width,
        layer=LAYER.W_GATE,
        port_type="electrical",
    )

    c.add_port(
        "top_e1",
        center=(resistor.xmin, resistor.y),
        orientation=180,
        width=width,
        layer=LAYER.NI_CONTACTS,
        port_type="electrical",
    )
    c.add_port(
        "top_e2",
        center=(resistor.xmax, resistor.y),
        orientation=0,
        width=width,
        layer=LAYER.NI_CONTACTS,
        port_type="electrical",
    )

    return c


@gf.cell
def transistor(l_mesa=8.0, l_gate=2.0, l_overlap=2.0, w_mesa=12.0):
    """Creates an ITO-based transistor layout.

    Parameters:
        l_mesa (float): Total mesa length (ITO channel region).
        l_gate (float): Gate length.
        l_overlap (float): Overlap between gate and channel.
        w_mesa (float): Width of the channel.

    Returns:
        Component: gdsfactory layout for an ITO transistor.
    """

    l_sd = (l_mesa - l_gate) / 2 + 4
    w_contact = w_mesa + 4

    c = gf.Component()

    mesa = c << gf.components.rectangle((l_mesa, w_mesa), layer=LAYER.ITO_CHANNEL)

    gate = c << gf.components.rectangle(
        (l_gate + 2 * l_overlap, w_contact + 8), layer=LAYER.W_GATE
    )
    gate.move(gate.center, mesa.center)

    c.add_port("g1", port=gate.ports["e2"])
    c.add_port("g2", port=gate.ports["e4"])

    source = c << gf.components.rectangle((l_sd, w_contact), layer=LAYER.NI_CONTACTS)
    drain = c << gf.components.rectangle((l_sd, w_contact), layer=LAYER.NI_CONTACTS)

    source.move(source.center, mesa.center)
    source.movex(-(l_sd + l_gate) / 2)

    drain.move(drain.center, mesa.center)
    drain.movex((l_sd + l_gate) / 2)

    c.add_port("s", port=source.ports["e1"])
    c.add_port("d", port=drain.ports["e3"])

    return c


@gf.cell
def via(size=(20, 20), inset=2) -> gf.Component:
    c = gf.Component()
    t = c << gf.components.pad(size, layer=LAYER.NI_CONTACTS)
    v = c << gf.components.rectangle(
        (size[0] - 2 * inset, size[1] - 2 * inset), layer=LAYER.AL2O3
    )
    b = c << gf.components.pad(size, layer=LAYER.W_GATE)

    v.center = t.center
    b.center = t.center

    c.add_ports(t.ports, prefix="top_")
    c.add_ports(b.ports, prefix="bot_")

    return c


@gf.cell
def crossing_ni() -> gf.Component:
    """
        |
        :
    ==========
        :
        |
    """
    cross_width = 20
    spacing = 5

    c = gf.Component()

    bot = c << gf.components.straight(
        length=cross_width + 2 * spacing, cross_section=metal_routing_w
    )
    bot.rotate(90)
    # bot = c << gf.components.rectangle((cross_width, cross_width + 2*spacing), layer=LAYER.W_GATE)

    v1 = c << via(size=(cross_width, cross_width))
    v1.x = bot.x
    v1.ymin = bot.ymax

    v2 = c << via(size=(cross_width, cross_width))
    v2.x = bot.x
    v2.ymax = bot.ymin

    top = c << gf.components.straight(
        length=cross_width + 2 * spacing, cross_section=metal_routing_ni
    )
    top.center = bot.center

    c.add_port("e1", port=top.ports["e1"])
    c.add_port("e3", port=top.ports["e2"])
    c.add_port("e2", port=v1.ports["top_e2"])
    c.add_port("e4", port=v2.ports["top_e4"])

    # c.draw_ports()
    return c


@gf.cell
def straight(**kwargs) -> gf.Component:
    return gf.components.straight(**kwargs)
