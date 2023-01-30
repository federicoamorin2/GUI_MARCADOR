from PyQt5.QtWidgets import QComboBox, QFormLayout, QLineEdit, QPushButton, QWidget

from src.backend.fields import Field, FieldType
from src.utils import LabelAdditionError, MessageBox, RegisterAdditionError


class FieldSetup(QWidget):
    def __init__(self, parent):
        super().__init__(None)
        self.parent = parent
        self.fieldRegister = parent.fieldRegister
        self.lay = QFormLayout(self)
        self.resize(400, 300)
        self.labelNames = {}
        self.add_field()

    @property
    def is_classification(self):
        return FieldType(self.comboBox.currentText()) == FieldType.CLASSIFCATION

    def add_field(self):
        self.fieldName = QLineEdit()
        self.fieldName.resize(1, 1)
        self.lay.addRow("Nome do campo: ", self.fieldName)

        self.setup_combo_box()
        self.setup_btn_adiciona()
        self.setup_btn_remove()
        self.setup_btn_confirma()
        self.comboBox.currentTextChanged.connect(self.on_combobox_changed)

    def setup_combo_box(self):
        self.comboBox = QComboBox(self)
        self.comboBox.addItem(FieldType.CLASSIFCATION.value)
        self.comboBox.addItem(FieldType.EXTRACTION.value)
        self.lay.addRow("Tipo de dado: ", self.comboBox)

    def setup_btn_confirma(self):
        self.btnConfirma = QPushButton("Confirma")
        self.btnConfirma.clicked.connect(self.confirm_field)
        self.lay.addRow(self.btnConfirma)

    def setup_btn_adiciona(self):
        self.btnAdicionaLabel = QPushButton("Adiciona Label")
        self.btnAdicionaLabel.clicked.connect(self.adiciona_label)
        self.lay.addRow(self.btnAdicionaLabel)

    def setup_btn_remove(self):
        self.btnRemoveLabel = QPushButton("Remove Label")
        self.btnRemoveLabel.clicked.connect(self.remove_label)
        self.lay.addRow(self.btnRemoveLabel)

    def remove_label(self):
        if len(self.labelNames) == 0:
            return
        label_name = f"Label {len(self.labelNames)}:"
        self.lay.removeRow(self.labelNames[label_name])
        del self.labelNames[label_name]

    def adiciona_label(self):
        label_name = f"Label {len(self.labelNames)+1}:"
        self.labelNames[label_name] = QLineEdit()
        self.lay.addRow(label_name, self.labelNames[label_name])

    def confirm_field(self):
        field_name = self.fieldName.displayText()
        field = Field(name=field_name, type=self.comboBox.currentText())
        try:
            for label in self.labelNames.values():
                field.add_label(label.displayText())
            self.fieldRegister.add(field)

        except (RegisterAdditionError, LabelAdditionError) as e:
            MessageBox(str(e))
            return
        self.parent.update_field_buttons()
        self.close()

    def on_combobox_changed(self):
        if self.is_classification and self.btnAdicionaLabel is None:
            self.btnConfirma.deleteLater()
            self.setup_btn_adiciona()
            self.setup_btn_remove()
            self.setup_btn_confirma()
        if not self.is_classification:
            self.btnRemoveLabel.deleteLater()
            self.btnRemoveLabel = None
            self.btnAdicionaLabel.deleteLater()
            self.btnAdicionaLabel = None
            for guy in self.labelNames.values():
                self.lay.removeRow(guy)

            self.labelNames = {}
