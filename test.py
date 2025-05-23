import unittest
import math

# Import des classes existantes
from formulas.tassement.formule_ei_tassement import EI_Tassement
from formulas.tassement.formule_ip_ir_tassement import ClassificationSol, CLASSE_SOL
from formulas.tassement.formule_cc_tassement import CalculCcStar
from formulas.tassement.formule_e0_tassement import CalculE0Tassement
from formulas.tassement.formule_sigma0 import CalculSigma0
from formulas.tassement.formule_calculer_tassement import CalculTassements
from formulas.tassement.formule_indice_des_vides import CalculIndiceDesVides

class TestEITassement(unittest.TestCase):
    """Tests pour la classe EI_Tassement"""
    
    def test_calcul_avec_w(self):
        # Test avec teneur en eau w
        ei = EI_Tassement(valeur_pore=50, Gs=2.7, type_pore="w")
        result = ei.calculer()
        expected = 0.01 * 50 * 2.7  # 1.35
        self.assertAlmostEqual(result, expected, places=6)
    
    def test_calcul_avec_rho_f(self):
        # Test avec densité du sol gelé ρf
        ei = EI_Tassement(valeur_pore=1.5, Gs=2.65, type_pore="ρf")
        result = ei.calculer()
        expected = (2.65 - 1.5) / (1.5 - 0.9174)
        self.assertAlmostEqual(result, expected, places=6)
    
    def test_calcul_avec_ef(self):
        # Test avec indice des vides du sol gelé ef
        ei = EI_Tassement(valeur_pore=2.18, Gs=2.7, type_pore="ef")
        result = ei.calculer()
        expected = 2.18 / 1.09
        self.assertAlmostEqual(result, expected, places=6)
    
    def test_validation_gs_invalide(self):
        # Test validation Gs hors limites
        with self.assertRaises(ValueError):
            EI_Tassement(valeur_pore=50, Gs=0.5, type_pore="w").calculer()
        
        with self.assertRaises(ValueError):
            EI_Tassement(valeur_pore=50, Gs=5.0, type_pore="w").calculer()
    
    def test_validation_w_negatif(self):
        # Test w négatif
        with self.assertRaises(ValueError):
            EI_Tassement(valeur_pore=-10, Gs=2.7, type_pore="w").calculer()
    
    def test_validation_rho_f_critique(self):
        # Test ρf = 0.9174 (division par zéro)
        with self.assertRaises(ValueError):
            EI_Tassement(valeur_pore=0.9174, Gs=2.7, type_pore="ρf").calculer()
    
    def test_validation_ef_limite(self):
        # Test ef > 4.36
        with self.assertRaises(ValueError):
            EI_Tassement(valeur_pore=5.0, Gs=2.7, type_pore="ef").calculer()
    
    def test_ei_star_limite_superieure(self):
        # Test avec ei* proche de 4 (limite supérieure)
        with self.assertRaises(ValueError) as context:
            ei_calc = EI_Tassement(valeur_pore=500, Gs=2.7, type_pore="w")  # Valeur qui dépasse 4
            ei_calc.calculer()  # Devrait lever une exception ValueError
    
    # Vérification que l'exception a bien été levée avec le bon message
        self.assertEqual(str(context.exception), "ei* dépasse le seuil maximal de 4.")

class TestClassificationSol(unittest.TestCase):
    """Tests pour la classification Ice-Rich/Ice-Poor"""
    
    def test_classification_clay_ice_rich(self):
        # Test avec clay% - Ice-Rich
        classif = ClassificationSol(ei_star=2.5, valeur_sol=50, type_sol="clay%", marge=0.1)
        result = classif.classer()
        self.assertEqual(result, 0)  # Ice-Rich
    
    def test_classification_clay_ice_poor(self):
        # Test avec clay% - Ice-Poor
        classif = ClassificationSol(ei_star=1.0, valeur_sol=50, type_sol="clay%", marge=0.1)
        result = classif.classer()
        self.assertEqual(result, 1)  # Ice-Poor
    
    def test_classification_clay_transition(self):
        # Test avec clay% - Zone de transition
        classif = ClassificationSol(ei_star=1.4, valeur_sol=50, type_sol="clay%", marge=0.1)
        result = classif.classer()
        self.assertEqual(result, 2)  # Zone de transition
    
    def test_classification_wL_ice_rich(self):
        # Test avec wL - Ice-Rich
        classif = ClassificationSol(ei_star=2.0, valeur_sol=30, type_sol="wL", marge=0.1)
        result = classif.classer()
        self.assertEqual(result, 0)  # Ice-Rich
    
    def test_classification_d50ff_ice_poor(self):
        # Test avec d50ff - Ice-Poor
        classif = ClassificationSol(ei_star=1.0, valeur_sol=0.01, type_sol="d50ff", marge=0.1)
        result = classif.classer()
        self.assertEqual(result, 1)  # Ice-Poor
    
    def test_validation_clay_percent_invalide(self):
        # Test clay% hors limites
        with self.assertRaises(ValueError):
            ClassificationSol(ei_star=1.5, valeur_sol=150, type_sol="clay%").classer()

