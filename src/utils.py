from PyQt5.QtWidgets import QMessageBox, QWidget


class RegisterAdditionError(Exception):
    """Mother class for related errors."""


class FieldExistsError(RegisterAdditionError):
    """Error when user tries to add field that already exists to register"""


class FieldNameEmptyError(RegisterAdditionError):
    """Error when user tries to add field with no name"""


class FieldHasNoLabelsError(RegisterAdditionError):
    """Error when user tries to add classification field with no labels."""


class LabelAdditionError(Exception):
    """Mother class for related errors."""


class FieldDuplicateLabelError(LabelAdditionError):
    """Same field, same label names, big no-no!"""


class FieldMethodNotValid(LabelAdditionError):
    """Wrong usage of function, probably bug in ui"""


class FieldLabelEmptyError(LabelAdditionError):
    """Empty label provided."""


class MessageBox(QWidget):
    def __init__(self, msg, icon_level=QMessageBox.Warning, parent=None) -> None:
        super().__init__(parent)
        self.msg = QMessageBox()
        self.msg.setWindowTitle("Aviso!")
        self.msg.setText(msg)
        self.msg.setIcon(icon_level)
        self.msg.exec_()


class QuestionMessageBox(QWidget):
    def __init__(self, msg, icon_level=QMessageBox.Information, parent=None) -> None:
        super().__init__(parent)
        msgBox = QMessageBox()
        msgBox.setIcon(icon_level)
        msgBox.setText(msg)
        msgBox.setWindowTitle("QMessageBox Example")
        msgBox.setStandardButtons(msgBox.Yes | msgBox.No)

        returnValue = msgBox.exec()
        self.is_yes = returnValue == QMessageBox.Yes