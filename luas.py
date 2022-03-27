import sys
from PyQt5.QtWidgets import (
    QApplication,
    QDialog
)
from PyQt5.uic import loadUi


class HitungLuas(QDialog):

    def __init__(self):
        super(HitungLuas, self).__init__()

        # Load the UI Page
        loadUi("luas.ui", self)
        self.setWindowTitle("Program Hitung Luas Persegi Panjang")
        self.pushButton.clicked.connect(self.on_pushButton_clicked)

    def on_pushButton_clicked(self):
        p = int(self.txt.text())
        l = int(self.txt_2.text())
        luas = p * l
        self.txt_3.setText(str(luas))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HitungLuas()
    window.show()
    sys.exit(app.exec_())
