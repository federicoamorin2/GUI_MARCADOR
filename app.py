from pathlib import Path
import sys

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QWidget,
    QFileDialog,
    QPushButton,
    QFormLayout,
    QDialog,
)

from src import (
    PdfReport,
    FieldRegister,
    ControlWidgets,
    LabelRegister,
    MessageBox,
)

CURRENT_DIR = Path().absolute()
PDFJS_PATH = "pdfjs/web/viewer.html"
PDFJS = QtCore.QUrl.fromLocalFile((CURRENT_DIR / PDFJS_PATH).as_posix()).toString()
# FIELD_DF = pd.DataFrame(columns=["name", "type", "labels", "is_drawn"])
FIELD_DF = pd.DataFrame(
    {
        "name": ["hr_audiencia", "dt_audiencia"],
        "type": ["Extração", "Extração"],
        "labels": [None, None],
        "is_drawn": [False, False],
    }
)


class MainApp(QWidget):
    def __init__(self, pdf_list, label_register, parent=None):
        super().__init__(parent)
        self.pdf_list = pdf_list
        self.label_register = label_register
        self.init_ui()
        self.setWindowTitle("Marcador do fredao")
        self.resize(1000, 1000)

    def init_ui(self):

        self.pdf = PdfReport(self.pdf_list, PDFJS)
        self.fieldRegister = FieldRegister(FIELD_DF)
        self.control = ControlWidgets(
            self.pdf, self.fieldRegister, self.pdf_list, self.label_register
        )

        lay = QGridLayout(self)
        lay.addWidget(self.pdf, 0, 0, 0, 4)
        lay.addWidget(self.control, 0, 4)


class IntroPage(QDialog):
    def __init__(self, label_register, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Config")
        self.resize(500, 200)
        self.selectFolderBtn = QPushButton("Seleciona Pasta")
        self.selectFolderBtn.clicked.connect(self.get_folder)
        self.lay = QFormLayout(self)
        self.lay.addRow(self.selectFolderBtn)
        self.pdf_path = None
        self.label_register = label_register

    def get_folder(self):
        pdf_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.pdf_list = list(Path(pdf_path).glob("*.pdf"))
        if len(self.pdf_list) > 0:
            self.label_register.load()
            self.accept()
        else:
            MessageBox("Provide a folder with pdfs inside!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    label_register = LabelRegister()
    login = IntroPage(label_register)
    login.show()
    if login.exec_() == QDialog.Accepted:
        main_window = MainApp(login.pdf_list, label_register)
        main_window.show()
        sys.exit(app.exec_())
