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

class FormulaD50ff:
    """Modèle hydraulique basé sur d50 de la fraction fine.

    Calcule kv, ei, e0, σ0, Cc et Ck. Utiliser `calculate(...)`.
    Retour: `(kv, ei, cc, ck, e0, sigma_0, kv0, sigma_v)`.
    """
    def __init__(self):
        self.type_sol = None
        self.pores_sol = None
        self.compress_sol = None
        self.density_sol = None
        self.sigma_v = None
        self.e0 = None
        self.ei = None
        self.sigma_0 = None
        self.kv0 = None
        self.cc = None
        self.ck = None
        self.result = None

    def calculate(self, clay, water, compression, density, pore_style, ei=None, cc=None, ck=None):
        """Calcule la conductivité et les indices intermédiaires."""
        self.type_sol = clay
        self.pores_sol = water
        self.compress_sol = self.sigma_v = compression
        self.density_sol = density
        self.ei = ei
        self.cc = cc
        self.ck = ck

        try:
            if self.ei is None:
                if pore_style == "Initial water content":
                    self.formula13a()
                elif pore_style == "Frozen bulk density":
                    self.formula13b()
                elif pore_style == "Frozen void ratio":
                    self.formula13c()
            self.formula12()
            self.formula14()
            self.formula15()
            if self.cc is None:
                self.formula16()
            if self.ck is None:
                self.formula17()
            self.formula11()
        except (ZeroDivisionError, OverflowError) as e:
            raise e

        return self.result, self.ei, self.cc, self.ck, self.e0, self.sigma_0, self.kv0, self.sigma_v

    def formula11(self):
        """Calcule kv à partir du rapport de contraintes et des indices."""
        exponent = -(self.cc / self.ck)
        base = self.sigma_v / self.sigma_0
        self.result = self.kv0 * base ** exponent
    def formula12(self):
        """Calcule e0 en fonction de ei et d50ff."""
        numerator = (
                (-0.074 * math.log10(self.type_sol) + 0.014) * math.log10(self.ei)
                - 0.028 * math.log10(self.type_sol)
                - 0.096
        )
        denominator = 0.30
        exponent = numerator / denominator
        self.e0 = 10 ** exponent

    def formula13a(self):
        """ei depuis W et Gs."""
        self.ei = 0.01 * self.pores_sol * self.density_sol

    def formula13b(self):
        """ei depuis ρf et Gs."""
        numerator = self.density_sol - self.pores_sol
        denominator = self.pores_sol - 0.9174
        self.ei = numerator / denominator

    def formula13c(self):
        """ei depuis ef (inverse 1.09)."""
        self.ei = self.pores_sol / 1.09

    def formula14(self):
        """Calcule σ0 (plafonné à 50 kPa)."""
        numerator = self.e0 + 0.25 * math.log10(self.type_sol) - 0.45
        denominator = 0.02 * math.log10(self.type_sol) - 0.06
        exponent = numerator / denominator
        sigma_0 = 0.9 * math.exp(exponent)
        if sigma_0 > 50:
            QMessageBox.warning(None, "Value out of range", f"Sigma_0 is over the limit of 50 with a value of {sigma_0}")
            self.sigma_0 = 50
        else:
            self.sigma_0 = sigma_0

    def formula15(self):
        """Calcule kv0 en fonction de e0 et d50ff."""
        exponent = 3.1 * math.log10(self.type_sol) + (2.02 * math.log10(self.type_sol) + 23.6) * self.e0
        self.kv0 = 1.3 * 2.2 * (10 ** (-10)) * math.exp(exponent)

    def formula16(self):
        """Calcule cc si non fourni."""
        self.cc = 0.74 * math.log10(self.e0) + 0.22

    def formula17(self):
        """Calcule ck si non fourni."""
        self.ck = 0.30 * math.log10(self.e0) + 0.12