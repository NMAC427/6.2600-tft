import gdsfactory as gf
import kfactory
from functools import partial
import itertools

import pdk.cross_section
from pdk import PDK
from pdk.components import *
from gdsfactory.cross_section import (
    port_names_electrical,
    port_types_electrical,
)

PDK.activate()


@gf.cell
def full_adder(
    l_mesa=50,
    l_gate=30,
    l_overlap=5,
    w_mesa=100,
    disabled=None,
    split_vdd=False,
):
    disabled = disabled or []

    grid_w = 175
    grid_h = 175
    wire_width = 50

    separation = 0
    h_separation = 5
    metal_routing_ni = partial(pdk.cross_section.metal_routing_ni, width=wire_width)
    metal_routing_w = partial(pdk.cross_section.metal_routing_w, width=wire_width)

    r_proto = resistor(length=5000, width=1.5 * grid_w)

    @gf.cell
    def _transistor(
        l_mesa: float,
        l_gate: float,
        l_overlap: float,
        w_mesa: float,
    ):
        c = gf.Component()
        t = c << transistor(
            l_mesa=l_mesa, l_gate=l_gate, l_overlap=l_overlap, w_mesa=w_mesa
        )
        t_height = t.bbox().width()
        t_width = t.bbox().height()

        if t_height < wire_width + 2 * h_separation:
            length = (wire_width + 2 * h_separation - t_height) / 2

            width1 = t.ports["s"].width
            width2 = max(width1, wire_width)
            s_s = c << gf.components.taper(
                length=length,
                width1=width1,
                width2=width2,
                cross_section=metal_routing_ni,
                port_names=port_names_electrical,
                port_types=port_types_electrical,
            )
            d_s = c << gf.components.taper(
                length=length,
                width1=width1,
                width2=width2,
                cross_section=metal_routing_ni,
                port_names=port_names_electrical,
                port_types=port_types_electrical,
            )

            s_s.connect("e1", t, "s", allow_width_mismatch=True)
            d_s.connect("e1", t, "d", allow_width_mismatch=True)
            c.add_port("s", port=s_s.ports["e2"])
            c.add_port("d", port=d_s.ports["e2"])
        else:
            c.add_port("s", port=t.ports["s"])
            c.add_port("d", port=t.ports["d"])

        if t_width < wire_width + 2 * h_separation:
            length = (wire_width + 2 * h_separation - t_width) / 2

            width1 = t.ports["g1"].width
            width2 = wire_width
            g1_s = c << gf.components.taper(
                length=length,
                width1=width1,
                width2=width2,
                cross_section=metal_routing_w,
                port_names=port_names_electrical,
                port_types=port_types_electrical,
            )
            g2_s = c << gf.components.taper(
                length=length,
                width1=width1,
                width2=width2,
                cross_section=metal_routing_w,
                port_names=port_names_electrical,
                port_types=port_types_electrical,
            )

            g1_s.connect("e1", t, "g1", allow_width_mismatch=True)
            g2_s.connect("e1", t, "g2", allow_width_mismatch=True)
            c.add_port("g1", port=g1_s.ports["e2"])
            c.add_port("g2", port=g2_s.ports["e2"])
        else:
            c.add_port("g1", port=t.ports["g1"])
            c.add_port("g2", port=t.ports["g2"])

        c.rotate(-90)
        return c

    t_proto = _transistor(l_mesa, l_gate, l_overlap, w_mesa)

    @gf.cell
    def without_ito(component):
        c = gf.Component(component.name + "_dis")
        c.kdb_cell.copy_tree(component.kdb_cell)
        c.add_ports(component.ports)
        c.remove_layers([LAYER.ITO_CHANNEL])
        return c

    def get_transistor(name: str):
        if name in disabled:
            return without_ito(t_proto)
        return t_proto

    def grid_pos(x, y):
        return (x * grid_w, y * grid_h)

    c = gf.Component()

    def route_ni(
        port_1,
        port_2,
        start_straight_length=separation,
        end_straight_length=separation,
        width=None,
        **kwargs,
    ):
        cross_section = metal_routing_ni
        if width is not None:
            cross_section = partial(cross_section, width=width)

        gf.routing.route_single(
            c,
            port_1,
            port_2,
            start_straight_length=start_straight_length,
            end_straight_length=end_straight_length,
            cross_section=cross_section,
            bend=gf.components.wire_corner,
            port_type="electrical",
            allow_width_mismatch=True,
            **kwargs,
        )

    def route_w(
        port_1,
        port_2,
        start_straight_length=separation,
        end_straight_length=separation,
        width=None,
        **kwargs,
    ):
        cross_section = metal_routing_w
        if width is not None:
            cross_section = partial(cross_section, width=width)

        gf.routing.route_single(
            c,
            port_1,
            port_2,
            start_straight_length=start_straight_length,
            end_straight_length=end_straight_length,
            cross_section=cross_section,
            bend=gf.components.wire_corner,
            port_type="electrical",
            allow_width_mismatch=True,
            **kwargs,
        )

    ############################
    # Inter Transistor Routing #
    ############################

    m_0 = c << get_transistor("m_0")
    m_0.center = grid_pos(1, 0)

    m_1 = c << get_transistor("m_1")
    m_1.center = grid_pos(0, -1)

    m_2 = c << get_transistor("m_2")
    m_2.center = grid_pos(1, -1)

    route_ni(m_0.ports["d"], m_2.ports["s"])
    route_ni(m_1.ports["s"], m_2.ports["s"])
    route_ni(m_1.ports["d"], m_2.ports["d"])

    m_3 = c << get_transistor("m_3")
    m_3.center = grid_pos(2, 0)

    m_4 = c << get_transistor("m_4")
    m_4.center = grid_pos(2, -1)

    route_ni(m_3.ports["d"], m_4.ports["s"])
    route_ni(m_3.ports["s"], m_0.ports["s"])
    route_ni(m_2.ports["d"], m_4.ports["d"])

    m_13 = c << get_transistor("m_13")
    m_13.center = grid_pos(3, 0)

    p_m_13_gnd = gf.Path(
        [
            m_13.ports["d"].center,
            (
                m_13.ports["d"].center[0],
                m_13.ports["d"].center[1] - wire_width / 2 - separation,
            ),
            (
                m_13.ports["d"].center[0] - grid_w / 2,
                m_13.ports["d"].center[1] - wire_width / 2 - separation,
            ),
            (
                m_13.ports["d"].center[0] - grid_w / 2,
                m_13.ports["d"].center[1] - grid_h - wire_width - separation,
            ),
        ]
    )

    c << gf.path.extrude(p_m_13_gnd, metal_routing_ni)

    route_ni(m_3.ports["s"], m_0.ports["s"])

    v_0 = c << via((wire_width, wire_width))
    v_0.connect("top_e4", m_3, "s", allow_width_mismatch=True)
    v_0.y += separation
    v_0.x += grid_w / 2
    route_ni(v_0.ports["top_e1"], m_3.ports["s"])
    route_w(
        v_0.ports["bot_e4"],
        m_13.ports["g2"],
        start_straight_length=0,
        end_straight_length=0,
    )

    m_5 = c << get_transistor("m_5")
    m_5.center = grid_pos(4, 0)

    route_w(
        v_0.ports["bot_e3"],
        m_5.ports["g2"],
        start_straight_length=grid_w - wire_width,
        end_straight_length=0,
    )

    m_6 = c << get_transistor("m_6")
    m_6.center = grid_pos(3, -1)

    m_7 = c << get_transistor("m_7")
    m_7.center = grid_pos(4, -1)

    m_8 = c << get_transistor("m_8")
    m_8.center = grid_pos(5, -1)

    route_ni(m_5.ports["d"], m_7.ports["s"])
    route_ni(m_6.ports["s"], m_7.ports["s"])
    route_ni(m_7.ports["s"], m_8.ports["s"])

    route_ni(m_4.ports["d"], m_6.ports["d"])
    route_ni(m_6.ports["d"], m_7.ports["d"])
    route_ni(m_7.ports["d"], m_8.ports["d"])

    m_9 = c << get_transistor("m_9")
    m_9.center = grid_pos(5, 0)

    route_ni(m_5.ports["s"], m_9.ports["s"])

    m_12 = c << get_transistor("m_12")
    m_12.center = grid_pos(6.5, 0.5)
    m_12.ymin = m_9.ymax + wire_width + separation + h_separation

    v_1 = c << via((wire_width, wire_width))
    v_1.connect("bot_e3", m_12, "g2", allow_width_mismatch=True)
    v_1.x -= 10
    route_ni(v_1.ports["top_e1"], m_9.ports["s"])
    route_w(v_1.ports["bot_e3"], m_12.ports["g2"])

    m_10 = c << get_transistor("m_10")
    m_10.center = grid_pos(6, 0)

    route_w(m_10.ports["g2"], m_8.ports["g1"], start_straight_length=h_separation)

    wp_m_9_m_10 = c << gf.components.rectangle(
        (wire_width, m_10.bbox().height()),
        port_orientations=(90, -90),
        layer=LAYER.NI_CONTACTS,
    )

    wp_m_9_m_10.center = grid_pos(5.5, 0)
    wp_m_9_m_10.xmin = m_9.xmax + h_separation

    route_ni(m_9.ports["d"], wp_m_9_m_10.ports["e2"])
    route_ni(wp_m_9_m_10.ports["e1"], m_10.ports["s"])

    m_11 = c << get_transistor("m_11")
    m_11.center = grid_pos(6, -1)

    route_ni(m_10.ports["d"], m_11.ports["s"])
    route_ni(m_8.ports["d"], m_11.ports["d"])

    route_ni(m_11.ports["d"], m_12.ports["d"])

    #################
    # Input Routing #
    #################

    a_in = c << via((100, 100))
    b_in = c << via((100, 100))
    c_in = c << via((100, 100))

    a_in.center = grid_pos(-0.5, -0.5)
    a_in.x -= a_in.bbox().width() / 2 + 2 * h_separation

    b_in.center = a_in.center
    b_in.y -= 200
    c_in.center = a_in.center
    c_in.y += 200

    route_w(m_1.ports["g2"], a_in.ports["bot_e4"])
    route_w(m_3.ports["g2"], a_in.ports["bot_e3"])
    route_w(m_6.ports["g1"], a_in.ports["bot_e3"])
    route_w(m_9.ports["g2"], a_in.ports["bot_e3"])

    route_w(m_2.ports["g1"], b_in.ports["bot_e3"])
    route_w(m_2.ports["g1"], m_4.ports["g2"])
    route_w(m_7.ports["g1"], b_in.ports["bot_e3"])
    route_w(m_11.ports["g1"], b_in.ports["bot_e3"])

    route_w(m_0.ports["g2"], c_in.ports["bot_e3"])
    route_w(m_10.ports["g2"], c_in.ports["bot_e3"], start_straight_length=h_separation)

    #############
    # Resistors #
    #############

    r_0 = c << r_proto
    r_0.rotate(-90)
    r_0.center = grid_pos(0, 0)
    r_0.ymin = c_in.ymax + 20

    r_1 = c << r_proto
    r_1.rotate(-90)
    r_1.center = grid_pos(4, 0)
    r_1.y = r_0.y

    r_2 = c << r_proto
    r_2.rotate(-90)
    r_2.center = grid_pos(6, 0)
    r_2.y = r_0.y

    r_3 = c << r_proto
    r_3.rotate(-90)
    r_3.center = grid_pos(2, 0)
    r_3.y = r_0.y

    route_ni(r_0.ports["top_e2"], m_0.ports["s"])
    route_ni(r_1.ports["top_e2"], m_5.ports["s"])
    route_ni(r_3.ports["top_e2"], m_13.ports["s"])

    if r_2.ymin < m_12.ymax + wire_width + 2 * separation:
        r_2.ymin = m_12.ymax + wire_width + 2 * separation
        route_ni(r_2.ports["top_e2"], m_12.ports["s"])
    else:
        route_m_12_r_2 = c << gf.components.straight(
            length=r_2.ymin - m_12.ports["s"].y, cross_section=metal_routing_ni
        )
        route_m_12_r_2.rotate(-90)
        route_m_12_r_2.connect("e1", m_12, "s", allow_width_mismatch=True)

    if not split_vdd:
        route_ni(r_0.ports["top_e1"], r_3.ports["top_e1"])
        route_ni(r_3.ports["top_e1"], r_1.ports["top_e1"])
        route_ni(r_1.ports["top_e1"], r_2.ports["top_e1"])

    #############
    # VDD / GND #
    #############

    if split_vdd:
        for res in [r_0, r_1, r_2, r_3]:
            vdd = c << gf.components.pad((100, 100), layer=LAYER.NI_CONTACTS)
            vdd.connect("e4", res, "top_e1", allow_width_mismatch=True)

    else:
        vdd = c << gf.components.pad((100, 100), layer=LAYER.NI_CONTACTS)

        vdd.center = grid_pos(7, 1.5)
        vdd.x += 20
        route_ni(vdd.ports["e2"], r_2.ports["top_e1"])

    gnd = c << gf.components.pad((100, 100), layer=LAYER.NI_CONTACTS)

    gnd.center = grid_pos(3, 0)
    gnd.ymax = b_in.y - wire_width / 2 - h_separation
    route_ni(gnd.ports["e2"], m_6.ports["d"])

    ###########
    # Outputs #
    ###########

    s_out = c << gf.components.pad((100, 100), layer=LAYER.NI_CONTACTS)
    c_out = c << via((100, 100))

    s_out.center = grid_pos(7, 0)
    s_out.x += 20
    route_ni(s_out.ports["e2"], m_12.ports["s"])

    c_out.center = grid_pos(3, 1)
    c_out.ymin = r_3.ymax + wire_width + separation + h_separation

    s_c_out_w = c << gf.components.straight(
        length=wire_width + 2 * h_separation, cross_section=metal_routing_w
    )
    s_c_out_w.connect("e1", c_out, "bot_e4", allow_width_mismatch=True)

    v_2 = c << via((wire_width, wire_width))
    v_2.connect("bot_e2", s_c_out_w, "e2")

    route_ni(v_2.ports["top_e4"], m_13.ports["s"])

    ### Quick Design Check

    if (
        (grid_h - m_0.bbox().height() - 2 * separation) < 2 * wire_width + h_separation
    ) or (
        (grid_w - m_0.bbox().width() - 2 * separation) < wire_width + 2 * h_separation
    ):
        old_c = c
        c = gf.Component()
        boundary = c << gf.components.rectangle(
            (old_c.bbox().width(), old_c.bbox().height()), layer=LAYER.SI
        )
        boundary.center = old_c.center

    ########
    # Text #
    ########

    for layer in [LAYER.W_GATE, LAYER.AL2O3, LAYER.NI_CONTACTS]:
        text = c << gf.components.text(
            text=f"Lm {l_mesa}\n"
            + f"Lg {l_gate}\n"
            + f"Ov {l_overlap}\n"
            + f"Wm {w_mesa}\n"
            + f"D {' '.join(disabled).replace('_', '')}\n",
            size=15,
            layer=layer,
        )

        text.xmin = s_out.xmin
        text.ymax = s_out.ymin - 20

    return c


def main():
    c = gf.Component()

    t_variants = itertools.product(
        [2, 5, 10, 20],  # l_ov
        [5, 10, 20, 30],  # l_g
        [10, 20, 50, 100],  # w
    )

    t_variants = [(l_ov * 2 + l_g - 1, l_g, l_ov, w) for l_ov, l_g, w in t_variants]

    full_adders = [
        full_adder(l_mesa, l_gate, l_overlap, w_mesa)
        for (l_mesa, l_gate, l_overlap, w_mesa) in t_variants
    ]

    c << gf.grid(gf.pack(full_adders, spacing=50))

    # c << full_adder(
    #     l_mesa=70,
    #     l_overlap=30,
    #     disabled=["m_0", "m_1"],
    #     split_vdd=True
    # )

    c.show()
    c.write_gds("full_adder.gds")


if __name__ == "__main__":
    main()
