import math

from PyQt6.QtWidgets import QMessageBox

"""
    Attributes:
        type_sol (float): Type de sol
        pores_sol (float): Porosité du sol
        compress_sol (float): Compression du sol
        density_sol (float): Densité du sol
        sigma_v (float): Contrainte verticale
        E0 (float): Indice des vides initial
        Ei (float): Indice des vides
        sigma_0 (float): Contrainte de référence
        kv0 (float): Perméabilité verticale
        Cc (float): Indice de compression
        Ck (float): Indice de perméabilité
        result (float): Résultat du calcul
    """
class FormulaClay:    

    
    def __init__(self):
        self.type_sol = None
        self.pores_sol = None
        self.compress_sol = None
        self.density_sol = None
        self.sigma_v = None
        self.E0 = None
        self.Ei = None
        self.sigma_0 = None
        self.kv0 = None
        self.Cc = None
        self.Ck = None
        self.result = None

    def calculate(self, clay, water, compression, density, pore_style, ei=None, cc=None, ck=None):
        """Calcule kv et les indices intermédiaires.

        Paramètres
        - clay : descripteur du sol (ex. clay%)
        - water : paramètre de pore (W, ρf, ef)
        - compression : contrainte verticale efficace σ'v
        - density : masse volumique spécifique des solides (Gs)
        - pore_style : "Initial water content" | "Frozen bulk density" | "Frozen void ratio"
        - ei, cc, ck : surcharges optionnelles
        """
        self.type_sol = clay
        self.pores_sol = water
        self.compress_sol = self.sigma_v = compression
        self.density_sol = density
        self.Ei = ei
        self.Cc = cc
        self.Ck = ck

        try:
            if self.Ei is None:
                if pore_style == "Initial water content":
                    self.formula13a()
                elif pore_style == "Frozen bulk density":
                    self.formula13b()
                elif pore_style == "Frozen void ratio":
                    self.formula13c()
            self.formula12()
            self.formula14()
            self.formula15()
            if self.Cc is None:
                self.formula16()
            if self.Ck is None:
                self.formula17()
            self.formula11()
        except (ZeroDivisionError, OverflowError) as e:
            raise e

        return self.result, self.Ei, self.Cc, self.Ck, self.E0, self.sigma_0, self.kv0, self.sigma_v

    def formula11(self):
        """Calcule la conductivité hydraulique dégelée kv."""
        exponent = -(self.Cc / self.Ck)
        base = self.sigma_v / self.sigma_0
        self.result = self.kv0 * base ** exponent


    def formula12(self):
        """Calcule E0 à partir de Ei et du descripteur de sol."""
        numerator = ((0.0018 * self.type_sol - 0.099) * math.log10(self.Ei) + 0.0007 * self.type_sol - 0.053)
        denominator = 0.30
        exponent = numerator / denominator
        self.E0 = 10 ** exponent
        

    def formula13a(self):
        """Ei à partir de la teneur en eau initiale W et de Gs."""
        self.Ei = 0.01 * self.pores_sol * self.density_sol

    def formula13b(self):
        """Ei à partir de la densité volumique gelée ρf et de Gs (protège div. par 0)."""
        numerator = self.density_sol - self.pores_sol
        denominator = self.pores_sol - 0.9174
        if denominator == 0:
            raise ZeroDivisionError
        self.Ei = numerator / denominator

    def formula13c(self):
        """Ei à partir de l'indice des vides gelé ef (inverse du facteur 1.09)."""
        self.Ei = self.pores_sol / 1.09

    def formula14(self):
        """Calcule σ0 et plafonne à 50 kPa avec avertissement UI."""
        numerator = self.E0 - 0.0049 * self.type_sol - 0.82
        denominator = -0.00063 * self.type_sol - 0.06
        exponent = numerator / denominator
        sigma_0 = 2 * math.exp(exponent)
        if sigma_0 > 50:
            QMessageBox.warning(None, "Value out of range", f"Sigma_0 is over the limit of 50 with a value of {sigma_0}")
            self.sigma_0 = 50
        else:
            self.sigma_0 = sigma_0

    def formula15(self):
        """Calcule la conductivité de référence kv0 à partir de E0 et clay%."""
        exponent = -0.077 * self.type_sol + (-0.05 * self.type_sol + 20.5) * self.E0
        self.kv0 = 3 * 1.1 * (10 ** (-12)) * math.exp(exponent)

    def formula16(self):
        """Calcule l'indice de compression Cc à partir de E0 si non fourni."""
        self.Cc = 0.74 * math.log10(self.E0) + 0.22

    def formula17(self):
        """Calcule l'indice de conductivité Ck à partir de E0 si non fourni."""
        self.Ck = 0.30 * math.log10(self.E0) + 0.12
