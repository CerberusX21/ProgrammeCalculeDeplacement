class CalculTassements:
    """
    Calcule les tassements S1, S2 et S_total en pourcentage.
    S1 = (ef - e0*) / (1 + ef)
    S2 = (e0* - e) / (1 + ef)
    """

    def __init__(self, ef: float, e0_star: float, e_final: float):
        self.ef = ef
        self.e0_star = e0_star
        self.e_final = e_final

    def calculer(self):
        if self.ef + 1 == 0:
            raise ValueError("Division by zero is not allowed in the settlement calculation.")

        s1 = (self.ef - self.e0_star) / (1 + self.ef) * 100
        s2 = (self.e0_star - self.e_final) / (1 + self.ef) * 100
        s_total = s1 + s2

        return s1, s2, s_total
