import gdsfactory as gf
import numpy as np

from pdk.cross_section import metal_routing_ni, metal_routing_w
from pdk.layer_map import LAYER


@gf.cell
def resistance_meander(
    pad_size=(50.0, 50.0),
    num_squares: int = 1000,
    width: float = 1.0,
    res_layer="MTOP",
    pad_layer="MTOP",
) -> gf.Component:
    """Return meander to test resistance.

    based on phidl.geometry

    Args:
        pad_size: Size of the two matched impedance pads (microns).
        num_squares: Number of squares comprising the resonator wire.
        width: The width of the squares (microns).
        res_layer: resistance layer.
        pad_layer: pad layer.
    """
    x = pad_size[0]
    z = pad_size[1]

    # Checking validity of input
    if x <= 0 or z <= 0:
        raise ValueError("Pad must have positive, real dimensions")
    elif width > z:
        raise ValueError("Width of cell cannot be greater than height of pad")
    elif num_squares <= 0:
        raise ValueError("Number of squares must be a positive real number")
    elif width <= 0:
        raise ValueError("Width of cell must be a positive real number")

    # Performing preliminary calculations
    num_rows = int(np.floor(z / (2 * width)))
    if num_rows % 2 == 0:
        num_rows -= 1
    num_columns = num_rows - 1
    squares_in_row = (num_squares - num_columns - 2) / num_rows

    # Compensating for weird edge cases
    if squares_in_row < 1:
        num_rows = round(num_rows / 2) - 2
        squares_in_row = 1
    if width * 2 > z:
        num_rows = 1
        squares_in_row = num_squares - 2

    length_row = squares_in_row * width

    # Creating row/column corner combination structure
    T = gf.Component()
    Row = gf.c.rectangle(size=(length_row, width), layer=res_layer)
    Col = gf.c.rectangle(size=(width, width), layer=res_layer)

    T.add_ref(Row)
    col = T.add_ref(Col)
    col.dmove((length_row - width, -width))

    # Creating entire straight net
    N = gf.Component()
    n = 1
    for i in range(num_rows):
        d = N.add_ref(T) if i != num_rows - 1 else N.add_ref(Row)
        if n % 2 == 0:
            d.dmirror_x(d.dx)
        d.dmovey(-(n - 1) * T.dysize)
        n += 1
    ref = N.add_ref(Col)
    ref.dmovex(-width)

    end = N.add_ref(Col)
    end.dmovey(-(n - 2) * T.dysize)
    end.dmovex(length_row)

    # Creating pads
    P = gf.Component()
    pad = gf.c.rectangle(size=(x, z), layer=pad_layer)
    pad1 = P.add_ref(pad)
    pad1.dmovex(-x - width)
    pad2 = P.add_ref(pad)
    pad2.dmovex(length_row + width)
    net = P.add_ref(N)
    net.dymin = pad1.dymin
    P.flatten()
    return P


@gf.cell
def resistor(
    length=100,
    width=20,
):
    layer = LAYER.W_GATE
    c = gf.Component()

    pad_size = (12, width)
    resistor = c << resistance_meander(
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

    c.flatten()
    return c


@gf.cell
def resistor_ito(length=1, width=20):
    c = gf.Component()

    if length * 3 < width or length <= 10:
        offset = 6
        trace_width = 2 if length >= 10 else 5
        pad_size = (12, width)

        r_size = (length * trace_width + 2 * offset, trace_width)
        resistor = c << gf.components.compass(r_size, layer=LAYER.ITO_CHANNEL)
    else:
        offset = 6
        pad_size = (12, width)
        resistor = c << resistance_meander(
            pad_size=(4, width),
            num_squares=length,
            width=5,
            res_layer=LAYER.ITO_CHANNEL,
            pad_layer=LAYER.ITO_CHANNEL,
        )

    print(length, width, pad_size)
    v1 = c << via(pad_size)
    v2 = c << via(pad_size)

    v1.y = resistor.y
    v2.y = resistor.y
    v1.xmax = resistor.xmin + offset
    v2.xmin = resistor.xmax - offset

    port_width = pad_size[1]

    c.add_port(
        "bot_e1",
        center=(c.xmin, c.y),
        orientation=180,
        width=port_width,
        layer=LAYER.W_GATE,
        port_type="electrical",
    )
    c.add_port(
        "bot_e2",
        center=(c.xmax, c.y),
        orientation=0,
        width=port_width,
        layer=LAYER.W_GATE,
        port_type="electrical",
    )

    c.add_port(
        "top_e1",
        center=(c.xmin, c.y),
        orientation=180,
        width=port_width,
        layer=LAYER.NI_CONTACTS,
        port_type="electrical",
    )
    c.add_port(
        "top_e2",
        center=(c.xmax, c.y),
        orientation=0,
        width=port_width,
        layer=LAYER.NI_CONTACTS,
        port_type="electrical",
    )

    c.flatten()
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

    return c


@gf.cell
def straight(**kwargs) -> gf.Component:
    return gf.components.straight(**kwargs)
