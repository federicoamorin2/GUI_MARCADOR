from PyQt5 import QtCore, QtWebEngineWidgets


class PdfReport(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, pdf_list, pdfjs, parent=None):
        super().__init__(parent)
        self.pdfjs = pdfjs
        # self.goto(0, pdf_list)

    def load_pdf(self, filename):
        url = QtCore.QUrl.fromLocalFile(filename).toString()
        self.load(QtCore.QUrl.fromUserInput("%s?file=%s" % (self.pdfjs, url)))

    def sizeHint(self):
        return QtCore.QSize(640, 480)

    def goto(self, idx, pdf_list):
        self.load_pdf(str(pdf_list[idx]))
