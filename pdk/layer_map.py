from gdsfactory.technology import LayerMap


class TFTLayerMap(LayerMap):
    W_GATE = (1, 0)  # 10nm Tungsten gate
    AL2O3 = (2, 0)  # 15nm ALD Alumina gate dielectric
    NI_CONTACTS = (3, 0)  # 30nm Nickel source/drain
    ITO_CHANNEL = (4, 0)  # 3nm ITO semiconducting channel
    SIO2 = (998, 0)  # 300nm SiO2
    SI = (999, 0)  # Silicon substrate


LAYER = TFTLayerMap
