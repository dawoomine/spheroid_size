import sys

from qtwindow import QTWindow
from PyQt5.QtWidgets import QApplication


def main(args):
    app = QApplication(args)
    ex = QTWindow()
    return app.exec_()


if __name__ == "__main__":
    ecode = main(sys.argv)
    sys.exit(ecode)
