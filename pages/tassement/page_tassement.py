from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QComboBox, QCheckBox, QLabel,
    QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QSizePolicy,
    QGroupBox, QFrame, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from widgets import parametre, parametre_result_inter
from pages.tassement.graph_viewer_tassement import GraphViewer
from style import APP_STYLE

from formulas.tassement.formule_ei_tassement import EI_Tassement
from formulas.tassement.formule_ip_ir_tassement import ClassificationSol
from formulas.tassement.formule_cc_tassement import CalculCcStar
from formulas.tassement.formule_e0_tassement import CalculE0Tassement
from formulas.tassement.formule_sigma0 import CalculSigma0
from formulas.tassement.formule_calculer_tassement import CalculTassements
from formulas.tassement.formule_indice_des_vides import CalculIndiceDesVides
from formulas.tassement.formule_ip_ir_tassement import CLASSE_SOL

class ModernParameterWidget(QWidget):
    """Widget moderne pour les paramètres avec tableau structuré"""
    def __init__(self, param_name, param_widget, unit_widget, value_widget, help_text=""):
        super().__init__()
        self.setup_ui(param_name, param_widget, unit_widget, value_widget, help_text)
    
    def setup_ui(self, param_name, param_widget, unit_widget, value_widget, help_text):
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
    
        name_label = QLabel(param_name)
        name_label.setObjectName("parameterName")
        if help_text:
            name_label.setToolTip(help_text)
        
        # Ajustement des widgets
        if param_widget:
            param_widget.setMinimumWidth(100)
            param_widget.setMaximumWidth(120)
        if unit_widget:
            unit_widget.setMinimumWidth(60)
            unit_widget.setMaximumWidth(80)
        if value_widget:
            value_widget.setMinimumWidth(80)
        
        # Organisation en colonnes
        layout.addWidget(name_label, 0, 0)
        if param_widget:
            layout.addWidget(param_widget, 0, 1)
        if unit_widget:
            layout.addWidget(unit_widget, 0, 2)
        if value_widget:
            layout.addWidget(value_widget, 0, 3)
        
        # Proportions des colonnes
        layout.setColumnStretch(0, 3)  # Nom du paramètre
        layout.setColumnStretch(1, 2)  # Paramètre
        layout.setColumnStretch(2, 1)  # Unité
        layout.setColumnStretch(3, 2)  # Valeur
        
        self.setLayout(layout)


class ModernGroupBox(QGroupBox):
   
    def __init__(self, title, icon=""):
        super().__init__()
        self.setTitle(title)
        self.setObjectName("modernGroupBox")


