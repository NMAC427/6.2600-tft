import gdsfactory as gf
from pdk.layer_map import LAYER


@gf.cell
def resistor(
        length=100,
        width=20
):
    layer = LAYER.W_GATE
    c = gf.Component()

    resistor = c << gf.components.resistance_meander(
        pad_size=(10, width),
        num_squares=length,
        width=2,
        res_layer=layer,
        pad_layer=layer,
    )

    c.add_port("p1", center=(resistor.xmin, resistor.y), orientation=180, width=width, layer=layer, port_type="electrical")
    c.add_port("p2", center=(resistor.xmax, resistor.y), orientation=0, width=width, layer=layer, port_type="electrical")

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

    c = gf.Component("ito_transistor")

    mesa = c << gf.components.rectangle((l_mesa, w_mesa), layer=LAYER.ITO_CHANNEL)

    gate = c << gf.components.rectangle((l_gate + 2 * l_overlap, w_contact + 8), layer=LAYER.W_GATE)
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
def straight(**kwargs) -> gf.Component:
    return gf.components.straight(**kwargs)