class TestCalculCcStar(unittest.TestCase):
    """Tests pour le calcul de Cc*"""
    
    def test_calcul_cc_star_limite_superieure(self):
        # Test Cc* pour valeurs maximales attendues
        calc = CalculCcStar(ei_star=5.0, valeur_type_sol=50, type_sol="clay%", etat_sol=0)
        result = calc.calculer()
        # On attend ici un résultat dans une plage valide
        self.assertGreater(result, 0)
        self.assertLess(result, 10)
    
    def test_calcul_cc_star_ice_poor(self):
        # Test Cc* pour Ice-Poor
        calc = CalculCcStar(ei_star=2.0, valeur_type_sol=40, type_sol="wL", etat_sol=1)
        result = calc.calculer()
        expected = 0.74 * math.log(2.0) + 0.22
        self.assertAlmostEqual(result, expected, places=6)
    
    def test_calcul_cc_star_ice_rich_wL(self):
        # Test Cc* pour Ice-Rich avec wL
        calc = CalculCcStar(ei_star=2.5, valeur_type_sol=50, type_sol="wL", etat_sol=0)
        result = calc.calculer()
        
        log_ei = math.log(2.5)
        expected = (0.0081 * 50 - 0.019) * log_ei + (0.0033 * 50 + 0.037)
        self.assertAlmostEqual(result, expected, places=6)
    
    def test_calcul_cc_star_ice_rich_clay(self):
        # Test Cc* pour Ice-Rich avec clay%
        calc = CalculCcStar(ei_star=1.8, valeur_type_sol=35, type_sol="clay%", etat_sol=0)
        result = calc.calculer()
        
        log_ei = math.log(1.8)
        expected = (0.0051 * 35 - 0.018) * log_ei + (0.0015 * 35 + 0.096)
        self.assertAlmostEqual(result, expected, places=6)
    
    def test_calcul_cc_star_ice_rich_d50ff(self):
        # Test Cc* pour Ice-Rich avec d50ff
        calc = CalculCcStar(ei_star=2.2, valeur_type_sol=0.01, type_sol="d50ff", etat_sol=0)
        result = calc.calculer()
        
        log_ei = math.log(2.2)
        log_d50 = math.log(0.01)
        expected = (-0.11 * log_d50 + 0.080) * log_ei + (-0.097 * log_d50 - 0.082)
        self.assertAlmostEqual(result, expected, places=6)
    
    def test_validation_ei_star_negatif(self):
        # Test ei* négatif
        with self.assertRaises(ValueError):
            CalculCcStar(ei_star=-1.0, valeur_type_sol=40, type_sol="wL", etat_sol=1).calculer()
    
    def test_validation_seuil_minimal(self):
        # Test vérification du seuil minimal
        # Valeurs qui devraient donner un Cc* trop faible
        with self.assertRaises(ValueError):
            CalculCcStar(ei_star=0.1, valeur_type_sol=20, type_sol="wL", etat_sol=0).calculer()
    
    def test_seuil_minimal_wL(self):
        # Test calcul seuil minimal pour wL
        calc = CalculCcStar(ei_star=2.0, valeur_type_sol=40, type_sol="wL", etat_sol=0)
        seuil = calc.seuil_minimal()
        expected = 0.004 * 40 - 0.05
        self.assertAlmostEqual(seuil, expected, places=6)
    
    def test_seuil_minimal_clay(self):
        # Test calcul seuil minimal pour clay%
        calc = CalculCcStar(ei_star=2.0, valeur_type_sol=30, type_sol="clay%", etat_sol=0)
        seuil = calc.seuil_minimal()
        expected = 0.001 * 30 + 0.05
        self.assertAlmostEqual(seuil, expected, places=6)
    
    def test_seuil_minimal_d50ff(self):
        # Test calcul seuil minimal pour d50ff
        calc = CalculCcStar(ei_star=2.0, valeur_type_sol=0.01, type_sol="d50ff", etat_sol=0)
        seuil = calc.seuil_minimal()
        expected = -0.04 * math.log(0.01) - 0.14
        self.assertAlmostEqual(seuil, expected, places=6)

    def test_calcul_cc_star_seuil_minimal(self):
        # Test pour s'assurer que Cc* respecte le seuil minimal
        calc = CalculCcStar(ei_star=0.1, valeur_type_sol=20, type_sol="wL", etat_sol=1)
        with self.assertRaises(ValueError):
            calc.calculer()  # Doit lever une exception si Cc* est en dessous du seuil minimal

