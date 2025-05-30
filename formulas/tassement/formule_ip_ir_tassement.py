import math

# Dictionnaire d'affichage
CLASSE_SOL = {
    0: "Ice-Rich",
    1: "Ice-Poor",
    2: "Zone de transition entre IR et IP",
    -1: "Hors seuils connus"
}

class ClassificationSol:
    """
    Pour le tassement :
    Classe pour classifier un sol comme Ice-Rich (IR), Ice-Poor (IP)
    ou Zone de transition selon ei* et le type de sol.
    Retourne un entier pour faciliter les traitements :
    - 0 : Ice-Rich
    - 1 : Ice-Poor
    - -1 : Hors seuils connus
    """
    
    def __init__(self, ei_star: float, valeur_sol: float, type_sol: str, marge: float = 0.1):
        self.ei_star = ei_star
        self.valeur_sol = valeur_sol
        self.type_sol = type_sol.strip()
        self.marge = marge  # Par défaut 0.1
        self.is_near_limit = False
    
    def classer(self) -> int:
        type_sol = self.type_sol
        self.is_near_limit = False
        if type_sol == "Clay percentage":
            if not (0 <= self.valeur_sol <= 100):
                raise ValueError("The value of Clay percentage must be between 0 and 100.")

            # Calcul des limites pour Clay percentage
            if self.valeur_sol <= 20:
                limite_ip = 1.5
                limite_ir = 2.0
            elif self.valeur_sol <= 40:
                limite_ip = 1.3
                limite_ir = 1.7
            else:
                limite_ip = 1.1
                limite_ir = 1.4

            seuil_ir = limite_ir
            seuil_ip = limite_ip
            diff = self.ei_star - seuil_ir
            # Zone de transition stricte
            if abs(self.ei_star - seuil_ir) <= self.marge:
                self.is_near_limit = True
            if self.ei_star > seuil_ir:
                return 0  # Ice-Rich
            elif self.ei_star < seuil_ip:
                return 1  # Ice-Poor
            else:
                # Exactement dans la zone de transition
                self.is_near_limit = True
                return 0 if diff >= 0 else 1
        elif type_sol == "Liquid limit":
            if not (0 <= self.valeur_sol <= 100):
                raise ValueError("The value of Liquid limit must be between 0 and 100.")

            # Calcul des limites pour Liquid limit
            if self.valeur_sol <= 30:
                limite_ip = 1.5
                limite_ir = 2.0
            elif self.valeur_sol <= 50:
                limite_ip = 1.3
                limite_ir = 1.7
            else:
                limite_ip = 1.1
                limite_ir = 1.4

            seuil = limite_ir
            diff = self.ei_star - seuil
            if abs(diff) <= self.marge:
                self.is_near_limit = True
            if self.ei_star > seuil:
                return 0  # Ice-Rich
            elif self.ei_star < seuil:
                return 1  # Ice-Poor
            else:
                self.is_near_limit = True
                return 0 if diff >= 0 else 1
        elif type_sol == "Fine fraction median diameter":
            if not (0.001 <= self.valeur_sol <= 0.1):
                raise ValueError("The value of Fine fraction median diameter must be between 0.001 and 0.1 mm.")

            # Calcul des limites pour Fine fraction median diameter
            if self.valeur_sol <= 0.002:
                limite_ip = 1.1
                limite_ir = 1.4
            elif self.valeur_sol <= 0.01:
                limite_ip = 1.3
                limite_ir = 1.7
            else:
                limite_ip = 1.5
                limite_ir = 2.0

            seuil = limite_ir
            diff = self.ei_star - seuil
            if abs(diff) <= self.marge:
                self.is_near_limit = True
            if self.ei_star > seuil:
                return 0  # Ice-Rich
            elif self.ei_star < seuil:
                return 1  # Ice-Poor
            else:
                self.is_near_limit = True
                return 0 if diff >= 0 else 1
        else:
            raise ValueError("Invalid soil type. Expected: Clay percentage, Liquid limit or Fine fraction median diameter.")