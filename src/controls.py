
# Módulos do PyQt5
from PyQt5.QtCore import pyqtSignal
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
    next = pyqtSignal()
    previous = pyqtSignal()

    def __init__(self, win):
        """
            :param win: Esse parâmetro precisa ser self.
        """
        self.main = win

        super(PlayerControls, self).__init__()
        self.playerState = QMediaPlayer.StoppedState

        # Definição do botão play/pause
        self.playButton = PushButton(48)
        self.playButton.setIcon(setIconTheme(self, theme, 'play'))
        self.playButton.clicked.connect(self.pressPlay)

        # Definição do botão stop
        self.stopButton = PushButton(30)
        self.stopButton.setIcon(setIconTheme(self, theme, 'stop'))
        self.stopButton.setEnabled(False)
        self.stopButton.clicked.connect(self.stop)

        # Definição do botão next
        self.nextButton = PushButton(30)
        self.nextButton.setIcon(setIconTheme(self, theme, 'next'))
        self.nextButton.clicked.connect(self.pressNext)

        # Definição do botão previous
        self.previousButton = PushButton(30)
        self.previousButton.setIcon(setIconTheme(self, theme, 'previous'))
        self.previousButton.clicked.connect(self.pressPrevious)

        # Layout para posicionar os botões definidos
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.previousButton)
        layout.addWidget(self.playButton)
        layout.addWidget(self.nextButton)
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
                self.main.positionSlider.setMaximum(0)
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


    # Se o cara vai avançar ou voltar uma música, é porque tem a intenção de escutar ela. Então, ao pressionar
    # um desses botões, foda-se se está pausado ou parado, ele vai tocar e deu.
    def pressNext(self):
        self.next.emit()
        if self.playerState in (QMediaPlayer.StoppedState, QMediaPlayer.PausedState):
            self.play.emit()


    # Mesmo esquema que mencionei acima.
    def pressPrevious(self):
        self.previous.emit()
        if self.playerState in (QMediaPlayer.StoppedState, QMediaPlayer.PausedState):
            self.play.emit()