class TestCalculE0Tassement(unittest.TestCase):
    """Tests pour le calcul de e0*"""
    
    def test_calcul_e0_ice_poor(self):
        # Test e0* pour Ice-Poor
        calc = CalculE0Tassement(ei_star=1.5, cc_star=0.4, etat_sol=1)
        result = calc.calculer()
        expected = 1.5  # Pour Ice-Poor, e0* = ei*
        self.assertAlmostEqual(result, expected, places=6)
    
    def test_calcul_e0_ice_rich(self):
        # Test e0* pour Ice-Rich
        calc = CalculE0Tassement(ei_star=2.0, cc_star=0.6, etat_sol=0)
        result = calc.calculer()
        exponent = (0.6 - 0.22) / 0.74
        expected = 10 ** exponent
        self.assertAlmostEqual(result, expected, places=6)
    
    def test_validation_etat_sol_invalide(self):
        # Test état du sol invalide
        with self.assertRaises(ValueError):
            CalculE0Tassement(ei_star=1.5, cc_star=0.4, etat_sol=2).calculer()
    
    def test_cas_limite_cc_star(self):
        # Test avec Cc* = 0.22 (cas limite pour Ice-Rich)
        calc = CalculE0Tassement(ei_star=2.0, cc_star=0.22, etat_sol=0)
        result = calc.calculer()
        expected = 10 ** 0  # 10^0 = 1
        self.assertAlmostEqual(result, expected, places=6)

class TestCalculSigma0(unittest.TestCase):
    """Tests pour le calcul de σ'₀"""
    
    def test_calcul_sigma0_wL_ice_poor(self):
        # Test avec wL et Ice-Poor
        calc = CalculSigma0(e0_star=1.5, type_sol="wL", valeur_sol=40, etat_sol=1)
        result = calc.calculer()
        self.assertLessEqual(result, 50)  # Seuil max pour Ice-Poor
        self.assertGreater(result, 0)
    
    def test_calcul_sigma0_clay_ice_rich(self):
        # Test avec clay% et Ice-Rich
        calc = CalculSigma0(e0_star=2.0, type_sol="clay%", valeur_sol=30, etat_sol=0)
        result = calc.calculer()
        self.assertGreaterEqual(result, 1)  # Seuil min pour Ice-Rich
        self.assertLessEqual(result, 50)    # Seuil max
    
    def test_calcul_sigma0_d50ff_ice_rich(self):
        # Test avec d50ff et Ice-Rich
        calc = CalculSigma0(e0_star=1.8, type_sol="d50ff", valeur_sol=0.01, etat_sol=0)
        result = calc.calculer()
        self.assertGreaterEqual(result, 1)
        self.assertLessEqual(result, 50)

class TestCalculIndiceDesVides(unittest.TestCase):
    """Tests pour le calcul de l'indice des vides final"""
    
    def test_calcul_indice_des_vides_normal(self):
        # Test calcul normal
        calc = CalculIndiceDesVides(e0_star=2.0, cc_star=0.5, sigma_v=100, sigma0=50)
        result = calc.calculer()
        expected = 2.0 - 0.5 * math.log10(100/50)
        self.assertAlmostEqual(result, expected, places=6)
    
    def test_calcul_indice_des_vides_sigma_egales(self):
        # Test avec σ'ᵥ = σ'₀
        calc = CalculIndiceDesVides(e0_star=1.5, cc_star=0.3, sigma_v=50, sigma0=50)
        result = calc.calculer()
        expected = 1.5 - 0.3 * math.log10(1)  # log10(1) = 0
        self.assertAlmostEqual(result, expected, places=6)
    
    def test_validation_sigma_v_negative(self):
        # Test σ'ᵥ négatif
        with self.assertRaises(ValueError):
            CalculIndiceDesVides(e0_star=1.5, cc_star=0.3, sigma_v=-10, sigma0=50).calculer()

    def test_calcul_indice_des_vides_sigma_egales(self):
        # Test avec σ'ᵥ égal à σ'₀
        calc = CalculIndiceDesVides(e0_star=2.0, cc_star=0.5, sigma_v=50, sigma0=50)
        result = calc.calculer()
        expected = 2.0 - 0.5 * math.log10(1)  # log10(1) = 0
        self.assertAlmostEqual(result, expected, places=6)

