from PyQt6.QtWidgets import QMessageBox


class EI_Tassement:
    """
    Classe pour le calcul de l'indice de glace ei* utilisé dans le modèle de tassement.
    """

    def __init__(self, valeur_pore: float, Specific_gravity_of_solids: float, type_pore: str):
        self.valeur_pore = valeur_pore
        self.Specific_gravity_of_solids = Specific_gravity_of_solids
        self.type_pore = type_pore  # "Initial water content", "Frozen bulk density", "Frozen void ratio"

    def calculer(self) -> float:
        # Validation Specific gravity of solids
        if not (1 <= self.Specific_gravity_of_solids <= 4):
            raise ValueError("The Specific gravity of solids must be between 1 and 4.")

        if self.type_pore == "Initial water content":
            if self.valeur_pore <= 0:
                raise ValueError("Initial water content must be positive.")
            ei_star = 0.01 * self.valeur_pore * self.Specific_gravity_of_solids

        elif self.type_pore == "Frozen bulk density":
            if abs(self.valeur_pore - 0.9174) < 1e-6: # pour éviter la division par zéro et erreurs arrondies
                raise ValueError("Frozen bulk density cannot be equal to 0.9174 (division by zero).")
            ei_star = (self.Specific_gravity_of_solids - self.valeur_pore) / (self.valeur_pore - 0.9174)  # Formule 13b

        elif self.type_pore == "Frozen void ratio":
            if not (0 < self.valeur_pore < 4.36):
                raise ValueError("Frozen void ratio must be positive and less than 4.36 for ei* < 4.")  #4.36 pour pas que ei depasse 4
            ei_star = self.valeur_pore / 1.09  # Formule 13c

        else:
            raise ValueError("Invalid pore parameter type: Initial water content, Frozen bulk density or Frozen void ratio expected.")

        if ei_star > 4:
            QMessageBox.critical(None,"Value out of range", "ei* exceeds the maximum threshold of 4."
                                                            "ei* adjusted to 4")
            ei_star = 4
            return ei_star
        if ei_star < 0:
            QMessageBox.critical(None, "Value out of range", "ei* cannot be less than zero."
                                                             "ei* adjusted to 0")
            ei_star = 0
            return ei_star

        return ei_star