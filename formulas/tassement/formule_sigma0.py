import math

class CalculSigma0:
    """
    Calcule la contrainte efficace initiale σ′₀ (en kPa), en fonction de e₀*, du type de sol, et de sa valeur.
    - pour IP : max 50 kPa,
    - pour IR : entre 1 et 50 kPa.
    """

    def __init__(self, e0_star: float, type_sol: str, valeur_sol: float, etat_sol: int):
        self.e0_star = e0_star
        self.type_sol = type_sol.strip()
        self.valeur = valeur_sol
        self.etat_sol = etat_sol

    def calculer(self) -> float:
        # Calcul brut selon type de sol
        if self.type_sol == "Liquid limit":
            if self.etat_sol == 0:  # Ice-Rich
                sigma0 = 0.0081 * self.valeur + 0.019
            else:  # Ice-Poor
                sigma0 = 0.0033 * self.valeur + 0.037

        elif self.type_sol == "Clay content":
            if self.etat_sol == 0:  # Ice-Rich
                sigma0 = 0.0081 * self.valeur + 0.019
            else:  # Ice-Poor
                sigma0 = 0.0033 * self.valeur + 0.037

        elif self.type_sol == "Fine fraction median diameter":
            if self.valeur <= 0:
                raise ValueError("Fine fraction median diameter must be greater than zero for the log.")
            if self.etat_sol == 0:  # Ice-Rich
                sigma0 = -0.017 * math.log10(self.valeur) + 0.0175
            else:  # Ice-Poor
                sigma0 = -0.007 * math.log10(self.valeur) + 0.0075

        else:
            raise ValueError("Soil type is invalid. Expected: Liquid limit, Clay content or Fine fraction median diameter.")

        # --- Application des seuils selon l'état du sol ---
        if self.etat_sol == 1:  # Ice-Poor
            sigma0 = max(1, min(50, sigma0))

        elif self.etat_sol == 0:  # Ice-Rich
            sigma0 = max(1, min(50, sigma0))

        return sigma0
