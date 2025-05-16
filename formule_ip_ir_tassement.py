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

    def __init__(self, ei_star: float, valeur_sol: float, type_sol: str, marge: float = 0.1):  #à revoir pour la 
        self.ei_star = ei_star
        self.valeur_sol = valeur_sol
        self.type_sol = type_sol.strip()
        self.marge = marge  # Par défaut 0.1

    def classer(self) -> int:
        type_sol = self.type_sol
         
        if type_sol == "clay%":
            if not (0 < self.valeur_sol <= 100):
                raise ValueError("La valeur de clay% doit être entre 0 et 100.")
            seuil_ip = 0.01 * self.valeur_sol + 0.90 #pour ice poor on prend 0.01*clay%+0.90
            seuil_ir = 0.01 * self.valeur_sol + 0.91 #Pour ice rich on prend 0.01*clay%+0.91
            centre_transition = 0.01 * self.valeur_sol + 0.90

        elif type_sol == "wL":
            if not (0 < self.valeur_sol <= 100):
                raise ValueError("La valeur de wL doit être entre 0 et 100.")
            seuil_ip = 0.01 * self.valeur_sol + 0.61
            seuil_ir = seuil_ip
            centre_transition = seuil_ip

        elif type_sol == "d50ff":
            if not (0.001 <= self.valeur_sol <= 0.1):
                raise ValueError("La valeur de d50ff doit être entre 0.001 et 0.1 mm.")
            seuil_ip = 0.17 * math.log(self.valeur_sol) + 1.98
            seuil_ir = seuil_ip
            centre_transition = seuil_ip

        else:
            raise ValueError("Type de sol invalide. Attendu : clay%, wL ou d50ff.")

        
        if self.ei_star < seuil_ip:
            return 1  # Ice-Poor
        elif self.ei_star > seuil_ir:
            return 0  # Ice-Rich
        elif abs(self.ei_star - centre_transition) <= self.marge:  #à voir ce qu'on fait pour le calcul du tassement
            return 2  # Zone de transition
        else:
            return -1  # Cas non classifiable