class TestCalculTassements(unittest.TestCase):
    """Tests pour le calcul des tassements S1, S2 et S_total"""
    
    def test_calcul_tassements_normal(self):
        # Test calcul normal des tassements
        calc = CalculTassements(ef=2.5, e0_star=2.0, e_final=1.5)
        s1, s2, s_total = calc.calculer()
        
        expected_s1 = (2.5 - 2.0) / (1 + 2.5) * 100  # 14.29%
        expected_s2 = (2.0 - 1.5) / (1 + 2.5) * 100  # 14.29%
        expected_total = expected_s1 + expected_s2    # 28.57%
        
        self.assertAlmostEqual(s1, expected_s1, places=2)
        self.assertAlmostEqual(s2, expected_s2, places=2)
        self.assertAlmostEqual(s_total, expected_total, places=2)
    
    def test_calcul_tassements_ef_egal_e0(self):
        # Test avec ef = e0* (S1 = 0)
        calc = CalculTassements(ef=2.0, e0_star=2.0, e_final=1.5)
        s1, s2, s_total = calc.calculer()
        
        expected_s1 = 0.0
        expected_s2 = (2.0 - 1.5) / (1 + 2.0) * 100
        expected_total = expected_s1 + expected_s2
        
        self.assertAlmostEqual(s1, expected_s1, places=6)
        self.assertAlmostEqual(s2, expected_s2, places=2)
        self.assertAlmostEqual(s_total, expected_total, places=2)
    
    def test_calcul_tassements_e0_egal_e_final(self):
        # Test avec e0* = e_final (S2 = 0)
        calc = CalculTassements(ef=2.5, e0_star=1.5, e_final=1.5)
        s1, s2, s_total = calc.calculer()
        
        expected_s1 = (2.5 - 1.5) / (1 + 2.5) * 100
        expected_s2 = 0.0
        expected_total = expected_s1 + expected_s2
        
        self.assertAlmostEqual(s1, expected_s1, places=2)
        self.assertAlmostEqual(s2, expected_s2, places=6)
        self.assertAlmostEqual(s_total, expected_total, places=2)
    
    def test_validation_division_par_zero(self):
        # Test ef = -1 (division par zéro)
        with self.assertRaises(ValueError):
            CalculTassements(ef=-1.0, e0_star=2.0, e_final=1.5).calculer()
    
    def test_tassements_negatifs(self):
        # Test cas où les tassements peuvent être négatifs (gonflement)
        calc = CalculTassements(ef=1.0, e0_star=1.5, e_final=2.0)
        s1, s2, s_total = calc.calculer()
        
        expected_s1 = (1.0 - 1.5) / (1 + 1.0) * 100  # Négatif (gonflement)
        expected_s2 = (1.5 - 2.0) / (1 + 1.0) * 100  # Négatif (gonflement)
        
        self.assertLess(s1, 0)  # S1 négatif
        self.assertLess(s2, 0)  # S2 négatif
        self.assertLess(s_total, 0)  # S_total négatif

