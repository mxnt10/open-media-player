
# Módulos do PyQt5
from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWidgets import QWidget, QHBoxLayout

# Modulos integrados (src)
from utils import setIconTheme
from widgets import PushButton


########################################################################################################################


theme = 'circle'

# Widget para a definição dos controles usados pelo reprodutor multimídia. Achei mais conveniente fazer assim,
# conforme nos exemplos tirados do qt5, pois assim o código não vai virar uma bagunça, porque senão daqui a pouco
# o cara não entende mais nada do que colocou no código.

class PlayerControls(QWidget):
    # Captura o sinal dos botões e dos controles
    play = pyqtSignal()
    pause = pyqtSignal()
    stop = pyqtSignal()

    def __init__(self, win):
        """
            @param win: Aqui você entra com self.
        """
        self.main = win

        super(PlayerControls, self).__init__()
        self.playerState = QMediaPlayer.StoppedState

        # Definição do botão play/pause
        self.playButton = PushButton(48)
        self.playButton.setIcon(setIconTheme(self, theme, 'play'))
        self.playButton.setFixedSize(48, 48)  # Durante o efeito, os botões não podem sair do lugar.
        self.playButton.setIconSize(QSize(48, 48))
        self.playButton.clicked.connect(self.pressPlay)

        # Definição do botão stop
        self.stopButton = PushButton(30)
        self.stopButton.setIcon(setIconTheme(self, theme, 'stop'))
        self.stopButton.setEnabled(False)
        self.stopButton.setFixedSize(30, 30)  # Durante o efeito, os botões não podem sair do lugar.
        self.stopButton.setIconSize(QSize(30, 30))
        self.stopButton.clicked.connect(self.stop)

        # Layout para posicionar os botões definidos
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.playButton)
        self.setLayout(layout)


########################################################################################################################


    # Especial para retornar o estado da reprodução ao clicar nos botões e nos controles.
    def state(self):
        return self.playerState


    # Essa função é necessária para mapear as alterações de execução do arquivo multimídia.
    # Se o reprodutor estiver executando, ele vai mostrar o botão pause, se estiver pausado, vai exibir
    # o botão play. E também faz o ajuste do botão play/pause ao clicar no botão stop.
    def setState(self, state):
        if state != self.playerState:
            self.playerState = state
            if state == QMediaPlayer.StoppedState:  # Stop
                self.stopButton.setEnabled(False)
                self.playButton.setIcon(setIconTheme(self, theme, 'play'))
                self.main.positionSlider.setValue(0)
                self.main.startLogo.show()
            elif state == QMediaPlayer.PlayingState:  # Play
                self.main.startLogo.hide()
                self.stopButton.setEnabled(True)
                self.playButton.setIcon(setIconTheme(self, theme, 'pause'))
            elif state == QMediaPlayer.PausedState:  # Pause
                self.stopButton.setEnabled(True)
                self.playButton.setIcon(setIconTheme(self, theme, 'play'))


    # Essa é a instrução que vai fazer o botão de play/pause e stop funcionar adequadamente.
    def pressPlay(self):
        if self.playerState in (QMediaPlayer.StoppedState, QMediaPlayer.PausedState):
            self.play.emit()
        elif self.playerState == QMediaPlayer.PlayingState:
            self.pause.emit()
