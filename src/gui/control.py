import time
import os
import re

from PyQt5.QtWidgets import (
    QPushButton,
    QGridLayout,
    QFormLayout,
    QWidget,
    QComboBox,
    QLineEdit,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QProgressBar,
)
from toolz import curry

from .fields import FieldSetup
from src.utils import MessageBox
from src.backend.fields import Field


class ControlButtons(QWidget):
    def __init__(self, pdf, fieldRegister, pdf_list, label_register) -> None:
        super().__init__(None)

        self.counter = 0
        self.label_register = label_register
        self.pdf_list = pdf_list
        self.current_labels = {}
        self.fieldRegister = fieldRegister
        self.plabel = QLabel(self.progress_str)
        self.pbar = QProgressBar(self)
        self.pbar.setMaximum(len(self.pdf_list))
        self.btnNext = QPushButton("Next")
        self.btnPrev = QPushButton("Prev")
        self.btnAddField = QPushButton("Addiciona campo")
        self.pdf = pdf
        self.lay = QFormLayout(self)
        self.lay.addRow(self.plabel)
        self.lay.addRow(self.pbar)
        self.lay.addRow(self.btnNext)
        self.lay.addRow(self.btnPrev)

        self.btnAddField.clicked.connect(self.add_field)
        self.btnNext.clicked.connect(lambda: self.pass_page(1))
        self.btnPrev.clicked.connect(lambda: self.pass_page(-1))
        self.update_field_buttons()
        self.pass_page(0)

    @property
    def progress_str(self):
        pct = f"{((self.counter + 1)*100/len(self.pdf_list)):.2f}"
        return f"Progreso: {pct}% ({self.counter + 1}/{len(self.pdf_list)})"

    @curry
    def pass_page(self, step: int) -> None:
        if not (0 <= self.counter + step < len(self.pdf_list)):
            MessageBox("End of pdfs!")
            return
        filename = self.pdf_list[self.counter]
        next_filename = self.pdf_list[self.counter + step]
        for field in self.fieldRegister:
            label_widget = self.current_labels[field.name].children()[-1]

            if field.is_extraction:
                label = label_widget.displayText()
                is_valid = self.valida_label(label, field)
                if not is_valid:
                    return
                fill_txt = self.label_register.get(next_filename, field.name, "")
                label_widget.setText(fill_txt)
            else:
                label = label_widget.currentText()
                fill_txt = self.label_register.get(next_filename, field.name, "")
                label_widget.setCurrentText(fill_txt)

            self.label_register.add(
                filename, label, time.time(), field.name, field.type
            )

        self.counter = self.counter + step
        self.pdf.goto(self.counter, self.pdf_list)
        self.pbar.setValue(self.counter + 1)
        self.plabel.setText(self.progress_str)

    def valida_label(self, label, field):
        if field.name == "dt_audiencia" and not (
            bool(re.match("\d{2}/\d{2}/\d{4}", label)) or label == ""
        ):
            MessageBox("Por favor insira data no formato:\n dd/mm/aaaa")
            return False
        if field.name == "hr_audiencia" and not (
            bool(re.match("\d{2}:\d{2}", label)) or label == ""
        ):
            MessageBox("Por favor insira horario no formato:\n hh:MM")
            return False
        return True

    def add_field(self):
        self.sub_window = FieldSetup(self)
        self.sub_window.show()

    def update_field_buttons(self):
        for field in self.fieldRegister.undrawn():
            if field.is_extraction:
                self.add_extraction_field(field)
            else:
                self.add_classification_field(field)
            self.lay.addRow(self.current_labels[field.name])

    def add_extraction_field(self, field: Field):
        self.current_labels[field.name] = QWidget()
        lay = QHBoxLayout(self.current_labels[field.name])

        fieldName = QLabel()
        fieldName.setText(f"{field.name.capitalize()}: ")

        fieldEntry = QLineEdit()
        rmvButton = QPushButton("Remove")
        rmvButton.clicked.connect(lambda: self.delete_field(field.name))

        lay.addWidget(fieldName)
        lay.addWidget(fieldEntry)
        # lay.addWidget(rmvButton)

    def add_classification_field(self, field: Field):
        self.current_labels[field.name] = QWidget()
        lay = QHBoxLayout(self.current_labels[field.name])

        fieldName = QLabel()
        fieldName.setText(f"{field.name.capitalize()}: ")

        rmvButton = QPushButton("Remove")
        rmvButton.clicked.connect(lambda: self.delete_field(field.name))

        fieldEntry = QComboBox()
        fieldEntry.addItem("")
        for label in field.labels:
            fieldEntry.addItem(label)

        lay.addWidget(fieldName)
        lay.addWidget(fieldEntry)
        lay.addWidget(rmvButton)

    @curry
    def delete_field(self, row_name):
        self.fieldRegister.remove(row_name)
        self.current_labels[row_name].deleteLater()


class ControlWidgets(QWidget):
    def __init__(self, pdf, fieldRegister, pdf_list, label_register) -> None:
        super().__init__(None)
        self.label_register = label_register
        self.fieldRegister = fieldRegister
        self.lay = QGridLayout(self)
        self.buttons = ControlButtons(pdf, fieldRegister, pdf_list, label_register)

        # addWidget(widget, fromRow, fromColumn, rowSpan, columnSpan, alignment)
        self.lay.addWidget(self.buttons, 0, 0, 1, 1)
        self.exportaExcelBtn = QPushButton("Exporta excel")
        self.lay.addWidget(self.exportaExcelBtn)
        self.lay.addWidget(self.exportaExcelBtn, 9, 0, 1, 1)
        self.exportaExcelBtn.clicked.connect(self.exporta)

    def exporta(self):
        arquivo, _ = QFileDialog.getSaveFileName(
            self,
            "Escolha onde guardar",
            f"marcador_{os.environ['USER']}.csv",
            "Excel (*.csv)",
        )
        if arquivo:
            df = self.label_register.export()
            df.to_csv(arquivo, index=False)
