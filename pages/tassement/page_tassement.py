from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QComboBox, QCheckBox, QLabel,
    QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QSizePolicy,
    QFrame, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from widgets.widgets_parametre import parametre
from widgets.widgets_parametre import parametre_result_inter
from pages.tassement.graph_viewer_tassement import GraphViewer
from style import APP_STYLE
from widgets.modern_widgets import ModernParameterWidget, ModernGroupBox

from formulas.tassement.formule_ei_tassement import EI_Tassement
from formulas.tassement.formule_ip_ir_tassement import ClassificationSol
from formulas.tassement.formule_cc_tassement import CalculCcStar
from formulas.tassement.formule_e0_tassement import CalculE0Tassement
from formulas.tassement.formule_sigma0 import CalculSigma0
from formulas.tassement.formule_calculer_tassement import CalculTassements
from formulas.tassement.formule_indice_des_vides import CalculIndiceDesVides
from formulas.tassement.formule_ip_ir_tassement import CLASSE_SOL
from pages.Hydro.hydro_layout import assemble_hydro_layout, init_unit_mappings, init_input_limits


class TassementPage(QWidget):
    def __init__(self):
        super().__init__()
        self._other_page = None
        self._syncing = False
        self._custom_ei_edited = False
        self._custom_cc_edited = False
        self._custom_type_edited = False
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)

        # --- Create soil parameter widgets just like Hydro ---
        self.type_sol_input = self._create_line_edit("Value...")
        self.pores_input = self._create_line_edit("Value...")
        self.compress_input = self._create_line_edit("Value...")
        self.density_input = self._create_line_edit("Value...")
        self.density_input.setText("2.67")

        self.type_sol = QComboBox()
        self.type_sol.addItems(["clay%", "wL", "d50ff"])
        self.type_sol_unit = QComboBox()

        self.pores_sol = QComboBox()
        self.pores_sol.addItems(["W", "ρf", "ef*"])
        self.pores_sol_unit = QComboBox()

        self.compress_sol = QComboBox()
        self.compress_sol.addItems(["σ′v"])
        self.compress_sol_unit = QComboBox()

        self.density_sol = QComboBox()
        self.density_sol.addItems(["Gs"])
        self.density_sol_unit = QComboBox()
        self.density_sol_unit.addItems(["-"])

        # Connect combo box changes
        self.type_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('type_sol', idx))
        self.type_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('type_sol_unit', idx))
        self.pores_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('pores_sol', idx))
        self.pores_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('pores_sol_unit', idx))
        self.compress_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('compress_sol', idx))
        self.compress_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('compress_sol_unit', idx))
        self.density_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('density_sol', idx))
        self.density_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('density_sol_unit', idx))

        # --- Results and custom widgets ---
        self.result_EI_input = self._create_line_edit("Value...")
        self.result_Cc_input = self._create_line_edit("Value...")

        self.result_EI_type = QComboBox()
        self.result_EI_type.addItems(["ei*"])
        self.result_EI_unit = QComboBox()
        self.result_EI_unit.addItems(["-"])

        self.result_Cc_type = QComboBox()
        self.result_Cc_type.addItems(["Cc*"])
        self.result_Cc_unit = QComboBox()
        self.result_Cc_unit.addItems(["-"])

        # Dummy widgets for compatibility with hydro_layout (not used in settlement)
        self.result_Ck_type = QComboBox()
        self.result_Ck_type.addItems(["Ck*"])
        self.result_Ck_unit = QComboBox()
        self.result_Ck_unit.addItems(["-"])
        self.result_Ck_input = self._create_line_edit("Value...")

        self.result_type_sol_choice = QComboBox()
        self.result_type_sol_choice.addItems(["Ice-Rich", "Ice-Poor"])
        self.result_type_sol_choice.setCurrentIndex(0)

        # Settlement-specific custom result widgets
        self.result_type_sol_type = QComboBox()
        self.result_type_sol_type.addItems(["Ice content"])
        self.result_type_sol_unit = QComboBox()
        self.result_type_sol_unit.addItems(["-"])

        self.use_custom_params_check = QCheckBox("Use custom results")

        self.result_label = QLabel("Result:")
        self.result_label.setObjectName("ResultLabel")
        self.calculate_button = QPushButton("Calculate")
        self.reset_button = QPushButton("Reset")
        self.graph_viewer = GraphViewer()

        # Initialize common mappings and limits from hydro_layout
        init_unit_mappings(self)
        init_input_limits(self)
        self._connect_unit_updates()
        self._set_initial_units()
        self._adjust_combo_box_widths()

        # --- Use the hydro layout for the common parameters section ---
        assemble_hydro_layout(self)
        
        # --- Add the settlement-specific custom results section ---
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
        self.use_custom_params_check.stateChanged.connect(self._on_custom_check_changed)

    def _setup_ui(self):

        self._set_value_column_width(120)


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
        
        # Enable/disable the input fields
        self.result_EI_input.setEnabled(is_checked)
        self.result_Cc_input.setEnabled(is_checked)
        self.result_type_sol_choice.setEnabled(is_checked)
        
        # Reset custom edit flags if unchecked
        if not is_checked:
            self._custom_ei_edited = False
            self._custom_cc_edited = False
            self._custom_type_edited = False

    def _assemble_modern_layout(self):
        # 5. Indices and Ratios
        self.indices_group = ModernGroupBox("Settlement Custom Parameters")
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

        ei_param = ModernParameterWidget(
            "Initial thawed void ratio",
            self.result_EI_type, self.result_EI_unit, self.result_EI_input
        )

        cc_param = ModernParameterWidget(
            "Thawed soil compression index",
            self.result_Cc_type, self.result_Cc_unit, self.result_Cc_input
        )

        ice_param = ModernParameterWidget(
            "Ice content classification",
            self.result_type_sol_type, self.result_type_sol_unit, self.result_type_sol_choice
        )

        indices_layout.addLayout(indices_headers)
        indices_layout.addWidget(indices_separator)
        indices_layout.addWidget(ei_param)
        indices_layout.addWidget(cc_param)
        indices_layout.addWidget(ice_param)
        self.indices_group.setLayout(indices_layout)

        # Initially hide the custom parameters
        self.indices_group.setVisible(False)
        
        # Add the custom parameters section to the main layout
        main_layout = self.layout()
        if main_layout:
            left_widget = main_layout.itemAt(0).widget()
            if left_widget:
                left_layout = left_widget.layout()
                if left_layout:
                    # Insert before the button layout (which is the last item)
                    left_layout.insertWidget(left_layout.count() - 1, self.indices_group)

        # Connect the checkbox to toggle visibility
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

    def _connect_unit_updates(self):
        self.type_sol.currentIndexChanged.connect(lambda: self.update_unit_options(self.type_sol, self.type_sol_unit))
        self.pores_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.pores_sol, self.pores_sol_unit))
        self.compress_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.compress_sol, self.compress_sol_unit))
        self.density_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.density_sol, self.density_sol_unit))

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
                QMessageBox.warning(self, "Invalid value",
                                    f"The value for {label} must be between {min_val} and {max_val}.")
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
                QMessageBox.warning(self, "Warning",
                                    "The soil is close to the Ice-Rich/Ice-Poor limit. Classification may be sensitive to small changes in parameters.")
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
                    cc_star = CalculCcStar(ei_star, data["type_sol_valeur"], data["type_sol"],
                                           code_etat_custom).calculer()
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
        """Set the reference to the other page for synchronization"""
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

    def _sync_combo(self, combo_name, index):
        if self._other_page and not self._syncing:
            self._other_page._syncing = True
            other_combo = getattr(self._other_page, combo_name)
            other_combo.setCurrentIndex(index)
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