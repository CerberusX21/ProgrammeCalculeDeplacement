from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QComboBox, QCheckBox, QMessageBox
from PyQt6.QtCore import Qt
from widgets import parametre, parametre_result_inter, parametre_result_combo
from formulas.tassement.formule_ei_tassement import EI_Tassement
from formulas.tassement.formule_ip_ir_tassement import ClassificationSol
from formulas.tassement.formule_cc_tassement import CalculCcStar
from formulas.tassement.formule_e0_tassement import CalculE0Tassement
from formulas.tassement.formule_sigma0 import CalculSigma0
from formulas.tassement.formule_calculer_tassement import CalculTassements
from formulas.tassement.formule_indice_des_vides import CalculIndiceDesVides
from formulas.tassement.formule_ip_ir_tassement import CLASSE_SOL



class TassementPage(QWidget):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._init_unit_mappings()
        self._init_input_limits()
        self._connect_unit_updates()
        self._set_initial_units()
        self._adjust_combo_box_widths()

    def _setup_ui(self):
        self.layout = QFormLayout()
        self.layout.setFormAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.layout.setHorizontalSpacing(20)
        self.layout.setVerticalSpacing(15)
        self.layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        self.setLayout(self.layout)

        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setContentsMargins(10, 10, 10, 10)

        self.type_sol_input = self._create_line_edit("Value...")
        self.pores_input = self._create_line_edit("Value...")
        self.compress_input = self._create_line_edit("Value...")
        self.density_input = self._create_line_edit("Value...")

        self.type_sol = QComboBox()
        self.type_sol.addItems(["clay%", "wL", "d50ff"])
        self.type_sol_unit = QComboBox()

        self.pores_sol = QComboBox()
        self.pores_sol.addItems(["w", "ρf", "ef*"])
        self.pores_sol_unit = QComboBox()

        self.compress_sol = QComboBox()
        self.compress_sol.addItems(["σ′v"])
        self.compress_sol_unit = QComboBox()

        self.result_EI_input, self.result_EI_check = self._create_optional_input("Value...")
        self.result_Cc_input, self.result_Cc_check = self._create_optional_input("Value...")

        self.result_type_sol_check = QCheckBox("Use custom result?")
        self.result_type_sol_choice = QComboBox()
        self.result_type_sol_choice.addItems(["Ice-Rich", "Ice-Poor"]) 
        self.result_type_sol_choice.setCurrentIndex(-1)
        self.result_type_sol_choice.setEnabled(False)
        self.result_type_sol_check.stateChanged.connect(
            lambda state: self.result_type_sol_choice.setEnabled(state == Qt.CheckState.Checked.value)
        )

        self.layout.addRow("Soil type:", parametre(self.type_sol_unit, self.type_sol, self.type_sol_input))
        self.layout.addRow("Pore type:", parametre(self.pores_sol_unit, self.pores_sol, self.pores_input))
        self.layout.addRow("Compression:", parametre(self.compress_sol_unit, self.compress_sol, self.compress_input))
        self.layout.addRow("Gs type:", self.density_input)
        self.layout.addRow("Result Ei:", parametre_result_inter(self.result_EI_check, self.result_EI_input))
        self.layout.addRow("Result Cc*:", parametre_result_inter(self.result_Cc_check, self.result_Cc_input))
        self.layout.addRow("Result soil:", parametre_result_combo(self.result_type_sol_check, self.result_type_sol_choice))

    def _create_line_edit(self, placeholder):
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        return edit

    def _create_optional_input(self, placeholder):
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        checkbox = QCheckBox("Use custom result?")
        edit.setEnabled(False)
        checkbox.stateChanged.connect(lambda state: edit.setEnabled(state == Qt.CheckState.Checked.value))
        return edit, checkbox

    def _adjust_combo_box_widths(self):
        for combo in [self.type_sol, self.type_sol_unit,
                      self.pores_sol, self.pores_sol_unit,
                      self.compress_sol, self.compress_sol_unit,
                      self.result_type_sol_choice]:
            combo.setMinimumWidth(80)
            combo.setMaximumWidth(120)
            combo.setFixedHeight(28)

    def _init_unit_mappings(self):
        self.type_unit_mapping = {
            self.type_sol: {
                "clay%": ["%"],
                "wL": ["%"],
                "d50ff": ["mm"]
            },
            self.pores_sol: {
                "w": ["kg/kg"],
                "ρf": ["kg/m³", "g/cm³"],
                "ef*": ["Direct"]
            },
            self.compress_sol: {
                "σ′v": ["kPa"]
            }
        }

    def _init_input_limits(self):
        self.input_limits = {
            self.type_sol_unit: {
                "%": (1, 100),
                "mm": (0.001, 0.1)
            },
            self.pores_sol_unit: {
                "kg/kg": (0, float('inf')),
                "kg/m³": (900, 3000),
                "g/cm³": (0.9, 3),
                "Direct": (0, float('inf')),
            },
            self.compress_sol_unit: {
                "kPa": (0, float('inf'))
            }
        }

    def _connect_unit_updates(self):
        self.type_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.type_sol, self.type_sol_unit))
        self.pores_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.pores_sol, self.pores_sol_unit))
        self.compress_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.compress_sol, self.compress_sol_unit))

    def _set_initial_units(self):
        self.update_unit_options(self.type_sol, self.type_sol_unit)
        self.update_unit_options(self.pores_sol, self.pores_sol_unit)
        self.update_unit_options(self.compress_sol, self.compress_sol_unit)

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

        validations = [
            (data["type_sol_valeur"], self.type_sol_unit, self.type_sol.currentText()),
            (data["valeur_pore"], self.pores_sol_unit, self.pores_sol.currentText()),
            (data["sigma_v"], self.compress_sol_unit, self.compress_sol.currentText()),
            (data["Gs"], False, "Gs")
        ]

        for value, unit_combo, label in validations:
            valid, min_val, max_val = self.validate_input(value, unit_combo)
            if not valid:
                QMessageBox.warning(self, "Valeur invalide",
                                    f"The value for {label} must be between {min_val} and {max_val}.")
                return

        if self.pores_sol_unit.currentText() == "kg/m³":
            data["valeur_pore"] = data["valeur_pore"] / 1000

        if data["type_pore"] == "ρf":
            if data["valeur_pore"] >= data["Gs"]:
                QMessageBox.warning(self, "Invalid value", "Make sure Gs > ρf")
                return

        try:
            # Calculate ei* based on input values
            ei_calculator = EI_Tassement(data["valeur_pore"], data["Gs"], data["type_pore"])
            ei_star_calc = ei_calculator.calculer()
            
            # Use custom ei* value if provided, otherwise use calculated value
            ei_star = float(self.result_EI_input.text()) if self.result_EI_check.isChecked() else ei_star_calc
            
            # Always display the calculated value even if not using it
            if not self.result_EI_check.isChecked():
                self.result_EI_input.setText(f"{ei_star:.2f}")

            # Use custom Cc* value if provided, otherwise calculate it
            cc_star = float(self.result_Cc_input.text()) if self.result_Cc_check.isChecked() else None

            # Classify soil type based on ei*
            classification = ClassificationSol(ei_star, data["type_sol_valeur"], data["type_sol"])
            code_etat = classification.classer()

            if code_etat == -1:
                QMessageBox.warning(self, "Warning", "Soil classification unknown")
                return

            detected_type = CLASSE_SOL[code_etat]
            result_label.setText(f"Soil type : {detected_type}")

            # Handle soil type selection
            if self.result_type_sol_check.isChecked():
                selected_type = self.result_type_sol_choice.currentText()
                code_etat = 0 if selected_type == "Ice-Rich" else 1
            elif code_etat == 2:
                QMessageBox.warning(self, "Transition zone",
                    "The soil is in a transition zone. You must manually select either Ice-Rich or Ice-Poor.")
                self.result_type_sol_check.setChecked(True)
                self.result_type_sol_choice.setEnabled(True)
                return

            if not self.result_type_sol_check.isChecked():
                soil_type_index = 0 if code_etat == 0 else 1
                self.result_type_sol_choice.setCurrentIndex(soil_type_index)

            if self.result_type_sol_choice.currentIndex() == -1:
                QMessageBox.warning(self, "Selection Required", "Please manually select a soil type.")
                return

            # Calculate Cc* if not provided
            if cc_star is None:
                cc_star = CalculCcStar(ei_star, data["type_sol_valeur"], data["type_sol"], code_etat).calculer()
                self.result_Cc_input.setText(f"{cc_star:.6f}")

            # Calculate remaining parameters
            e0_star = CalculE0Tassement(ei_star, cc_star, code_etat).calculer()
            sigma0 = CalculSigma0(e0_star, data["type_sol"], data["type_sol_valeur"], code_etat).calculer()
            indice_vides = CalculIndiceDesVides(e0_star, cc_star, data["sigma_v"], sigma0).calculer()
            
            # Calculate settlement
            ef = data["valeur_pore"] if data["type_pore"] == "ef*" else ei_star * 1.09
            s1, s2, s_total = CalculTassements(ef, e0_star, indice_vides).calculer()

            result_label.setText(
                f"Result: Total settlement S = {s_total:.2f} %\n"
                f"Settlement S1 (ice melt) = {s1:.2f} %\n"
                f"Settlement S2 (compression) = {s2:.2f} %"
            )

            # Return complete results dictionary including ei_star
            return self.register(s_total, ei_star, cc_star, e0_star, sigma0, indice_vides, s1, s2)

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

        for check_box in [self.result_EI_check, self.result_Cc_check, self.result_type_sol_check]:
            check_box.setChecked(False)

        self.result_EI_input.setEnabled(False)
        self.result_Cc_input.setEnabled(False)
        self.result_type_sol_choice.setEnabled(False)
        self.result_type_sol_choice.setCurrentIndex(-1)
        self.result_type_sol_check.setChecked(False)
        

    def register(self, s_total, ei_star, cc_star, e0_star, sigma0, indice_vides, s1, s2):
        return {
            "result": sigma0,
            "kv0": float(self.compress_input.text()),
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