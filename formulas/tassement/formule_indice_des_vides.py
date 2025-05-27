import math

class CalculIndiceDesVides:
    """
    Calcule l'indice des vides (e)
    """

    def __init__(self, e0_star: float, cc_star: float, sigma_v: float, sigma0: float):
        self.e0_star = e0_star
        self.cc_star = cc_star
        self.sigma_v = sigma_v
        self.sigma0 = sigma0

    def calculer(self) -> float:
        if self.sigma_v <= 0:
            raise ValueError("The vertical stress σ′ᵥ must be strictly positive.")
        if self.sigma0 <= 0:
            raise ValueError("The initial stress σ′₀ must be strictly positive.")

        ratio = self.sigma_v / self.sigma0
        return self.e0_star - self.cc_star * math.log10(ratio)
