
# Módulos do PyQt5
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFrame

# Modulos integrados (src)
from jsonTools import set_json
from utils import setIconTheme
from widgets import PushButton, Slider


########################################################################################################################


# Widget para a definição dos controles usados pelo reprodutor multimídia. Achei mais conveniente fazer assim,
# conforme nos exemplos tirados do qt5, pois assim o código não vai virar uma bagunça, porque senão daqui a pouco
# o cara não entende mais nada do que colocou no código.
class PlayerControls(QWidget):
    # Captura o sinal dos botões e dos controles
    eventPoint = pyqtSignal(int)
    play = pyqtSignal()
    pause = pyqtSignal()
    stop = pyqtSignal()
    next = pyqtSignal()
    previous = pyqtSignal()
    changeVolume = pyqtSignal(int)
    changeMuting = pyqtSignal(bool)
    replayOne = pyqtSignal()
    replay = pyqtSignal()
    shuffle = pyqtSignal()

    def __init__(self, win):
        """
            :param win: Esse parâmetro precisa ser self.
        """
        self.main = win

        super(PlayerControls, self).__init__()
        self.playerState = QMediaPlayer.StoppedState
        self.playerMuted = False
        self.statusPlayBack = None
        self.theme = set_json('theme')

        # Definição do botão play/pause
        self.playButton = PushButton(48)
        self.playButton.setIcon(setIconTheme(self, self.theme, 'play'))
        self.playButton.clicked.connect(self.pressPlay)

        # Definição do botão stop
        self.stopButton = PushButton(30)
        self.stopButton.setIcon(setIconTheme(self, self.theme, 'stop'))
        self.stopButton.clicked.connect(self.stop)

        # Definição do botão next
        self.nextButton = PushButton(30)
        self.nextButton.setIcon(setIconTheme(self, self.theme, 'next'))
        self.nextButton.clicked.connect(self.pressNext)

        # Definição do botão previous
        self.previousButton = PushButton(30)
        self.previousButton.setIcon(setIconTheme(self, self.theme, 'previous'))
        self.previousButton.clicked.connect(self.pressPrevious)

        # Botão para o mute
        self.muteButton = PushButton(30)
        self.muteButton.setIcon(setIconTheme(self, self.theme, 'volume_high'))
        self.muteButton.clicked.connect(self.pressMute)

        # Botão para o replay
        self.replayButton = PushButton(30)
        self.replayButton.setIcon(setIconTheme(self, self.theme, 'replay'))
        self.replayButton.clicked.connect(self.setReplay)

        # Botão para o shuffle
        self.shuffleButton = PushButton(30)
        self.shuffleButton.setIcon(setIconTheme(self, self.theme, 'shuffle'))
        self.shuffleButton.clicked.connect(self.setShuffle)

        # Controle de volume
        self.volumeSlider = Slider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setMinimumWidth(100)
        self.volumeSlider.pointClicked.connect(self.changeVolume)

        # divisória para os botões
        self.line = QFrame()
        self.line.setFrameShape(QFrame.VLine)
        self.line.setMaximumHeight(30)
        self.line.setStyleSheet(open('qss/controls.qss').read())

        # Ajuste do tamanho do espaçamento da linha
        self.positionline = QHBoxLayout()
        self.positionline.setContentsMargins(10, 0, 10, 0)
        self.positionline.addWidget(self.line)

        # Ajuste do espaçamento do controle do volume
        self.positionvolume = QHBoxLayout()
        self.positionvolume.setContentsMargins(5, 0, 0, 0)
        self.positionvolume.addWidget(self.volumeSlider)

        # Layout para posicionar os botões definidos
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)
        layout.addWidget(self.shuffleButton)
        layout.addWidget(self.replayButton)
        layout.addLayout(self.positionline)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.previousButton)
        layout.addWidget(self.playButton)
        layout.addWidget(self.nextButton)
        layout.addWidget(self.muteButton)
        layout.addLayout(self.positionvolume)
        layout.addStretch(1)  # Esse addStretch adiciona um espaçamento
        self.setLayout(layout)


