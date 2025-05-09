import gdsfactory as gf
from gdsfactory.get_factories import get_cells
from gdsfactory.technology import LayerViews

from pdk import components, cross_section
from pdk.layer_map import LAYER
from pdk.layer_stack import layer_stack

# from components import tungsten_gate, ito_channel, nickel_contacts

layer_views = LayerViews.from_lyp("pdk/layer_views.lyp")


PDK = gf.Pdk(
    name="tft_pdk",
    layers=LAYER,
    layer_stack=layer_stack,
    layer_views=layer_views,
    cross_sections={},
    cells=get_cells(components),
)