class TestCalculsIntegres(unittest.TestCase):
    """Tests d'intégration pour le calcul complet de tassement"""
    
    def test_cas_complet_ice_poor_clay(self):
        """Test complet : sol Ice-Poor avec clay%"""
        print("\n=== Test complet : Sol Ice-Poor avec clay% ===")
        
        # Étape 1: Calcul de ei*
        ei_calc = EI_Tassement(valeur_pore=60, Gs=2.7, type_pore="w")
        ei_star = ei_calc.calculer()
        print(f"ei* = {ei_star:.4f}")
        
        # Étape 2: Classification du sol
        classif = ClassificationSol(ei_star=ei_star, valeur_sol=40, type_sol="clay%")
        etat_sol = classif.classer()
        print(f"Classification: {CLASSE_SOL[etat_sol]}")
        
        # Étape 3: Calcul de Cc*
        if etat_sol in [0, 1]:  # Pas de transition
            cc_calc = CalculCcStar(ei_star=ei_star, valeur_type_sol=40, type_sol="clay%", etat_sol=etat_sol)
            cc_star = cc_calc.calculer()
            print(f"Cc* = {cc_star:.4f}")
            
            # Étape 4: Calcul de e0*
            e0_calc = CalculE0Tassement(ei_star=ei_star, cc_star=cc_star, etat_sol=etat_sol)
            e0_star = e0_calc.calculer()
            print(f"e0* = {e0_star:.4f}")
            
            # Étape 5: Calcul de σ'₀
            sigma0_calc = CalculSigma0(e0_star=e0_star, type_sol="clay%", valeur_sol=40, etat_sol=etat_sol)
            sigma0 = sigma0_calc.calculer()
            print(f"σ'₀ = {sigma0:.2f} kPa")
            
            # Étape 6: Calcul de l'indice des vides final
            sigma_v = 150  # Contrainte appliquée
            indice_calc = CalculIndiceDesVides(e0_star=e0_star, cc_star=cc_star, sigma_v=sigma_v, sigma0=sigma0)
            e_final = indice_calc.calculer()
            print(f"Indice des vides final e = {e_final:.4f}")
            
            # Étape 7: Calcul des tassements
            ef = 2.5  # Indice des vides du sol gelé (exemple)
            tassement_calc = CalculTassements(ef=ef, e0_star=e0_star, e_final=e_final)
            s1, s2, s_total = tassement_calc.calculer()
            print(f"S1 = {s1:.2f}%, S2 = {s2:.2f}%, S_total = {s_total:.2f}%")
            
            # Vérifications
            self.assertGreater(e_final, 0)
            self.assertIsInstance(s_total, float)
    
    def test_cas_complet_ice_rich_wL(self):
        """Test complet : sol Ice-Rich avec wL"""
        print("\n=== Test complet : Sol Ice-Rich avec wL ===")
        
        # Étape 1: Calcul de ei* avec ρf
        ei_calc = EI_Tassement(valeur_pore=1.8, Gs=2.65, type_pore="ρf")
        ei_star = ei_calc.calculer()
        print(f"ei* = {ei_star:.4f}")
        
        # Étape 2: Classification du sol
        classif = ClassificationSol(ei_star=ei_star, valeur_sol=50, type_sol="wL")
        etat_sol = classif.classer()
        print(f"Classification: {CLASSE_SOL[etat_sol]}")
        
        # Étape 3: Calcul complet si pas en zone de transition
        if etat_sol in [0, 1]:
            cc_calc = CalculCcStar(ei_star=ei_star, valeur_type_sol=50, type_sol="wL", etat_sol=etat_sol)
            cc_star = cc_calc.calculer()
            print(f"Cc* = {cc_star:.4f}")
            
            e0_calc = CalculE0Tassement(ei_star=ei_star, cc_star=cc_star, etat_sol=etat_sol)
            e0_star = e0_calc.calculer()
            print(f"e0* = {e0_star:.4f}")
            
            sigma0_calc = CalculSigma0(e0_star=e0_star, type_sol="wL", valeur_sol=50, etat_sol=etat_sol)
            sigma0 = sigma0_calc.calculer()
            print(f"σ'₀ = {sigma0:.2f} kPa")
            
            # Test avec plusieurs contraintes
            contraintes = [100, 200, 400]
            ef = 3.0  # Exemple
            
            for sigma_v in contraintes:
                indice_calc = CalculIndiceDesVides(e0_star=e0_star, cc_star=cc_star, sigma_v=sigma_v, sigma0=sigma0)
                e_final = indice_calc.calculer()
                
                tassement_calc = CalculTassements(ef=ef, e0_star=e0_star, e_final=e_final)
                s1, s2, s_total = tassement_calc.calculer()
                
                print(f"σ'ᵥ = {sigma_v} kPa : e = {e_final:.4f}, S_total = {s_total:.2f}%")
    
    def test_cas_complet_d50ff(self):
        """Test complet : sol avec d50ff"""
        print("\n=== Test complet : Sol avec d50ff ===")
        
        # Étape 1: Calcul de ei* avec ef
        ei_calc = EI_Tassement(valeur_pore=3.0, Gs=2.68, type_pore="ef")
        ei_star = ei_calc.calculer()
        print(f"ei* = {ei_star:.4f}")
        
        # Étape 2: Classification du sol
        classif = ClassificationSol(ei_star=ei_star, valeur_sol=0.005, type_sol="d50ff")
        etat_sol = classif.classer()
        print(f"Classification: {CLASSE_SOL[etat_sol]}")
        
        # Étape 3: Calcul complet
        if etat_sol in [0, 1]:
            cc_calc = CalculCcStar(ei_star=ei_star, valeur_type_sol=0.005, type_sol="d50ff", etat_sol=etat_sol)
            cc_star = cc_calc.calculer()
            print(f"Cc* = {cc_star:.4f}")
            
            e0_calc = CalculE0Tassement(ei_star=ei_star, cc_star=cc_star, etat_sol=etat_sol)
            e0_star = e0_calc.calculer()
            print(f"e0* = {e0_star:.4f}")
            
            sigma0_calc = CalculSigma0(e0_star=e0_star, type_sol="d50ff", valeur_sol=0.005, etat_sol=etat_sol)
            sigma0 = sigma0_calc.calculer()
            print(f"σ'₀ = {sigma0:.2f} kPa")
            
            # Calcul final du tassement
            sigma_v = 300
            ef = 2.75  # Valeur initiale ef
            
            indice_calc = CalculIndiceDesVides(e0_star=e0_star, cc_star=cc_star, sigma_v=sigma_v, sigma0=sigma0)
            e_final = indice_calc.calculer()
            
            tassement_calc = CalculTassements(ef=ef, e0_star=e0_star, e_final=e_final)
            s1, s2, s_total = tassement_calc.calculer()
            
            print(f"Résultats finaux:")
            print(f"  ef = {ef:.4f}")
            print(f"  e0* = {e0_star:.4f}")
            print(f"  e_final = {e_final:.4f}")
            print(f"  S1 = {s1:.2f}%")
            print(f"  S2 = {s2:.2f}%")
            print(f"  S_total = {s_total:.2f}%")
    
    def test_cas_limites_et_erreurs(self):
        """Test des cas limites et gestion d'erreurs"""
        print("\n=== Tests des cas limites ===")
        
        # Test avec ei* proche du seuil maximal
        ei_calc = EI_Tassement(valeur_pore=4.35, Gs=2.7, type_pore="ef")
        ei_star = ei_calc.calculer()
        print(f"ei* limite = {ei_star:.4f}")
        self.assertLess(ei_star, 4.0)
        
        # Test avec contraintes identiques (pas de tassement secondaire)
        indice_calc = CalculIndiceDesVides(e0_star=1.5, cc_star=0.3, sigma_v=100, sigma0=100)
        e_final = indice_calc.calculer()
        print(f"e avec contraintes égales = {e_final:.4f}")
        self.assertAlmostEqual(e_final, 1.5, places=6)
        
        # Test tassement avec gonflement (valeurs inversées)
        tassement_calc = CalculTassements(ef=1.0, e0_star=1.5, e_final=2.0)
        s1, s2, s_total = tassement_calc.calculer()
        print(f"Cas de gonflement: S1 = {s1:.2f}%, S2 = {s2:.2f}%, S_total = {s_total:.2f}%")
        self.assertLess(s_total, 0)  # Gonflement

def run_all_tests():
    """Fonction pour exécuter tous les tests avec un rapport détaillé"""
    print("="*60)
    print("TESTS DE VALIDATION - FORMULES DE TASSEMENT COMPLÈTES")
    print("="*60)
    
    # Créer une suite de tests
    test_suite = unittest.TestSuite()
    
    # Ajouter tous les tests
    test_classes = [
        TestEITassement,
        TestClassificationSol,
        TestCalculCcStar,
        TestCalculE0Tassement,
        TestCalculSigma0,
        TestCalculIndiceDesVides,
        TestCalculTassements,
        TestCalculsIntegres
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    

    
    # Exécuter les tests avec rapport détaillé
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Résumé final
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    print(f"Tests exécutés: {result.testsRun}")
    print(f"Échecs: {len(result.failures)}")
    print(f"Erreurs: {len(result.errors)}")
    
    if result.failures:
        print("\nÉCHECS:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERREURS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
    else:
        print(f"\n {len(result.failures + result.errors)} TESTS ONT ÉCHOUÉ")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # Exécuter tous les tests
    success = run_all_tests()
    
    # Code de sortie pour intégration CI/CD
    exit(0 if success else 1)