########################################################################################################################


    # Especial para retornar o estado da reprodução ao clicar nos botões e nos controles
    def state(self):
        return self.playerState


    # Essa função é necessária para mapear as alterações de execução do arquivo multimídia.
    # Se o reprodutor estiver executando, ele vai mostrar o botão pause, se estiver pausado, vai exibir
    # o botão play. E também faz o ajuste do botão play/pause ao clicar no botão stop.
    def setState(self, state):
        if state != self.playerState:
            self.playerState = state
            if state == QMediaPlayer.StoppedState:  # Stop
                self.playButton.setIcon(setIconTheme(self, self.theme, 'play'))
            elif state == QMediaPlayer.PlayingState:  # Play
                self.playButton.setIcon(setIconTheme(self, self.theme, 'pause'))
            elif state == QMediaPlayer.PausedState:  # Pause
                self.playButton.setIcon(setIconTheme(self, self.theme, 'play'))


    # Essa é a instrução que vai fazer o botão de play/pause e stop funcionar adequadamente
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


    # Mesmo esquema que mencionei acima
    def pressPrevious(self):
        self.previous.emit()
        if self.playerState in (QMediaPlayer.StoppedState, QMediaPlayer.PausedState):
            self.play.emit()


    # Função para retornar o volume para o reprodutor
    def volume(self):
        return self.volumeSlider.value()


    # Essa função vai alterar o volume do reprodutor
    def setVolume(self, volume):
        if self.isMuted():
            self.pressMute()
        if 0 < volume <= 25:
            self.muteButton.setIcon(setIconTheme(self, self.theme, 'volume_low'))
        elif 25 < volume <= 75:
            self.muteButton.setIcon(setIconTheme(self, self.theme, 'volume_medium'))
        elif volume > 75:
            self.muteButton.setIcon(setIconTheme(self, self.theme, 'volume_high'))
        elif volume == 0:
            self.muteButton.setIcon(setIconTheme(self, self.theme, 'mute'))
        self.volumeSlider.setValue(volume)


    # Verificando se o programa está mudo
    def isMuted(self):
        return self.playerMuted


    # Essa parte vai alterar o estado da saída de áudio, se está no mudo ou não
    def setMuted(self, muted):
        if muted != self.playerMuted:
            self.playerMuted = muted
        if muted:
            self.muteButton.setIcon(setIconTheme(self, self.theme, 'mute'))
        elif not muted and self.volumeSlider.value() > 0:
            self.muteButton.setIcon(setIconTheme(self, self.theme, 'volume_high'))


    # Ao clicar no botão mute um sinal é emitido
    def pressMute(self):
        self.changeMuting.emit(not self.playerMuted)


    # Função para recomeçar a playlist novamente
    def setReplay(self):
        if self.main.playlist.playbackMode() != QMediaPlaylist.PlaybackMode.Loop:
            self.main.playlist.setPlaybackMode(QMediaPlaylist.PlaybackMode.Loop)
            self.replayButton.setIcon(setIconTheme(self, self.theme, 'replay-on'))
            self.shuffleButton.setIcon(setIconTheme(self, self.theme, 'shuffle'))
        elif self.main.playlist.playbackMode() == QMediaPlaylist.PlaybackMode.Loop:
            self.main.playlist.setPlaybackMode(QMediaPlaylist.PlaybackMode.Sequential)
            self.replayButton.setIcon(setIconTheme(self, self.theme, 'replay'))


    # Função para reproduzir so arquivos de multimídia de forma aleatória
    def setShuffle(self):
        if self.main.playlist.playbackMode() != QMediaPlaylist.PlaybackMode.Random:
            self.main.playlist.setPlaybackMode(QMediaPlaylist.PlaybackMode.Random)
            self.shuffleButton.setIcon(setIconTheme(self, self.theme, 'shuffle-on'))
            self.replayButton.setIcon(setIconTheme(self, self.theme, 'replay'))
        elif self.main.playlist.playbackMode() == QMediaPlaylist.PlaybackMode.Random:
            self.main.playlist.setPlaybackMode(QMediaPlaylist.PlaybackMode.Sequential)
            self.shuffleButton.setIcon(setIconTheme(self, self.theme, 'shuffle'))


    # Emissão feita ao passar o mouse nos controles
    def enterEvent(self, event):
        self.eventPoint.emit(1)


    # Emissão feita ao retirar o mouse dos controles
    def leaveEvent(self, event):
        self.eventPoint.emit(2)
