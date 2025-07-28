from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QComboBox, QLineEdit,
    QPushButton, QMessageBox, QCheckBox, QSizePolicy, QHBoxLayout, QLabel
)
from PyQt6.QtCore import Qt
from style import APP_STYLE
from widgets.modern_widgets import ModernGroupBox, ModernResultsSection, ModernResultsDisplay, ModernResultsPanel  # Add ModernResultsPanel here
from formulas.hydraulique.FormulaClay import FormulaClay
from formulas.hydraulique.FormulaLiquid import FormulaLiquid
from formulas.hydraulique.FormulaD50ff import FormulaD50ff
from pages.soil_parameter import assemble_hydro_layout, init_unit_mappings, init_input_limits
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QPainter, QTextDocument
import tempfile
import os

"""
Module Hydro – interface graphique de la section hydraulique.
Contient les composants visuels et les fonctions de contrôle de l’interface utilisateur.
"""

class HydroPage(QWidget):
    def __init__(self):
        super().__init__()
        self._other_page = None
        self._syncing = False
        self._custom_ei_edited = False
        self._custom_cc_edited = False
        self._custom_ck_edited = False
        self.setMinimumSize(800, 600)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(APP_STYLE)
        self._init_widgets()
        
        # Initialize common mappings and limits
        init_unit_mappings(self)
        init_input_limits(self)
        self._connect_unit_updates()
        self._set_initial_units()
        
        # Create the results display widget
        self.results_display = ModernResultsDisplay()
        self.results_display.setFixedHeight(150)
        self.results_display.setMaximumHeight(650)
        
        # Create the results panel to group results and graphs
        self.results_panel = ModernResultsPanel()
        self.results_panel.add_widget(self.results_display)
        
        self.calculate_button = QPushButton("Calculate")
        self.reset_button = QPushButton("Reset")
        self.calculate_button.clicked.connect(self.calculate)
        self.reset_button.clicked.connect(self.reset)
        
        # Set up the main layout
        assemble_hydro_layout(self)
        
        # Add the hydro-specific custom results section
        self._setup_custom_results()
        
        # For syncing data between pages
        self.type_sol_input.textChanged.connect(lambda value: self._sync_field('type_sol_input', value))
        self.pores_input.textChanged.connect(lambda value: self._sync_field('pores_input', value))
        self.compress_input.textChanged.connect(lambda value: self._sync_field('compress_input', value))
        self.density_input.textChanged.connect(lambda value: self._sync_field('density_input', value))
        # Manual input detection
        self.result_EI_input.textEdited.connect(self._on_custom_ei_edited)
        self.result_Cc_input.textEdited.connect(self._on_custom_cc_edited)
        self.result_Ck_input.textEdited.connect(self._on_custom_ck_edited)
        self.use_custom_params_check.stateChanged.connect(self._on_custom_check_changed)
        self.use_custom_params_check.stateChanged.connect(self._toggle_custom_params)

        # --- Add QLabel above the main layout (robust approach) ---
        old_layout = self.layout()
        main_widget = QWidget()
        main_widget.setLayout(old_layout)
        outer_layout = QVBoxLayout()
        label = QLabel("Thawed soil hydraulic conductivity as proposed by Picard and al. (2026)")
        label.setObjectName("parameterLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        outer_layout.addWidget(label)
        outer_layout.addWidget(main_widget)
        QWidget.setLayout(self, outer_layout)
        # --- End QLabel addition ---

    def set_other_page(self, other_page):
        self._other_page = other_page

    def _sync_field(self, field_name, value):
        if self._other_page and not self._syncing:
            self._other_page._syncing = True
            getattr(self._other_page, field_name).setText(value)
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

        self.type_sol = QComboBox()
        self.type_sol.setProperty("type", "type")
        self.type_sol.addItems(["Clay content", "Liquid limit", "Fine fraction median diameter"])
        self.type_sol_unit = QComboBox()

        self.pores_sol = QComboBox()
        self.pores_sol.setProperty("type", "type")
        self.pores_sol.addItems(["Initial water content", "Frozen bulk density", "Frozen void ratio"])
        self.pores_sol_unit = QComboBox()

        self.compress_sol = QComboBox()
        self.compress_sol.setProperty("type", "type")
        self.compress_sol.addItems(["Effective vertical stress"])
        self.compress_sol_unit = QComboBox()

        self.density_sol = QComboBox()
        self.density_sol.setProperty("type", "type")
        self.density_sol.addItems(["Specific gravity of solids"])
        self.density_sol_unit = QComboBox()
        self.density_sol_unit.addItems(["-"])

        # Update initial states of dropdowns with single options
        self._update_combo_state(self.compress_sol)
        self._update_combo_state(self.density_sol)
        self._update_combo_state(self.density_sol_unit)

        # Results widgets
        self.result_EI_input = self._create_line_edit("Value...")
        self.result_Cc_input = self._create_line_edit("Value...")
        self.result_Ck_input = self._create_line_edit("Value...")

        # Results unit dropdowns
        self.result_EI_unit = QComboBox()
        self.result_EI_unit.addItems(["ei*"])
        self._update_combo_state(self.result_EI_unit)

        self.result_Cc_unit = QComboBox()
        self.result_Cc_unit.addItems(["Cc*"])
        self._update_combo_state(self.result_Cc_unit)

        self.result_Ck_unit = QComboBox()
        self.result_Ck_unit.addItems(["Ck*"])
        self._update_combo_state(self.result_Ck_unit)

        # Connect combo box changes
        self.type_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('type_sol', idx))
        self.type_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('type_sol_unit', idx))
        self.pores_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('pores_sol', idx))
        self.pores_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('pores_sol_unit', idx))
        self.compress_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('compress_sol', idx))
        self.compress_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('compress_sol_unit', idx))
        self.density_sol.currentIndexChanged.connect(lambda idx: self._sync_combo('density_sol', idx))
        self.density_sol_unit.currentIndexChanged.connect(lambda idx: self._sync_combo('density_sol_unit', idx))

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

    def _connect_unit_updates(self):
        self.type_sol.currentIndexChanged.connect(lambda: self.update_unit_options(self.type_sol, self.type_sol_unit))
        self.pores_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.pores_sol, self.pores_sol_unit))
        self.compress_sol.currentIndexChanged.connect(
            lambda: self.update_unit_options(self.compress_sol, self.compress_sol_unit))

    def _set_initial_units(self):
        self.update_unit_options(self.type_sol, self.type_sol_unit)
        self.update_unit_options(self.pores_sol, self.pores_sol_unit)
        self.update_unit_options(self.compress_sol, self.compress_sol_unit)

    def _update_combo_state(self, combo: QComboBox):
        """Update the enabled state and style of a combo box based on number of items"""
        has_multiple_options = combo.count() > 1
        combo.setEnabled(has_multiple_options)
        
        if not has_multiple_options:
            combo.setStyleSheet("""
                QComboBox {
                    background-color: #f0f0f0;
                    color: #666666;
                    border: 1px solid #cccccc;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                }
            """)
        else:
            combo.setStyleSheet("")

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
            
            # Update the combo box state based on number of options
            self._update_combo_state(unit_combo)

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

        # Validation des entrées
        validations = [
            (data["type_sol"], self.type_sol_unit, self.type_sol.currentText()),
            (data["pores_sol"], self.pores_sol_unit, self.pores_sol.currentText()),
            (data["compress_sol"], self.compress_sol_unit, self.compress_sol.currentText()),
            (data["density_sol"], False, "Specific gravity of solids")
        ]
        for value, unit_combo, label in validations:
            valid, min_val, max_val = self.validate_input(value, unit_combo)
            if not valid:
                QMessageBox.warning(self, "Invalid value",
                                    f"The value for {label} must be between {min_val} and {max_val}.")
                return

        if self.pores_sol_unit.currentText() == "kg/m³":
            data["pores_sol"] /= 1000
        if self.pores_sol.currentText() == "Frozen bulk density" and data["pores_sol"] >= data["density_sol"]:
            QMessageBox.warning(self, "Invalid value", "Make sure Specific gravity of solids > Frozen bulk density")
            return

        formula_class = {
            "Clay content": FormulaClay,
            "Liquid limit": FormulaLiquid,
            "Fine fraction median diameter": FormulaD50ff
        }.get(data["type"])

        # Initialize custom values as None
        ei = None
        cc = None
        ck = None

        # Only use custom values for checked parameters
        if self.use_custom_params_check.isChecked():
            if self.result_EI_check.isChecked():
                try:
                    ei = float(self.result_EI_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Invalid Value", "Please enter a valid number for Initial thawed void ratio")
                    return

            if self.result_Cc_check.isChecked():
                try:
                    cc = float(self.result_Cc_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Invalid Value", "Please enter a valid number for Thawed soil compression index")
                    return

            if self.result_Ck_check.isChecked():
                try:
                    ck = float(self.result_Ck_input.text())
                except ValueError:
                    QMessageBox.warning(self, "Invalid Value", "Please enter a valid number for Hydraulic conductivity index")
                    return

        # Calculate with custom or calculated values
        try:
            result, ei_calc, cc_calc, ck_calc, e0, sigma_0, kv0, sigma_v = formula_class().calculate(
                data["type_sol"], data["pores_sol"], data["compress_sol"], data["density_sol"],
                data["water"], ei=ei, cc=cc, ck=ck
            )
            
            # Clear previous results
            self.results_display.clear()
            
            # Show result exactly as before
            self.results_display.add_result("", f"kv = {result:.2e}")
            # Show intermediate results
            self.results_display.add_result("", f"Ei = {ei or ei_calc:.3f}")
            self.results_display.add_result("", f"E0 = {e0:.3f}")
            self.results_display.add_result("", f"sigma0 = {sigma_0:.3f}")
            self.results_display.add_result("", f"kv0 = {kv0:.3e}")
            self.results_display.add_result("", f"Cc = {cc or cc_calc:.3f}")
            self.results_display.add_result("", f"Ck = {ck or ck_calc:.3f}")
            
            # Only update unchecked parameter displays
            if not (self.use_custom_params_check.isChecked() and self.result_EI_check.isChecked()):
                self.result_EI_input.setText(f"{ei_calc:.2f}")
            if not (self.use_custom_params_check.isChecked() and self.result_Cc_check.isChecked()):
                self.result_Cc_input.setText(f"{cc_calc:.2f}")
            if not (self.use_custom_params_check.isChecked() and self.result_Ck_check.isChecked()):
                self.result_Ck_input.setText(f"{ck_calc:.2f}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Calculation error: {e}")
            return

    def reset(self):
        for input_widget in [
            self.type_sol_input, self.pores_input, self.compress_input,
            self.density_input, self.result_EI_input, self.result_Cc_input, self.result_Ck_input
        ]:
            input_widget.clear()
        
        self.density_input.setText("2.67")
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

        self.results_display.clear()

    def _toggle_custom_params(self, state):
        is_checked = state == Qt.CheckState.Checked.value
        self.results_group.setVisible(is_checked)
        
        # When showing the custom results, ensure everything starts disabled
        if is_checked:
            # Reset and disable all checkboxes
            self.result_EI_check.setChecked(False)
            self.result_Cc_check.setChecked(False)
            self.result_Ck_check.setChecked(False)
            
            # Ensure all inputs are disabled and styled accordingly
            self.result_EI_input.setEnabled(False)
            self.result_Cc_input.setEnabled(False)
            self.result_Ck_input.setEnabled(False)
            self.result_EI_unit.setEnabled(False)
            self.result_Cc_unit.setEnabled(False)
            self.result_Ck_unit.setEnabled(False)
            
            # Apply disabled styling
            disabled_style = """
                QLineEdit:disabled, QComboBox:disabled {
                    background-color: #f0f0f0;
                    color: #666666;
                    border: 1px solid #cccccc;
                }
            """
            self.result_EI_input.setStyleSheet(disabled_style)
            self.result_Cc_input.setStyleSheet(disabled_style)
            self.result_Ck_input.setStyleSheet(disabled_style)
            self.result_EI_unit.setStyleSheet(disabled_style)
            self.result_Cc_unit.setStyleSheet(disabled_style)
            self.result_Ck_unit.setStyleSheet(disabled_style)

    def _set_value_column_width(self, width=120):
        self.type_sol_input.setMinimumWidth(width)
        self.type_sol_input.setMaximumWidth(width)
        self.pores_input.setMinimumWidth(width)
        self.pores_input.setMaximumWidth(width)
        self.compress_input.setMinimumWidth(width)
        self.compress_input.setMaximumWidth(width)
        self.density_input.setMinimumWidth(width)
        self.density_input.setMaximumWidth(width)
        # For optional results
        if hasattr(self, 'result_EI_input'):
            self.result_EI_input.setMinimumWidth(width)
            self.result_EI_input.setMaximumWidth(width)
        if hasattr(self, 'result_Cc_input'):
            self.result_Cc_input.setMinimumWidth(width)
            self.result_Cc_input.setMaximumWidth(width)
        if hasattr(self, 'result_Ck_input'):
            self.result_Ck_input.setMinimumWidth(width)
            self.result_Ck_input.setMaximumWidth(width)

    def _setup_custom_results(self):
        # Create the custom results group
        self.results_group = ModernGroupBox("Hydraulic Custom Parameters")
        
        # Create the results section
        results_section = ModernResultsSection()
        
        # Add the parameters and store the checkboxes
        self.result_EI_check = results_section.add_result(
            "Initial thawed void ratio",
            self.result_EI_unit,
            self.result_EI_input
        )
        
        self.result_Cc_check = results_section.add_result(
            "Thawed soil compression index",
            self.result_Cc_unit,
            self.result_Cc_input
        )
        
        self.result_Ck_check = results_section.add_result(
            "Hydraulic conductivity index",
            self.result_Ck_unit,
            self.result_Ck_input
        )
        
        # Set up the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(results_section)
        self.results_group.setLayout(main_layout)
        self.results_group.setVisible(False)

        # Add to main layout right after the checkbox
        main_layout = self.layout()
        if main_layout:
            left_widget = main_layout.itemAt(0).widget()
            if left_widget:
                left_layout = left_widget.layout()
                if left_layout:
                    # Find the checkbox widget
                    for i in range(left_layout.count()):
                        item = left_layout.itemAt(i)
                        if item.widget() and isinstance(item.widget(), QWidget):
                            if hasattr(item.widget(), 'layout'):
                                checkbox_layout = item.widget().layout()
                                if checkbox_layout and isinstance(checkbox_layout, QHBoxLayout):
                                    for j in range(checkbox_layout.count()):
                                        checkbox_item = checkbox_layout.itemAt(j)
                                        if checkbox_item.widget() and isinstance(checkbox_item.widget(), QCheckBox):
                                            # Insert the results group right after the checkbox's parent widget
                                            left_layout.insertWidget(i + 1, self.results_group)
                                            return
                    
                    # Fallback: insert before the button layout if checkbox not found
                    left_layout.insertWidget(left_layout.count() - 1, self.results_group)