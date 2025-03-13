import gdsfactory as gf
from functools import partial

import pdk.cross_section
from pdk import PDK
from pdk.components import *

PDK.activate()


def main():

    separation = 5  # 0
    h_separation = 5
    wire_width = 50
    metal_routing_ni = partial(pdk.cross_section.metal_routing_ni, width=wire_width)
    metal_routing_w = partial(pdk.cross_section.metal_routing_w, width=wire_width)

    grid_w = 200  # 170
    grid_h = 200  # 165

    def grid_pos(x, y):
        return (x * grid_w, y * grid_h)

    t_proto = transistor(l_mesa=50, l_gate=30, l_overlap=5, w_mesa=100)
    r_proto = resistor(length=5000, width=grid_w * 1.5)

    # PLAN: Define a grid on which to place components.

    c = gf.Component()

    def route_ni(
        port_1,
        port_2,
        start_straight_length=separation,
        end_straight_length=separation,
        **kwargs
    ):
        gf.routing.route_single(
            c,
            port_1,
            port_2,
            start_straight_length=start_straight_length,
            end_straight_length=end_straight_length,
            cross_section=metal_routing_ni,
            bend=gf.components.wire_corner,
            port_type="electrical",
            allow_width_mismatch=True,
            **kwargs
        )

    def route_w(
        port_1,
        port_2,
        start_straight_length=separation,
        end_straight_length=separation,
        **kwargs
    ):
        gf.routing.route_single(
            c,
            port_1,
            port_2,
            start_straight_length=start_straight_length,
            end_straight_length=end_straight_length,
            cross_section=metal_routing_w,
            bend=gf.components.wire_corner,
            port_type="electrical",
            allow_width_mismatch=True,
            **kwargs
        )

    # vdd = c << gf.components.pad(layer=LAYER.NI_CONTACTS)
    # gnd = c << gf.components.pad(layer=LAYER.NI_CONTACTS)

    # gnd.center = vdd.center
    # gnd.y -= 1000

    # a_in = c << gf.components.pad(layer=LAYER.NI_CONTACTS)
    # b_in = c << gf.components.pad(layer=LAYER.NI_CONTACTS)
    # c_in = c << gf.components.pad(layer=LAYER.NI_CONTACTS)

    # a_in.y -= 150
    # b_in.y -= 300
    # c_in.y -= 450

    # r_0 = c << r_proto
    # r_0.rotate(-90)

    m_0 = c << t_proto
    m_0.rotate(-90)
    m_0.center = grid_pos(1, 0)

    m_1 = c << t_proto
    m_1.rotate(-90)
    m_1.center = grid_pos(0, -1)

    m_2 = c << t_proto
    m_2.rotate(-90)
    m_2.center = grid_pos(1, -1)

    route_ni(m_0.ports["d"], m_2.ports["s"])
    route_ni(m_1.ports["s"], m_2.ports["s"])
    route_ni(m_1.ports["d"], m_2.ports["d"])

    m_3 = c << t_proto
    m_3.rotate(-90)
    m_3.center = grid_pos(2, 0)

    m_4 = c << t_proto
    m_4.rotate(-90)
    m_4.center = grid_pos(2, -1)

    route_ni(m_3.ports["d"], m_4.ports["s"])
    route_ni(m_3.ports["s"], m_0.ports["s"])
    route_ni(m_2.ports["d"], m_4.ports["d"])

    m_13 = c << t_proto
    m_13.rotate(-90)
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
                m_13.ports["d"].center[1] - grid_h - wire_width,
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
    route_w(v_0.ports["bot_e4"], m_13.ports["g2"])

    m_5 = c << t_proto
    m_5.rotate(-90)
    m_5.center = grid_pos(4, 0)

    route_w(
        v_0.ports["bot_e3"], m_5.ports["g2"], start_straight_length=grid_w - wire_width
    )

    m_6 = c << t_proto
    m_6.rotate(-90)
    m_6.center = grid_pos(3, -1)

    m_7 = c << t_proto
    m_7.rotate(-90)
    m_7.center = grid_pos(4, -1)

    m_8 = c << t_proto
    m_8.rotate(-90)
    m_8.center = grid_pos(5, -1)

    route_ni(m_5.ports["d"], m_7.ports["s"])
    route_ni(m_6.ports["s"], m_7.ports["s"])
    route_ni(m_7.ports["s"], m_8.ports["s"])

    route_ni(m_4.ports["d"], m_6.ports["d"])
    route_ni(m_6.ports["d"], m_7.ports["d"])
    route_ni(m_7.ports["d"], m_8.ports["d"])

    m_9 = c << t_proto
    m_9.rotate(-90)
    m_9.center = grid_pos(5, 0)

    route_ni(m_5.ports["s"], m_9.ports["s"])

    m_12 = c << t_proto
    m_12.rotate(-90)
    m_12.center = grid_pos(6, 1)

    v_1 = c << via((wire_width, wire_width))
    v_1.connect("bot_e3", m_12, "g2", allow_width_mismatch=True)
    v_1.x -= 10
    route_ni(v_1.ports["top_e1"], m_9.ports["s"])
    route_w(v_1.ports["bot_e3"], m_12.ports["g2"])

    wp_m_12_gnd = c << gf.components.rectangle(
        (wire_width, wire_width),
        port_orientations=(180, -90),
        layer=LAYER.NI_CONTACTS,
    )
    wp_m_12_gnd.xmin = m_12.xmax + h_separation
    wp_m_12_gnd.ymax = m_12.ymin - separation
    route_ni(m_12.ports["d"], wp_m_12_gnd.ports["e1"])

    m_10 = c << t_proto
    m_10.rotate(-90)
    m_10.center = grid_pos(6, 0)

    route_w(m_8.ports["g1"], m_10.ports["g2"], start_straight_length=h_separation)

    wp_m_9_m_10 = c << gf.components.rectangle(
        (wire_width, m_10.bbox().height()),
        port_orientations=(90, -90),
        layer=LAYER.NI_CONTACTS,
    )

    wp_m_9_m_10.center = grid_pos(5.5, 0)
    wp_m_9_m_10.xmax = m_10.xmin - h_separation

    route_ni(m_9.ports["d"], wp_m_9_m_10.ports["e2"])
    route_ni(wp_m_9_m_10.ports["e1"], m_10.ports["s"])

    m_11 = c << t_proto
    m_11.rotate(-90)
    m_11.center = grid_pos(6, -1)

    route_ni(m_10.ports["d"], m_11.ports["s"])
    route_ni(m_8.ports["d"], m_11.ports["d"])

    p_m_12_gnd = gf.Path(
        [
            wp_m_12_gnd.ports["e2"].center,
            (
                wp_m_12_gnd.ports["e2"].center[0],
                m_11.ports["d"].center[1] - wire_width / 2 - separation,
            ),
            (
                m_11.ports["d"].center[0],
                m_11.ports["d"].center[1] - wire_width / 2 - separation,
            ),
        ]
    )

    c << gf.path.extrude(p_m_12_gnd, metal_routing_ni)

    # cross = c << crossing_ni()
    # cross.center = (500, 0)

    c.plot()

    # r_0.connect("top_p1", m_0.ports["s"], allow_width_mismatch=True)

    # v_r0vdd = c << via((22, 22))
    # v_r0vdd.movey(150)
    # r_0.connect("p1", v_r0vdd.ports["be1"], allow_width_mismatch=True)

    # ref1 = c.add_ref(resistor(length=100, width=50))
    #
    # ref2 = c.add_ref(
    #     transistor(
    #         l_mesa=50,
    #         l_gate=20,
    #         l_overlap=10,
    #         w_mesa=20,
    #     )
    # )
    #
    # ref2.movex(100)
    #
    # ref3 = c.add_ref(
    #     transistor(
    #         l_mesa=50,
    #         l_gate=20,
    #         l_overlap=10,
    #         w_mesa=20,
    #     )
    # )
    #
    # ref3.movex(100)
    # ref3.movey(200)

    #
    # print(r)
    #
    # gf.routing.route_astar(
    #     component=c,
    #     port1=ref1.ports["p2"],
    #     port2=ref2.ports["g1"],
    #     cross_section=partial(gf.cross_section.strip, width=1, layer=LAYER.W_GATE, port_types=("electrical","electrical")),
    #     resolution=1,
    #     distance=10,
    #     avoid_layers=(LAYER.W_GATE, LAYER.NI_CONTACTS),
    #     bend=gf.components.wire_corner,
    # )

    c.show()
    c.plot()

    c.write_gds("ito_transistor_test.gds")


if __name__ == "__main__":
    main()
