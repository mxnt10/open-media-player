#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Módulos do PyQt5
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap, QKeySequence
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QShortcut

# Modulos integrados (src)
from utils import setIcon
from version import __version__
from widgets import Label


########################################################################################################################


# Dispensa comentários
class AboutDialog(QDialog):
    def __init__(self):
        super(AboutDialog, self).__init__()
        self.oldPos = None
        self.block = 0

        # Propriedades da janela
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowTitle('About Open Media Player')
        self.setStyleSheet(open('qss/dialog.qss').read())

        # Definindo o layout e o título do texto
        title = Label('Open Media Player v' + str(__version__))
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        # Definição do ícone do programa como logo
        logo = Label()
        logo.setPixmap(QPixmap(setIcon(logo=True)))
        logo.setToolTip("Close with one click")

        # Criando o layout
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 20, 50, 20)
        layout.addWidget(title)
        layout.addWidget(logo)
        layout.addWidget(Label('License: GNU General Public License Version 3 (GLPv3)\n'))
        layout.addWidget(Label('Maintainer: Mauricio Ferrari'))
        layout.addWidget(Label('Contact: m10ferrari1200@gmail.com'))  # As informações
        self.setLayout(layout)

        # Definir tudo no centro
        for i in range(0, layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)

        # Já que não tem muita coisa explicita para fechar essa janela,
        # botei várias teclas de atalho para isso.
        self.shortcut1 = QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Q), self)
        self.shortcut1.activated.connect(self.close)
        self.shortcut2 = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.shortcut2.activated.connect(self.close)


    # Para sair é só dar um clique da janela que já fecha
    def mouseReleaseEvent(self, event):
        if self.block == 0:
            self.close()
        self.block = 0


    # Isso eu botei por frescura mesmo. Apenas possibilita mover a janela
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()


    # A funções que faz a mágica e move a janela
    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
        self.block = 1
