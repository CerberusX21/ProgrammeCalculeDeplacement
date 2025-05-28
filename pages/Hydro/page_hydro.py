from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit,
    QLabel, QPushButton, QMessageBox, QCheckBox, QSizePolicy, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from style import APP_STYLE
from pages.Hydro.graph_viewer_hydro import GraphViewer
from formulas.hydraulique.FormulaClay import FormulaClay
from formulas.hydraulique.FormulaLiquid import FormulaLiquid
from formulas.hydraulique.FormulaD50ff import FormulaD50ff
from pages.tassement.page_tassement import ModernParameterWidget, ModernGroupBox


class HydroPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1400, 900)
        self.setStyleSheet(APP_STYLE)
        self._other_page = None
        self._syncing = False
        self._custom_ei_edited = False
        self._custom_cc_edited = False
        self._custom_ck_edited = False
        self.graph_data = None
        self._init_widgets()
        self._init_unit_mappings()
        self._init_input_limits()
        self._connect_unit_updates()
        self._set_initial_units()
        self.result_label = QLabel("Result:")
        self.result_label.setObjectName("ResultLabel")
        self.graph_viewer = GraphViewer()
        self.calculate_button = QPushButton("Calculate")
        self.reset_button = QPushButton("Reset")
        self.calculate_button.clicked.connect(self.calculate)
        self.reset_button.clicked.connect(self.reset)
        self._assemble_layout()
        # Pour syncroniser les données entre les pages
        self.type_sol_input.textChanged.connect(self._sync_type_sol)
        self.pores_input.textChanged.connect(self._sync_pores)
        self.compress_input.textChanged.connect(self._sync_compress)
        self.density_input.textChanged.connect(self._sync_density)
        # Détection de saisie manuelle 
        self.result_EI_input.textEdited.connect(self._on_custom_ei_edited)
        self.result_Cc_input.textEdited.connect(self._on_custom_cc_edited)
        self.result_Ck_input.textEdited.connect(self._on_custom_ck_edited)
        self.use_custom_params_check.stateChanged.connect(self._on_custom_check_changed)

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
    def _on_custom_ck_edited(self):
        self._custom_ck_edited = True
    def _on_custom_check_changed(self, state):
        if state == Qt.CheckState.Checked.value:
            self._custom_ei_edited = False
            self._custom_cc_edited = False
            self._custom_ck_edited = False

    def _init_widgets(self):
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
        self.pores_sol.addItems(["W", "ρf", "ef*"])
        self.pores_sol_unit = QComboBox()

        self.compress_sol = QComboBox()
        self.compress_sol.addItems(["σ′v"])
        self.compress_sol_unit = QComboBox()

        self.result_EI_input, self.result_EI_check = self._create_optional_input("Value...")
        self.result_Cc_input, self.result_Cc_check = self._create_optional_input("Value...")
        self.result_Ck_input, self.result_Ck_check = self._create_optional_input("Value...")

        self.density_sol = QComboBox()
        self.density_sol.addItems(["Gs"])
        self.density_sol_unit = QComboBox()
        self.density_sol_unit.addItems(["-"])

        self.result_EI_input = self._create_line_edit("Value...")
        self.result_Cc_input = self._create_line_edit("Value...")
        self.result_Ck_input = self._create_line_edit("Value...")

        self.result_EI_type = QComboBox()
        self.result_EI_type.addItems(["ei*"])
        self.result_EI_unit = QComboBox()
        self.result_EI_unit.addItems(["-"])

        self.result_Cc_type = QComboBox()
        self.result_Cc_type.addItems(["Cc*"])
        self.result_Cc_unit = QComboBox()
        self.result_Cc_unit.addItems(["-"])

        self.result_Ck_type = QComboBox()
        self.result_Ck_type.addItems(["Ck*"])
        self.result_Ck_unit = QComboBox()
        self.result_Ck_unit.addItems(["-"])

    def _assemble_layout(self):
        main_layout = QHBoxLayout()

        # --- Paramètres à gauche ---
        parameters_widget = QWidget()
        parameters_layout = QVBoxLayout(parameters_widget)
        parameters_layout.setSpacing(12)
        parameters_layout.setContentsMargins(10, 10, 10, 10)

        #  our les headers
        def make_headers():
            headers_layout = QGridLayout()
            headers_layout.addWidget(QLabel("<b>Parameter</b>"), 0, 0, alignment=Qt.AlignmentFlag.AlignHCenter)
            headers_layout.addWidget(QLabel("<b>Type</b>"), 0, 1, alignment=Qt.AlignmentFlag.AlignHCenter)
            headers_layout.addWidget(QLabel("<b>Unit</b>"), 0, 2, alignment=Qt.AlignmentFlag.AlignHCenter)
            headers_layout.addWidget(QLabel("<b>Value</b>"), 0, 3, alignment=Qt.AlignmentFlag.AlignHCenter)
            headers_layout.setColumnStretch(0, 3)
            headers_layout.setColumnStretch(1, 2)
            headers_layout.setColumnStretch(2, 1)
            headers_layout.setColumnStretch(3, 2)
            return headers_layout

        def make_separator():
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("background-color: #e2e8f0; height: 1px;")
            return sep

        # Soil group
        soil_group = ModernGroupBox("Soil Type Parameters")
        soil_layout = QVBoxLayout()
        soil_layout.addLayout(make_headers())
        soil_layout.addWidget(make_separator())
        soil_param = ModernParameterWidget(
            "Clay percentage / Liquid limit / Fine fraction",
            self.type_sol, self.type_sol_unit, self.type_sol_input,
            "Options: Clay percentage (clay%), Liquid limit (wL), Fine fraction median diameter (d50ff)"
        )
        soil_layout.addWidget(soil_param)
        soil_group.setLayout(soil_layout)

        # Pore group
        pore_group = ModernGroupBox("Pore-Ice Parameters")
        pore_layout = QVBoxLayout()
        pore_layout.addLayout(make_headers())
        pore_layout.addWidget(make_separator())
        pore_param = ModernParameterWidget(
            "Water content / Frozen density / Frozen void ratio",
            self.pores_sol, self.pores_sol_unit, self.pores_input,
            "Thawed soil initial water content (W), Frozen bulk density (ρf), Frozen void ratio (ef*)"
        )
        pore_layout.addWidget(pore_param)
        pore_group.setLayout(pore_layout)

        # Compression group
        compress_group = ModernGroupBox("Soil Compression Parameters")
        compress_layout = QVBoxLayout()
        compress_layout.addLayout(make_headers())
        compress_layout.addWidget(make_separator())
        compress_param = ModernParameterWidget(
            "Effective vertical stress",
            self.compress_sol, self.compress_sol_unit, self.compress_input,
            "Effective vertical stress (σ'v)"
        )
        compress_layout.addWidget(compress_param)
        compress_group.setLayout(compress_layout)

        # Gs group (Specific Gravity) - même format que Settlement
        gs_group = ModernGroupBox("Specific Gravity of Solids")
        gs_layout = QVBoxLayout()
        gs_layout.addLayout(make_headers())
        gs_layout.addWidget(make_separator())
        self.density_sol = QComboBox()
        self.density_sol.addItems(["Gs"])
        self.density_sol_unit = QComboBox()
        self.density_sol_unit.addItems(["-"])
        gs_param = ModernParameterWidget(
            "Specific gravity",
            self.density_sol, self.density_sol_unit, self.density_input,
            "Specific gravity of soil solids"
        )
        gs_layout.addWidget(gs_param)
        gs_group.setLayout(gs_layout)

        # Checkbox pour paramètres personnalisés
        self.use_custom_params_check = QCheckBox("Use custom results")
        self.use_custom_params_check.stateChanged.connect(self._toggle_custom_params)
        custom_checkbox_widget = QWidget()
        custom_checkbox_layout = QHBoxLayout(custom_checkbox_widget)
        custom_checkbox_layout.setContentsMargins(0, 8, 0, 2)
        custom_checkbox_layout.setAlignment(self.use_custom_params_check, Qt.AlignmentFlag.AlignLeft)
        custom_checkbox_layout.addWidget(self.use_custom_params_check)
        custom_checkbox_widget.setMaximumWidth(600)

        # Results group (pour ei*, Cc*, Ck*)
        results_group = ModernGroupBox("Indices and Ratios")
        results_layout = QVBoxLayout()
        results_layout.addLayout(make_headers())
        results_layout.addWidget(make_separator())
        # ei*
        ei_param = ModernParameterWidget(
            "Initial thawed void ratio",
            self.result_EI_type, self.result_EI_unit, self.result_EI_input,
            "Initial thawed void ratio (ei*)"
        )
        # Cc*
        cc_param = ModernParameterWidget(
            "Thawed soil compression index",
            self.result_Cc_type, self.result_Cc_unit, self.result_Cc_input,
            "Thawed soil compression index (Cc*)"
        )
        # Ck*
        ck_param = ModernParameterWidget(
            "Hydraulic conductivity index",
            self.result_Ck_type, self.result_Ck_unit, self.result_Ck_input,
            "Hydraulic conductivity index (Ck*)"
        )
        results_layout.addWidget(ei_param)
        results_layout.addWidget(cc_param)
        results_layout.addWidget(ck_param)
        results_group.setLayout(results_layout)
        results_group.setVisible(False)  # Masqué par défaut

        # Ajout des groupes au layout
        parameters_layout.addWidget(soil_group)
        parameters_layout.addWidget(pore_group)
        parameters_layout.addWidget(compress_group)
        parameters_layout.addWidget(gs_group)
        parameters_layout.addWidget(custom_checkbox_widget)
        parameters_layout.addWidget(results_group)

        # Boutons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.calculate_button)
        button_layout.addStretch()
        parameters_layout.addLayout(button_layout)

        # --- Résultats à droite ---
        results_panel = QWidget()
        results_panel.setObjectName("resultsPanel")
        results_layout_right = QVBoxLayout(results_panel)
        results_layout_right.setContentsMargins(10, 10, 10, 10)
        results_layout_right.setSpacing(10)

        results_title = QLabel("Hydraulic Results")
        results_title.setObjectName("resultsTitle")
        results_layout_right.addWidget(results_title)
        results_layout_right.addWidget(self.result_label)

        graph_title = QLabel("Hydraulic Conductivity Graph")
        graph_title.setObjectName("graphTitle")
        results_layout_right.addWidget(graph_title)
        results_layout_right.addWidget(self.graph_viewer)

        # --- Layout principal ---
        main_layout.addWidget(parameters_widget, 1)
        main_layout.addWidget(results_panel, 1)
        self.setLayout(main_layout)

        # Stocke pour accès dans d'autres méthodes
        self.results_group = results_group

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

    def _init_unit_mappings(self):
        self.type_unit_mapping = {
            self.type_sol: {"clay%": ["%"], "wL": ["%"], "d50ff": ["mm"]},
            self.pores_sol: {"W": ["kg/kg"], "ρf": ["kg/m3", "g/cm3"], "ef*": ["Direct"]},
            self.compress_sol: {"σ′v": ["kPa"]},
        }

    def _init_input_limits(self):
        self.input_limits = {
            self.type_sol_unit: {"%": (1, 100), "mm": (0.001, 0.1)},
            self.pores_sol_unit: {
                "kg/kg": (0, float('inf')), "kg/m3": (900, 3000),
                "g/cm3": (0.9, 3), "Direct": (0, float('inf'))
            },
            self.compress_sol_unit: {"kPa": (0, float('inf'))},
        }

    def _connect_unit_updates(self):
        self.type_sol.currentIndexChanged.connect(lambda: self.update_unit_options(self.type_sol, self.type_sol_unit))
        self.pores_sol.currentIndexChanged.connect(lambda: self.update_unit_options(self.pores_sol, self.pores_sol_unit))
        self.compress_sol.currentIndexChanged.connect(lambda: self.update_unit_options(self.compress_sol, self.compress_sol_unit))

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

    def calculate(self):
        try:
            data = {
                'type_sol': float(self.type_sol_input.text()),
                'pores_sol': float(self.pores_input.text()),
                'compress_sol': float(self.compress_input.text()),
                'density_sol': float(self.density_input.text()),
                'water': self.pores_sol.currentText(),
                'type': self.type_sol.currentText()
            }
        except ValueError:
            QMessageBox.critical(self, "Value Error", "Please enter valid numerical values.")
            return

        validations = [
            (data["type_sol"], self.type_sol_unit, self.type_sol.currentText()),
            (data["pores_sol"], self.pores_sol_unit, self.pores_sol.currentText()),
            (data["compress_sol"], self.compress_sol_unit, self.compress_sol.currentText()),
            (data["density_sol"], False, "Gs")
        ]

        for value, unit_combo, label in validations:
            valid, min_val, max_val = self.validate_input(value, unit_combo)
            if not valid:
                QMessageBox.warning(self, "Invalid value", f"The value for {label} must be between {min_val} and {max_val}.")
                return

        if self.pores_sol_unit.currentText() == "g/cm3":
            data["pores_sol"] /= 1000

        if self.pores_sol.currentText() == "ρf" and data["pores_sol"] >= data["density_sol"]:
            QMessageBox.warning(self, "Invalid value", "Make sure Gs > ρf")
            return

        formula_class = {"clay%": FormulaClay, "wL": FormulaLiquid, "d50ff": FormulaD50ff}.get(data["type"])

        # Pour les valeurs custom
        if self.use_custom_params_check.isChecked():
            # Calcul automatique pour initialisation
            try:
                result, ei_calc, cc_calc, ck_calc, e0, sigma_0, kv0, sigma_v = formula_class().calculate(
                    data["type_sol"], data["pores_sol"], data["compress_sol"], data["density_sol"],
                    data["water"], ei=None, cc=None, ck=None
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Calculation error: {e}")
                return
            # EI*
            if not self._custom_ei_edited:
                self.result_EI_input.setText(f"{ei_calc:.2f}")
                ei = ei_calc
            else:
                try:
                    ei = float(self.result_EI_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Invalid ei*", "Please enter a valid number for ei*.")
                    return
            # Cc*
            if not self._custom_cc_edited:
                self.result_Cc_input.setText(f"{cc_calc:.2f}")
                cc = cc_calc
            else:
                try:
                    cc = float(self.result_Cc_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Invalid Cc*", "Please enter a valid number for Cc*.")
                    return
            # Ck*
            if not self._custom_ck_edited:
                self.result_Ck_input.setText(f"{ck_calc:.2f}")
                ck = ck_calc
            else:
                try:
                    ck = float(self.result_Ck_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Invalid Ck*", "Please enter a valid number for Ck*.")
                    return
            # Calcul final avec les valeurs custom ou éditées
            try:
                result, ei, cc, ck, e0, sigma_0, kv0, sigma_v = formula_class().calculate(
                    data["type_sol"], data["pores_sol"], data["compress_sol"], data["density_sol"],
                    data["water"], ei=ei, cc=cc, ck=ck
                )
                self.result_label.setText(f"Result: {result:.2e}")
                self.result_EI_input.setText(f"{ei:.2f}")
                self.result_Cc_input.setText(f"{cc:.2f}")
                self.result_Ck_input.setText(f"{ck:.2f}")
                self.graph_data = {
                    "result": result, "ei": ei, "cc": cc, "ck": ck,
                    "e0": e0, "sigma_0": sigma_0, "kv0": kv0, "sigma_v": sigma_v
                }
                self.graph_viewer.set_graph_data(self.graph_data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Calculation error: {e}")
                return
        else:
           
            try:
                result, ei, cc, ck, e0, sigma_0, kv0, sigma_v = formula_class().calculate(
                    data["type_sol"], data["pores_sol"], data["compress_sol"], data["density_sol"],
                    data["water"], ei=None, cc=None, ck=None
                )
                self.result_label.setText(f"Result: {result:.2e}")
                self.result_EI_input.setText(f"{ei:.2f}")
                self.result_Cc_input.setText(f"{cc:.2f}")
                self.result_Ck_input.setText(f"{ck:.2f}")
                self.graph_data = {
                    "result": result, "ei": ei, "cc": cc, "ck": ck,
                    "e0": e0, "sigma_0": sigma_0, "kv0": kv0, "sigma_v": sigma_v
                }
                self.graph_viewer.set_graph_data(self.graph_data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Calculation error: {e}")
                return

    def reset(self):
        for input_widget in [
            self.type_sol_input, self.pores_input, self.compress_input,
            self.density_input, self.result_EI_input, self.result_Cc_input, self.result_Ck_input
        ]:
            input_widget.clear()

        for combo_box in [
            self.type_sol, self.type_sol_unit,
            self.pores_sol, self.pores_sol_unit,
            self.compress_sol, self.compress_sol_unit
        ]:
            combo_box.setCurrentIndex(0)

        for check_box, input_widget in [
            (self.result_EI_check, self.result_EI_input),
            (self.result_Cc_check, self.result_Cc_input),
            (self.result_Ck_check, self.result_Ck_input)
        ]:
            check_box.setChecked(False)
            input_widget.setEnabled(False)
            input_widget.clear()

        self.result_label.setText("Result:")
        self.graph_viewer.clear_graph()
        self.graph_data = None

    def _toggle_custom_params(self, state):
        is_checked = state == Qt.CheckState.Checked.value
        self.results_group.setVisible(is_checked)
        self.result_EI_input.setEnabled(is_checked)
        self.result_Cc_input.setEnabled(is_checked)
        self.result_Ck_input.setEnabled(is_checked)
        self.result_EI_type.setEnabled(is_checked)
        self.result_EI_unit.setEnabled(is_checked)
        self.result_Cc_type.setEnabled(is_checked)
        self.result_Cc_unit.setEnabled(is_checked)
        self.result_Ck_type.setEnabled(is_checked)
        self.result_Ck_unit.setEnabled(is_checked)

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