class TassementPage(QWidget):
    def __init__(self):
        super().__init__()
        self._other_page = None
        self._syncing = False
        self._custom_ei_edited = False
        self._custom_cc_edited = False
        self._custom_type_edited = False
        # Définir une taille minimale plus grande pour éviter le scroll
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        self._setup_ui()
        self._init_unit_mappings()
        self._init_input_limits()
        self._connect_unit_updates()
        self._set_initial_units()
        self._adjust_combo_box_widths()

        self.result_label = QLabel("Result:")
        self.result_label.setObjectName("ResultLabel")
        self.calculate_button = QPushButton("Calculate")
        self.reset_button = QPushButton("Reset")
        self.graph_viewer = GraphViewer()

        self._assemble_modern_layout()
        self._apply_modern_styles()

        self.calculate_button.clicked.connect(lambda: self.calculate(self.result_label))
        self.reset_button.clicked.connect(self.reset)

        # Synchronisation des champs principaux
        self.type_sol_input.textChanged.connect(self._sync_type_sol)
        self.pores_input.textChanged.connect(self._sync_pores)
        self.compress_input.textChanged.connect(self._sync_compress)
        self.density_input.textChanged.connect(self._sync_density)

        # Détection de saisie manuelle custom
        self.result_EI_input.textEdited.connect(self._on_custom_ei_edited)
        self.result_Cc_input.textEdited.connect(self._on_custom_cc_edited)
        self.result_type_sol_choice.activated.connect(self._on_custom_type_edited)
        self.use_custom_params_check.stateChanged.connect(self._on_custom_check_changed)

    def _setup_ui(self):
       
        self.type_sol_input = self._create_line_edit("Value...")
        self.pores_input = self._create_line_edit("Value...")
        self.compress_input = self._create_line_edit("Value...")
        self.density_input = self._create_line_edit("Value...")
        self.density_input.setText("2.67")
       
        self._set_value_column_width(120)

    
        self.type_sol = QComboBox()
        self.type_sol.addItems(["clay%", "wL", "d50ff"])
        self.type_sol_unit = QComboBox()

        self.pores_sol = QComboBox()
        self.pores_sol.addItems(["w", "ρf", "ef*"])
        self.pores_sol_unit = QComboBox()

        self.compress_sol = QComboBox()
        self.compress_sol.addItems(["σ′v"])
        self.compress_sol_unit = QComboBox()

      
        self.density_sol = QComboBox()
        self.density_sol.addItems(["Gs"])
        self.density_sol_unit = QComboBox()
        self.density_sol_unit.addItems(["-"])


        self.result_EI_input = self._create_line_edit("Value...")
        self.result_Cc_input = self._create_line_edit("Value...")

        self.result_type_sol_choice = QComboBox()
        self.result_type_sol_choice.addItems(["Ice-Rich", "Ice-Poor"])
        self.result_type_sol_choice.setCurrentIndex(0)

        # Checkbox pour afficher/masquer les paramètres personnalisés
        self.use_custom_params_check = QCheckBox("Use custom results")

       
        same_width = 120  # ajuste si besoin
        self.result_EI_input.setMinimumWidth(same_width)
        self.result_EI_input.setMaximumWidth(same_width)
        self.result_Cc_input.setMinimumWidth(same_width)
        self.result_Cc_input.setMaximumWidth(same_width)
        self.result_type_sol_choice.setMinimumWidth(same_width)
        self.result_type_sol_choice.setMaximumWidth(same_width)

        self.pores_input.setMinimumWidth(120)  # Ajuste si nécessaire
        self.pores_input.setMaximumWidth(120)  # Ajuste si nécessaire

        self._set_value_column_width(120)

    def _toggle_custom_params(self, state):
        
        is_checked = state == Qt.CheckState.Checked.value
        if hasattr(self, 'indices_group'):
            self.indices_group.setVisible(is_checked)
        self.result_EI_input.setEnabled(is_checked)
        self.result_Cc_input.setEnabled(is_checked)
        self.result_type_sol_choice.setEnabled(is_checked)

    def _assemble_modern_layout(self):
        # Widget principal des paramètres (sans scroll area)
        parameters_widget = QWidget()
        parameters_layout = QVBoxLayout(parameters_widget)
        parameters_layout.setSpacing(12)  # Réduit l'espacement
        parameters_layout.setContentsMargins(10, 10, 10, 10)  # Réduit les marges

        # 1. Soil Type Parameters
        soil_group = ModernGroupBox("Soil Type Parameters")
        soil_layout = QVBoxLayout()
        soil_layout.setSpacing(6)
        
        # En-têtes du tableau
        headers_layout = QGridLayout()
        headers_layout.addWidget(QLabel("<b>Parameter</b>"), 0, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
        headers_layout.addWidget(QLabel("<b>Type</b>"), 0, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        headers_layout.addWidget(QLabel("<b>Unit</b>"), 0, 2, alignment=Qt.AlignmentFlag.AlignHCenter)
        headers_layout.addWidget(QLabel("<b>Value</b>"), 0, 3, alignment=Qt.AlignmentFlag.AlignHCenter)
        headers_layout.setColumnStretch(0, 3)
        headers_layout.setColumnStretch(1, 2)
        headers_layout.setColumnStretch(2, 1)
        headers_layout.setColumnStretch(3, 2)
        
        # Ligne de séparation
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #e2e8f0; height: 1px;")
        
        soil_param = ModernParameterWidget(
            "Clay percentage / Liquid limit / Fine fraction",
            self.type_sol, self.type_sol_unit, self.type_sol_input,
            "Options: Clay percentage (clay%), Liquid limit (wL), Fine fraction median diameter (d50ff)"
        )
        
        soil_layout.addLayout(headers_layout)
        soil_layout.addWidget(separator)
        soil_layout.addWidget(soil_param)
        soil_group.setLayout(soil_layout)

        # 2. Pore-Ice Parameters
        pore_group = ModernGroupBox("Pore-Ice Parameters")
        pore_layout = QVBoxLayout()
        pore_layout.setSpacing(6)
        
        pore_headers = QGridLayout()
        pore_headers.addWidget(QLabel("<b>Parameter</b>"), 0, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
        pore_headers.addWidget(QLabel("<b>Type</b>"), 0, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        pore_headers.addWidget(QLabel("<b>Unit</b>"), 0, 2, alignment=Qt.AlignmentFlag.AlignHCenter)
        pore_headers.addWidget(QLabel("<b>Value</b>"), 0, 3, alignment=Qt.AlignmentFlag.AlignHCenter)
        pore_headers.setColumnStretch(0, 3)
        pore_headers.setColumnStretch(1, 2)
        pore_headers.setColumnStretch(2, 1)
        pore_headers.setColumnStretch(3, 2)
        
        pore_separator = QFrame()
        pore_separator.setFrameShape(QFrame.Shape.HLine)
        pore_separator.setStyleSheet("background-color: #e2e8f0; height: 1px;")
        
        pore_param = ModernParameterWidget(
            "Water content / Frozen density / Frozen void ratio",
            self.pores_sol, self.pores_sol_unit, self.pores_input,
            "Thawed soil initial water content (w), Frozen bulk density (ρf), Frozen void ratio (ef*)"
        )
        
        pore_layout.addLayout(pore_headers)
        pore_layout.addWidget(pore_separator)
        pore_layout.addWidget(pore_param)
        pore_group.setLayout(pore_layout)

        # 3. Soil Compression Parameters
        compression_group = ModernGroupBox("Soil Compression Parameters")
        compression_layout = QVBoxLayout()
        compression_layout.setSpacing(6)
        
        comp_headers = QGridLayout()
        comp_headers.addWidget(QLabel("<b>Parameter</b>"), 0, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
        comp_headers.addWidget(QLabel("<b>Type</b>"), 0, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        comp_headers.addWidget(QLabel("<b>Unit</b>"), 0, 2, alignment=Qt.AlignmentFlag.AlignHCenter)
        comp_headers.addWidget(QLabel("<b>Value</b>"), 0, 3, alignment=Qt.AlignmentFlag.AlignHCenter)
        comp_headers.setColumnStretch(0, 3)
        comp_headers.setColumnStretch(1, 2)
        comp_headers.setColumnStretch(2, 1)
        comp_headers.setColumnStretch(3, 2)
        
        comp_separator = QFrame()
        comp_separator.setFrameShape(QFrame.Shape.HLine)
        comp_separator.setStyleSheet("background-color: #e2e8f0; height: 1px;")
        
        comp_param = ModernParameterWidget(
            "Effective vertical stress",
            self.compress_sol, self.compress_sol_unit, self.compress_input,
            "Effective vertical stress (σ'v)"
        )
        
        compression_layout.addLayout(comp_headers)
        compression_layout.addWidget(comp_separator)
        compression_layout.addWidget(comp_param)
        compression_group.setLayout(compression_layout)

        # 4. Specific Gravity of Solids 
        gs_group = ModernGroupBox("Specific Gravity of Solids")
        gs_layout = QVBoxLayout()
        gs_layout.setSpacing(6)
        
        gs_headers = QGridLayout()
        gs_headers.addWidget(QLabel("<b>Parameter</b>"), 0, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
        gs_headers.addWidget(QLabel("<b>Type</b>"), 0, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        gs_headers.addWidget(QLabel("<b>Unit</b>"), 0, 2, alignment=Qt.AlignmentFlag.AlignHCenter)
        gs_headers.addWidget(QLabel("<b>Value</b>"), 0, 3, alignment=Qt.AlignmentFlag.AlignHCenter)
        gs_headers.setColumnStretch(0, 3)
        gs_headers.setColumnStretch(1, 2)
        gs_headers.setColumnStretch(2, 1)
        gs_headers.setColumnStretch(3, 2)
        
        gs_separator = QFrame()
        gs_separator.setFrameShape(QFrame.Shape.HLine)
        gs_separator.setStyleSheet("background-color: #e2e8f0; height: 1px;")
        
        gs_param = ModernParameterWidget(
            "Specific gravity",
            self.density_sol, self.density_sol_unit, self.density_input,
            "Specific gravity of soil solids"
        )
        
        gs_layout.addLayout(gs_headers)
        gs_layout.addWidget(gs_separator)
        gs_layout.addWidget(gs_param)
        gs_group.setLayout(gs_layout)

        # Checkbox pour paramètres personnalisés
        custom_checkbox_widget = QWidget()
        custom_checkbox_layout = QHBoxLayout(custom_checkbox_widget)
        custom_checkbox_layout.setContentsMargins(0, 8, 0, 2)  
        custom_checkbox_layout.setAlignment(self.use_custom_params_check, Qt.AlignmentFlag.AlignLeft)
        custom_checkbox_layout.addWidget(self.use_custom_params_check)
        custom_checkbox_widget.setMaximumWidth(600) 

        # 5. Indices and Ratios 
        self.indices_group = ModernGroupBox("Indices and Ratios")
        indices_layout = QVBoxLayout()
        indices_layout.setSpacing(6)
        
        indices_headers = QGridLayout()
        indices_headers.addWidget(QLabel("<b>Parameter</b>"), 0, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
        indices_headers.addWidget(QLabel("<b>Type</b>"), 0, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
        indices_headers.addWidget(QLabel("<b>Unit</b>"), 0, 2, alignment=Qt.AlignmentFlag.AlignHCenter)
        indices_headers.addWidget(QLabel("<b>Value</b>"), 0, 3, alignment=Qt.AlignmentFlag.AlignHCenter)
        indices_headers.setColumnStretch(0, 3)
        indices_headers.setColumnStretch(1, 2)
        indices_headers.setColumnStretch(2, 1)
        indices_headers.setColumnStretch(3, 2)
        
        indices_separator = QFrame()
        indices_separator.setFrameShape(QFrame.Shape.HLine)
        indices_separator.setStyleSheet("background-color: #e2e8f0; height: 1px;")
        
        # Créer les comboboxes pour les types et unités
        self.result_EI_type = QComboBox()
        self.result_EI_type.addItems(["ei*"])
        self.result_EI_unit = QComboBox()
        self.result_EI_unit.addItems(["-"])
        
        self.result_Cc_type = QComboBox()
        self.result_Cc_type.addItems(["Cc*"])
        self.result_Cc_unit = QComboBox()
        self.result_Cc_unit.addItems(["-"])
        
        self.result_type_sol_type = QComboBox()
        self.result_type_sol_type.addItems(["Ice content"])
        self.result_type_sol_unit = QComboBox()
        self.result_type_sol_unit.addItems(["-"])
        
       
        ei_param = ModernParameterWidget(
            "Initial thawed void ratio",
            self.result_EI_type, self.result_EI_unit, self.result_EI_input,
            "Initial thawed void ratio (ei*)"
        )
        
        cc_param = ModernParameterWidget(
            "Thawed soil compression index",
            self.result_Cc_type, self.result_Cc_unit, self.result_Cc_input,
            "Thawed soil compression index (Cc*)"
        )
        
        ice_param = ModernParameterWidget(
            "Ice content classification",
            self.result_type_sol_type, self.result_type_sol_unit, self.result_type_sol_choice,
            "Ice content: Ice-Rich or Ice-Poor"
        )
        
        indices_layout.addLayout(indices_headers)
        indices_layout.addWidget(indices_separator)
        indices_layout.addWidget(ei_param)
        indices_layout.addWidget(cc_param)
        indices_layout.addWidget(ice_param)
        self.indices_group.setLayout(indices_layout)
        
      
        self.indices_group.setVisible(False)

      
        parameters_layout.addWidget(soil_group)
        parameters_layout.addWidget(pore_group)
        parameters_layout.addWidget(compression_group)
        parameters_layout.addWidget(gs_group)
        parameters_layout.addWidget(custom_checkbox_widget)
        parameters_layout.addWidget(self.indices_group)
        
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.calculate_button)
        button_layout.addStretch()
        parameters_layout.addLayout(button_layout)
        
        # Panel des résultats
        results_panel = QWidget()
        results_panel.setObjectName("resultsPanel")
        results_layout = QVBoxLayout(results_panel)
        results_layout.setContentsMargins(10, 10, 10, 10)
        results_layout.setSpacing(10)
        
        # Titre des résultats
        results_title = QLabel("Settlement Results")
        results_title.setObjectName("resultsTitle")
        results_layout.addWidget(results_title)
        
        # Zone des résultats
        results_layout.addWidget(self.result_label)
        
        # Graphique
        graph_title = QLabel("Void Ratio vs Effective Stress")
        graph_title.setObjectName("graphTitle")
        results_layout.addWidget(graph_title)
        results_layout.addWidget(self.graph_viewer)

        # Layout principal 
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(parameters_widget, 1)
        main_layout.addWidget(results_panel, 1)
        
        self.setLayout(main_layout)

        self.use_custom_params_check.stateChanged.connect(self._toggle_custom_params)

    def _apply_modern_styles(self):
        self.setStyleSheet(APP_STYLE)

    def _create_line_edit(self, placeholder):
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        return edit

    def _adjust_combo_box_widths(self):
        for combo in [self.type_sol, self.type_sol_unit,
                      self.pores_sol, self.pores_sol_unit,
                      self.compress_sol, self.compress_sol_unit,
                      self.density_sol, self.density_sol_unit,
                      self.result_type_sol_choice]:
            combo.setMinimumWidth(100) 
            combo.setMaximumWidth(120)  
            combo.setMinimumHeight(20)
        
    def _init_unit_mappings(self):
        self.type_unit_mapping = {
            self.type_sol: {"clay%": ["%"], "wL": ["%"], "d50ff": ["mm"]},
            self.pores_sol: {"w": ["kg/kg"], "ρf": ["kg/m³", "g/cm³"], "ef*": ["Direct"]},
            self.compress_sol: {"σ′v": ["kPa"]},
            self.density_sol: {"Gs": ["-"]}
        }

    def _init_input_limits(self):
        self.input_limits = {
            self.type_sol_unit: {"%": (1, 100), "mm": (0.001, 0.1)},
            self.pores_sol_unit: {
                "kg/kg": (0, float('inf')), "kg/m³": (900, 3000),
                "g/cm³": (0.9, 3), "Direct": (0, float('inf'))
            },
            self.compress_sol_unit: {"kPa": (0, float('inf'))},
            self.density_sol_unit: {"-": (1, 4)}
        }

    def _connect_unit_updates(self):
        self.type_sol.currentIndexChanged.connect(lambda: self.update_unit_options(self.type_sol, self.type_sol_unit))
        self.pores_sol.currentIndexChanged.connect(lambda: self.update_unit_options(self.pores_sol, self.pores_sol_unit))
        self.compress_sol.currentIndexChanged.connect(lambda: self.update_unit_options(self.compress_sol, self.compress_sol_unit))
        self.density_sol.currentIndexChanged.connect(lambda: self.update_unit_options(self.density_sol, self.density_sol_unit))

    def _set_initial_units(self):
        self.update_unit_options(self.type_sol, self.type_sol_unit)
        self.update_unit_options(self.pores_sol, self.pores_sol_unit)
        self.update_unit_options(self.compress_sol, self.compress_sol_unit)
        self.update_unit_options(self.density_sol, self.density_sol_unit)

    def update_unit_options(self, type_combo: QComboBox, unit_combo: QComboBox):
        selected_type = type_combo.currentText()
        units = self.type_unit_mapping.get(type_combo, {}).get(selected_type, [])
        if units:
            current_unit = unit_combo.currentText()
            unit_combo.blockSignals(True)
            unit_combo.clear()
            unit_combo.addItems(units)
            if current_unit in units:
                unit_combo.setCurrentIndex(units.index(current_unit))
            unit_combo.blockSignals(False)

    def validate_input(self, value: float, unit_combo):
        if unit_combo is False:
            return (1 <= value <= 4), 1, 4
        unit = unit_combo.currentText()
        limits = self.input_limits.get(unit_combo, {}).get(unit)
        if limits:
            min_val, max_val = limits
            return (min_val <= value <= max_val), min_val, max_val
        return True, None, None

    def calculate(self, result_label):
        try:
            data = {
                'type_sol_valeur': float(self.type_sol_input.text()),
                'valeur_pore': float(self.pores_input.text()),
                'sigma_v': float(self.compress_input.text()),
                'Gs': float(self.density_input.text()),
                'type_pore': self.pores_sol.currentText(),
                'type_sol': self.type_sol.currentText()
            }
        except ValueError:
            QMessageBox.critical(self, "Value Error", "Please enter valid numerical values.")
            return

        # Validation des entrées
        validations = [
            (data["type_sol_valeur"], self.type_sol_unit, self.type_sol.currentText()),
            (data["valeur_pore"], self.pores_sol_unit, self.pores_sol.currentText()),
            (data["sigma_v"], self.compress_sol_unit, self.compress_sol.currentText()),
            (data["Gs"], False, "Gs")
        ]
        for value, unit_combo, label in validations:
            valid, min_val, max_val = self.validate_input(value, unit_combo)
            if not valid:
                QMessageBox.warning(self, "Invalid value", f"The value for {label} must be between {min_val} and {max_val}.")
                return

        if self.pores_sol_unit.currentText() == "kg/m³":
            data["valeur_pore"] /= 1000
        if data["type_pore"] == "ρf" and data["valeur_pore"] >= data["Gs"]:
            QMessageBox.warning(self, "Invalid value", "Make sure Gs > ρf")
            return

        try:
            # 1. Calcul ei*
            ei_star_calc = EI_Tassement(data["valeur_pore"], data["Gs"], data["type_pore"]).calculer()
            # 2. Classification (IR ou IP)
            classification = ClassificationSol(ei_star_calc, data["type_sol_valeur"], data["type_sol"])
            code_etat = classification.classer()
            if code_etat == -1:
                QMessageBox.warning(self, "Warning", "Soil classification unknown")
                return
            if classification.is_near_limit:
                QMessageBox.warning(self, "Warning", "The soil is close to the Ice-Rich/Ice-Poor limit. Classification may be sensitive to small changes in parameters.")
            detected_type = CLASSE_SOL[code_etat]
            result_label.setText(f"Soil type : {detected_type}")

            # 3. Gestion des paramètres custom
            if self.use_custom_params_check.isChecked():
                # EI*
                if not self._custom_ei_edited:
                    self.result_EI_input.setText(f"{ei_star_calc:.3f}")
                    ei_star = ei_star_calc
                else:
                    try:
                        ei_star = float(self.result_EI_input.text())
                    except ValueError:
                        QMessageBox.warning(self, "Invalid ei*", "Please enter a valid number for ei*.")
                        return
                # Type de sol
                if not self._custom_type_edited:
                    self.result_type_sol_choice.setCurrentIndex(0 if code_etat == 0 else 1)
                    code_etat_custom = code_etat
                else:
                    code_etat_custom = 0 if self.result_type_sol_choice.currentText() == "Ice-Rich" else 1
                # Cc*
                if not self._custom_cc_edited:
                    cc_star = CalculCcStar(ei_star, data["type_sol_valeur"], data["type_sol"], code_etat_custom).calculer()
                    self.result_Cc_input.setText(f"{cc_star:.3f}")
                else:
                    try:
                        cc_star = float(self.result_Cc_input.text())
                    except ValueError:
                        QMessageBox.warning(self, "Invalid Cc*", "Please enter a valid number for Cc*.")
                        return
                code_etat = code_etat_custom
            else:
                ei_star = ei_star_calc
                self.result_EI_input.setText(f"{ei_star:.3f}")
                cc_star = CalculCcStar(ei_star, data["type_sol_valeur"], data["type_sol"], code_etat).calculer()
                self.result_Cc_input.setText(f"{cc_star:.3f}")
                self.result_type_sol_choice.setCurrentIndex(0 if code_etat == 0 else 1)

            # 4. Calculs restants
            e0_star = CalculE0Tassement(ei_star, cc_star, code_etat).calculer()
            sigma0 = CalculSigma0(e0_star, data["type_sol"], data["type_sol_valeur"], code_etat).calculer()
            indice_vides = CalculIndiceDesVides(e0_star, cc_star, data["sigma_v"], sigma0).calculer()
            ef = data["valeur_pore"] if data["type_pore"] == "ef*" else ei_star * 1.09
            s1, s2, s_total = CalculTassements(ef, e0_star, indice_vides).calculer()

            # 5. Affichage texte (toujours)
            result_label.setText(
                f"Result: Total settlement S = {s_total:.2f} %\n"
                f"Settlement S1 (ice melt) = {s1:.2f} %\n"
                f"Settlement S2 (compression) = {s2:.2f} %"
            )

            # 6. Mise à jour du graphique
            self.graph_viewer.set_is_tassement(True)
            self.graph_viewer.set_ei_value(ei_star)
            self.graph_viewer.set_graph_data(self.register(
                s_total, ei_star, cc_star, e0_star, sigma0, indice_vides, s1, s2
            ))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Calcul error: {e}")


    def reset(self):
        for input_widget in [
            self.type_sol_input, self.pores_input, self.compress_input,
            self.density_input, self.result_EI_input, self.result_Cc_input
        ]:
            input_widget.clear()
        for combo_box in [
            self.type_sol, self.type_sol_unit,
            self.pores_sol, self.pores_sol_unit,
            self.compress_sol, self.compress_sol_unit,
            self.result_type_sol_choice
        ]:
            combo_box.setCurrentIndex(0)
        self.use_custom_params_check.setChecked(False)
        self.result_EI_input.setEnabled(False)
        self.result_Cc_input.setEnabled(False)
        self.result_type_sol_choice.setEnabled(False)
        self.result_type_sol_choice.setCurrentIndex(-1)
        self.result_label.setText("Result:")
        self.graph_viewer.clear_graph()

    def register(self, s_total, ei_star, cc_star, e0_star, sigma0, indice_vides, s1, s2):
        return {
            "result": sigma0,
            "kv0": float(self.compress_input.text()),
            "sigma_v": float(self.compress_input.text()),
            "E0": e0_star,
            "Cc": cc_star,
            "ei_star": ei_star,
            "s_total": s_total,
            "s1": s1,
            "s2": s2,
            "cc_star": cc_star,
            "e0_star": e0_star,
            "sigma0": sigma0,
            "indice_vides": indice_vides
        }

    def _set_value_column_width(self, width=120):
        self.result_EI_input.setMinimumWidth(width)
        self.result_EI_input.setMaximumWidth(width)
        self.result_Cc_input.setMinimumWidth(width)
        self.result_Cc_input.setMaximumWidth(width)
        self.result_type_sol_choice.setMinimumWidth(width)
        self.result_type_sol_choice.setMaximumWidth(width)
     
    def _set_value_column_width(self, width=120):
        self.type_sol_input.setMinimumWidth(width)
        self.type_sol_input.setMaximumWidth(width)
        self.pores_input.setMinimumWidth(width)
        self.pores_input.setMaximumWidth(width)
        self.compress_input.setMinimumWidth(width)
        self.compress_input.setMaximumWidth(width)
        self.density_input.setMinimumWidth(width)
        self.density_input.setMaximumWidth(width)
        # Pour les résultats optionnels
        if hasattr(self, 'result_EI_input'):
            self.result_EI_input.setMinimumWidth(width)
            self.result_EI_input.setMaximumWidth(width)
        if hasattr(self, 'result_Cc_input'):
            self.result_Cc_input.setMinimumWidth(width)
            self.result_Cc_input.setMaximumWidth(width)
        if hasattr(self, 'result_Ck_input'):
            self.result_Ck_input.setMinimumWidth(width)
            self.result_Ck_input.setMaximumWidth(width)

    def set_other_page(self, other_page):
        self._other_page = other_page

    def _sync_type_sol(self, value):
        if self._other_page and not self._syncing:
            self._other_page._syncing = True
            self._other_page.type_sol_input.setText(value)
            self._other_page._syncing = False
    def _sync_pores(self, value):
        if self._other_page and not self._syncing:
            self._other_page._syncing = True
            self._other_page.pores_input.setText(value)
            self._other_page._syncing = False
    def _sync_compress(self, value):
        if self._other_page and not self._syncing:
            self._other_page._syncing = True
            self._other_page.compress_input.setText(value)
            self._other_page._syncing = False
    def _sync_density(self, value):
        if self._other_page and not self._syncing:
            self._other_page._syncing = True
            self._other_page.density_input.setText(value)
            self._other_page._syncing = False

    def _on_custom_ei_edited(self):
        self._custom_ei_edited = True
    def _on_custom_cc_edited(self):
        self._custom_cc_edited = True
    def _on_custom_type_edited(self):
        self._custom_type_edited = True
    def _on_custom_check_changed(self, state):
        if state == Qt.CheckState.Checked.value:
            self._custom_ei_edited = False
            self._custom_cc_edited = False
            self._custom_type_edited = False
