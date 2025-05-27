class EI_Tassement:
    """
    Classe pour le calcul de l'indice de glace ei* utilisé dans le modèle de tassement.
    """

    def __init__(self, valeur_pore: float, Gs: float, type_pore: str):
        self.valeur_pore = valeur_pore
        self.Gs = Gs
        self.type_pore = type_pore  # "w", "ρf", "ef*"

    def calculer(self) -> float:
        # Validation Gs
        if not (1 <= self.Gs <= 4):
            raise ValueError("The specific gravity Gs must be between 1 and 4.")

        if self.type_pore == "w": 
            if self.valeur_pore <= 0:
                raise ValueError("w must be positive.")
            ei_star = 0.01 * self.valeur_pore * self.Gs  # Formule 13a

        elif self.type_pore == "ρf":
            if abs(self.valeur_pore - 0.9174) < 1e-6: # pour éviter la division par zéro et erreurs arrondies
                raise ValueError("ρf cannot be equal to 0.9174 (division by zero).")
            ei_star = (self.Gs - self.valeur_pore) / (self.valeur_pore - 0.9174)  # Formule 13b

        elif self.type_pore == "ef":
            if not (0 < self.valeur_pore < 4.36):
                raise ValueError("ef must be positive and less than 4.36 for ei* < 4.")  #4.36 pour pas que ei depasse 4
            ei_star = self.valeur_pore / 1.09  # Formule 13c

        else:
            raise ValueError("Invalid pore parameter type: w, ρf or ef expected.")

        if ei_star > 4:
            raise ValueError("ei* exceeds the maximum threshold of 4.")
        if ei_star < 0:
            raise ValueError("ei* cannot be negative.")

        return ei_star