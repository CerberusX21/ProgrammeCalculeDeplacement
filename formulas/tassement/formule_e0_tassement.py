import math

class CalculE0Tassement:
    """
    Classe pour calculer e0* selon l’état du sol (0 = IR, 1 = IP), en utilisant ei* et Cc*.
    """

    def __init__(self, ei_star: float, cc_star: float, etat_sol: int):
        self.ei_star = ei_star
        self.cc_star = cc_star
        self.etat = etat_sol  # 0 = Ice-Rich, 1 = Ice-Poor

    def calculer(self) -> float:
        if self.etat == 1:  # Ice-Poor
            return self.ei_star

        elif self.etat == 0:  # Ice-Rich
            exponent = (self.cc_star - 0.22) / 0.74
            
            return 10 ** exponent

        else:
            raise ValueError("État du sol non reconnu :  Ice-Rich ou Ice-Poor attendu.")
