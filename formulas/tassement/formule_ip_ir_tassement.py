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
        if type_sol == "clay%":
            if not (0 < self.valeur_sol <= 100):
                raise ValueError("The value of clay% must be between 0 and 100.")
            seuil_ir = 0.01 * self.valeur_sol + 0.91
            seuil_ip = 0.01 * self.valeur_sol + 0.9
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
        elif type_sol == "wL":
            if not (0 < self.valeur_sol <= 100):
                raise ValueError("The value of wL must be between 0 and 100.")
            seuil = 0.01 * self.valeur_sol + 0.61
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
        elif type_sol == "d50ff":
            if not (0.001 <= self.valeur_sol <= 0.1):
                raise ValueError("The value of d50ff must be between 0.001 and 0.1 mm.")
            seuil = 0.17 * math.log(self.valeur_sol) + 1.98
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
            raise ValueError("Invalid soil type. Expected: clay%, wL or d50ff.")