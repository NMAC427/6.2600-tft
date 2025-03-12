from gdsfactory.technology import LayerMap


class TFTLayerMap(LayerMap):
    SI = (0, 0)  # Silicon substrate
    SIO2 = (1, 0)  # 300nm SiO2
    W_GATE = (2, 0)  # 10nm Tungsten gate
    AL2O3 = (3, 0)  # 15nm ALD Alumina gate dielectric
    ITO_CHANNEL = (4, 0)  # 3nm ITO semiconducting channel
    NI_CONTACTS = (5, 0)  # 30nm Nickel source/drain


LAYER = TFTLayerMap
