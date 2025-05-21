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
    - 2 : Zone de transition
    - -1 : Hors seuils connus
    """
    
    def __init__(self, ei_star: float, valeur_sol: float, type_sol: str, marge: float = 0.1):
        self.ei_star = ei_star
        self.valeur_sol = valeur_sol
        self.type_sol = type_sol.strip()
        self.marge = marge  # Par défaut 0.1
    
    def classer(self) -> int:
        type_sol = self.type_sol
        
        if type_sol == "clay%":
            if not (0 < self.valeur_sol <= 100):
                raise ValueError("La valeur de clay% doit être entre 0 et 100.")
            
            seuil = 0.01 * self.valeur_sol + 0.9
            diff = self.ei_star - seuil
            
            if abs(diff) <= self.marge + 1e-4:  # pour tolerer nombre avec virgules
                return 2  # Zone de transition
            elif diff > self.marge:
                return 0  # Ice-Rich (Ei* > 0.01*clay% + 0.9 + marge)
            else:
                return 1  # Ice-Poor (Ei* < 0.01*clay% + 0.9 - marge)
        
        elif type_sol == "wL":
            if not (0 < self.valeur_sol <= 100):
                raise ValueError("La valeur de wL doit être entre 0 et 100.")
            
            seuil = 0.01 * self.valeur_sol + 0.61
            diff = self.ei_star - seuil
            
            if abs(diff) <= self.marge + 1e-4:  
                return 2  # Zone de transition
            elif diff > self.marge:
                return 0  # Ice-Rich (Ei* > 0.01*wL + 0.61 + marge)
            else:
                return 1  # Ice-Poor (Ei* < 0.01*wL + 0.61 - marge)
        
        elif type_sol == "d50ff":
            if not (0.001 <= self.valeur_sol <= 0.1):
                raise ValueError("La valeur de d50ff doit être entre 0.001 et 0.1 mm.")
            
            seuil = 0.17 * math.log(self.valeur_sol) + 1.98
            diff = self.ei_star - seuil
            
            if abs(diff) <= self.marge + 1e-4:   
                return 2  # Zone de transition
            elif diff > self.marge:
                return 0  # Ice-Rich (Ei* > 0.17*ln(d50ff) + 1.98 + marge)
            else:
                return 1  # Ice-Poor (Ei* < 0.17*ln(d50ff) + 1.98 - marge)
        
        else:
            raise ValueError("Type de sol invalide. Attendu : clay%, wL ou d50ff.")