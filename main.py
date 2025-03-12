import gdsfactory as gf
from functools import partial

from pdk import PDK
from pdk.components import *

PDK.activate()


def main():

    c = gf.Component()
    PDK.activate()
    ref1 = c.add_ref(resistor(length=100, width=50))

    ref2 = c.add_ref(
        transistor(
            l_mesa=50,
            l_gate=20,
            l_overlap=10,
            w_mesa=20,
        )
    )

    ref2.movex(100)

    ref3 = c.add_ref(
        transistor(
            l_mesa=50,
            l_gate=20,
            l_overlap=10,
            w_mesa=20,
        )
    )

    ref3.movex(100)
    ref3.movey(200)

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
