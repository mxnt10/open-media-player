#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Módulos do PyQt5
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

# Modulos integrados (src)
from utils import setIcon
from version import __version__


########################################################################################################################


# Somente para não pegar a borda da janela. Método mais econômico.
class Label(QLabel):
    def __init__(self, parent=None):
        super(Label, self).__init__(parent)
        self.setStyleSheet('border: 0')


# Dispensa comentários.
class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)
        self.oldPos = None

        # Propriedades da janela.
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('About Open Media Player')
        self.setStyleSheet('background: #000000;'
                           'color: #ffffff;'
                           'border: 5px solid #150033')
        self.setFixedSize(0, 0)

        # Definição do botão de OK
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.setStyleSheet('border: 0')

        # Definindo o layout e o título do texto
        title = Label('Open Media Player - Version ' + str(__version__))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        # Definição do ícone do programa como logo
        logo = Label()
        logo.setPixmap(QPixmap(setIcon(logo=True)))

        # Criando o layout
        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(logo)
        layout.addWidget(Label('License: GNU General Public License Version 3 (GLPv3)\n'))
        layout.addWidget(Label('Maintainer: Mauricio Ferrari'))
        layout.addWidget(Label('Contact: m10ferrari1200@gmail.com\n'))  # As informações
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

        # Definir tudo no centro
        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)


    # Isso eu botei por frescura mesmo. Apenas possibilita mover a janela.
    def mousePressEvent(self, evt):
        self.oldPos = evt.globalPos()


    # A funções que faz a mágica e move a janela.
    def mouseMoveEvent(self, evt):
        delta = QPoint(evt.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = evt.globalPos()
