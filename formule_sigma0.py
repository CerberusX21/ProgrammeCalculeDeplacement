import math

class CalculSigma0:
    """
    Calcule la contrainte efficace initiale σ′₀ (en kPa), en fonction de e₀*, du type de sol, et de sa valeur.
    Vérifie les seuils selon l’état du sol (IR/IP).
    """

    def __init__(self, e0_star: float, type_sol: str, valeur_sol: float, etat_sol: int):
        self.e0_star = e0_star
        self.type_sol = type_sol.strip()
        self.valeur = valeur_sol
        self.etat_sol = etat_sol

    def calculer(self) -> float: #si le type de sol est wL on applique la formule σ′=e^((e0*-0.014*valeur-0.42)/(-0.0014*valeur-0.012))
        if self.type_sol == "wL":
            num = self.e0_star - 0.014 * self.valeur - 0.42
            denom = -0.0014 * self.valeur - 0.012
            sigma0 = math.exp(num / denom)

        elif self.type_sol == "clay%":
            num = self.e0_star - 0.0049 * self.valeur - 0.82 #si le type de sol est clay% on applique la formule σ′=e^((e0*-0.0049*valeur-0.82)/(-0.00063*valeur-0.060))
            denom = -0.00063 * self.valeur - 0.060
            sigma0 = math.exp(num / denom)

        elif self.type_sol == "d50ff":  # si le type de sol est d50ff on applique la formule σ′=e^((e0*+0.25*log(d50ff)-0.45)/(0.020*log(d50ff)-0.060))
            if self.valeur <= 0:
                raise ValueError("d50ff doit être supérieur à zéro pour le log.")
            log_d50 = math.log(self.valeur)
            num = self.e0_star + 0.25 * log_d50 - 0.45
            denom = 0.020 * log_d50 - 0.060
            sigma0 = math.exp(num / denom)

        else:
            raise ValueError("Type de sol invalide. Attendu : wL, clay% ou d50ff.")

        # --- Vérification des seuils selon l'état du sol ---
        if self.etat_sol == 1 and sigma0 > 50:
            raise ValueError("σ′₀ dépasse 50 kPa pour un sol Ice-Poor.")
        if self.etat_sol == 0 and not (1 <= sigma0 <= 50):
            raise ValueError("σ′₀ doit être entre 1 et 50 kPa pour un sol Ice-Rich.")

        return sigma0
