import math

class CalculCcStar:
    """
    Calcule la valeur de Cc* en fonction de ei*, du type de sol, de la valeur de l'indice,
    et de l'état du sol (0 = IR, 1 = IP). Vérifie aussi le seuil minimal autorisé.
    """

    def __init__(self, ei_star: float, valeur_type_sol: float, type_sol: str, etat_sol: int):
        self.ei_star = ei_star
        self.valeur = valeur_type_sol
        self.type = type_sol.strip()
        self.etat = etat_sol  #  (0 = IR, 1 = IP)

    def calculer(self) -> float:
        if self.ei_star <= 0:
            raise ValueError("ei* must be strictly positive for the log calculation.")
        log_ei = math.log10(self.ei_star)
        # Ice-Poor (1)
        if self.etat == 1:
            cc_star = 0.74 * log_ei + 0.22  # Cc* = 0.74 * log(ei*) + 0.22

        # Ice-Rich (0)
        elif self.etat == 0:
            if self.type == "Liquid limit":
                cc_star = (0.0081 * self.valeur - 0.019) * log_ei + (0.0033 * self.valeur + 0.037)
            elif self.type == "Clay content":
                cc_star = (0.0051 * self.valeur - 0.18) * log_ei + (0.0015 * self.valeur + 0.096)
            elif self.type == "Fine fraction median diameter":
                if self.valeur <= 0:
                    raise ValueError("Fine fraction median diameter must be > 0 to calculate log.")
                log_d50 = math.log10(self.valeur)
                cc_star = (-0.11 * log_d50 + 0.080) * log_ei + (-0.097 * log_d50 - 0.082)
            else:
                raise ValueError("Unknown soil type: expected 'Clay percentage', 'Liquid limit', or 'Fine fraction median diameter'.")
        else:
            raise ValueError("Unrecognized soil state: expected IR or IP.")

        # --- Vérification du seuil minimal autorisé ---
        seuil = self.seuil_minimal()

        if cc_star <= seuil:
            raise ValueError(
                f"Cc* = {cc_star:.6f} is inferior to the minimum authorized threshold ({seuil:.6f}) for soil type {self.type}."
            )

        return cc_star

    def seuil_minimal(self) -> float:
        if self.type == "Liquid limit":
            return 0.004 * self.valeur - 0.05
        elif self.type == "Clay percentage":
            return 0.001 * self.valeur + 0.05
        elif self.type == "Fine fraction median diameter":
            if self.valeur <= 0:
                raise ValueError("Fine fraction median diameter must be > 0 to evaluate the threshold.")
            return -0.04 * math.log(self.valeur) - 0.14
        else:
            raise ValueError("Invalid soil type for threshold evaluation.")
