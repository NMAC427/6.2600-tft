from gdsfactory.technology import LayerStack, LayerLevel
from pdk.layer_map import LAYER

layer_stack = LayerStack(
    layers={
        "SI": LayerLevel(layer=LAYER.SI, thickness=500, zmin=0, material="Si"),
        "SIO2": LayerLevel(layer=LAYER.SIO2, thickness=0.3, zmin=0, material="SiO2"),
        "W_GATE": LayerLevel(
            layer=LAYER.W_GATE, thickness=0.01, zmin=0.3, material="W"
        ),
        "AL2O3": LayerLevel(
            layer=LAYER.AL2O3, thickness=0.015, zmin=0.31, material="Al2O3"
        ),
        "ITO_CHANNEL": LayerLevel(
            layer=LAYER.ITO_CHANNEL, thickness=0.003, zmin=0.325, material="ITO"
        ),
        "NI_CONTACTS": LayerLevel(
            layer=LAYER.NI_CONTACTS, thickness=0.03, zmin=0.328, material="Ni"
        ),
    }
)
