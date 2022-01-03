
# Aqui, a ideia é personalizar todos os eventos de widgets e botões necessários e mandar tudo pra cá.
########################################################################################################################


# Módulos importados
from logging import warning

# Módulos do PyQt5
from PyQt5.QtCore import QSize, QTimer, pyqtSlot, Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPainter
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWidgets import (QPushButton, QSlider, QApplication, QStyle, QListView, QSizePolicy, QGraphicsView,
                             QFrame, QLabel)

# Essa variável vai servir para auxiliar o mapeamento de clique único
state = None


########################################################################################################################


# Não tem utilidade nenhuma a não ser impedir a ocultação dos controles ao posicianar o mouse nos textos
# que mostram o tempo de duração e execução de um arquivo multimídia.
class Label(QLabel):
    eventPoint = pyqtSignal(int)
    def __init__(self, parent=None):
        super(Label, self).__init__(parent)
        self.setStyleSheet('border: 0')

    # Emissão feita ao passar o mouse nos controles.
    def enterEvent(self, event):
        self.eventPoint.emit(1)


    # Emissão feita ao retirar o mouse dos controles.
    def leaveEvent(self, event):
        self.eventPoint.emit(2)


########################################################################################################################


# QSlider personalizado para funcionar quando você clica nele. É muito mais conveniente do que mover
# a barra deslizante para a posição desejada.
class Slider(QSlider):
    eventPoint = pyqtSignal(int)
    pointClicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super(Slider, self).__init__(parent)
        self.setStyleSheet(open('qss/progressbar.qss').read())


    # Função para alterar o valor da barra de reprodução.
    def positionToInterval(self, event):
        value = QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width())
        self.setValue(value)
        self.pointClicked.emit(value)


    # Ao clicar na barra de reprodução em qualquer lugar, o valor muda.
    def mousePressEvent(self, event):
        self.positionToInterval(event)


    # Ao mover a barra de reprodução, o valor muda.
    def mouseMoveEvent(self, event):
        self.positionToInterval(event)


    # Emissão feita ao passar o mouse nos controles.
    def enterEvent(self, event):
        self.eventPoint.emit(1)


    # Emissão feita ao retirar o mouse dos controles.
    def leaveEvent(self, event):
        self.eventPoint.emit(2)


########################################################################################################################


# Essa classe controla todos os efeitos dos botões do programa.
class PushButton(QPushButton):
    def __init__(self, num):
        self.num = num
        """
            :param num: Aqui você entra com o tamanho dos ícones.
        """
        super(PushButton, self).__init__()
        self.__fading_button = None
        self.setFixedSize(self.num, self.num)
        self.setIconSize(QSize(self.num, self.num))
        self.setStyleSheet('border: 0')
        self.pressed.connect(self.onEffect)


    # Esse evento funciona quando o mouse passa em cima dos botões.
    def enterEvent(self, event):
        try:
            self.setIconSize(QSize(self.num + 2, self.num + 2))
        except Exception as msg:
            print(msg)


    # Já esse funciona ao tirar o mouse de cima dos botões.
    def leaveEvent(self, event):
        try:
            self.setIconSize(QSize(self.num, self.num))
        except Exception as msg:
            print(msg)


    # Efeito visual ao clicar nos botões. Esse efeito consiste em reduzir os botões em 2px.
    @pyqtSlot()
    def onEffect(self):
        self.__fading_button = self.sender()  # Mapear o sinal do botão a ser alterado
        try:
            self.__fading_button.setIconSize(QSize(self.num - 2, self.num - 2))
        except Exception as msg:
            warning('\033[33m %s.\033[32m', msg)
        QTimer.singleShot(100, self.unEffect)  # Timer do efeito


    # Para completar o efeito visual ao clicar nos botões. Depois da redução, o tamanho
    # precisa voltar ao normal.
    def unEffect(self):
        try:
            self.__fading_button.setIconSize(QSize(self.num + 2, self.num + 2))
        except Exception as msg:
            print(msg)
        self.__fading_button = None  # Finalizar o estado do botão


########################################################################################################################


# Lista redimensionável para a playlist, pois assim não precisa ficar sofrendo para reformular o layout tudo
# de novo e também porque só é preciso que a playlist seja redimensionável.
class ListView(QListView):
    resizeMargin = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._sizeHint = QSize(0, 0)
        self.startPos = self.section = None
        self.setMouseTracking(True)


    # Função para atualizar o cursor ao chegar na borda especificada para redirecionar.
    def updateCursor(self, pos):
        if pos.x() < self.resizeMargin:
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
            self.section = (1, QRect())
            return self.section
        QApplication.setOverrideCursor(Qt.ArrowCursor)


    # A playlist só direciona com esse treco aqui.
    def minimumSizeHint(self):
        try:
            return self._sizeHint
        except Exception as msg:
            print(msg)


    # Ao pressionar o botão do mouse esquerdo, a playlist poderá ser redimensionada.
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.updateCursor(event.pos()):  # Verifica se o cursor foi atualizado
                self.startPos = event.pos()
        super().mousePressEvent(event)


    # Evento que vai fazer o serviço e redimensionar a playlist.
    def mouseMoveEvent(self, event):
        if self.startPos is not None:
            delta = event.pos()
            if self.section:
                delta.setX(-delta.x())
            self._sizeHint = QSize(self.width() + delta.x(), self.height() + delta.y())
            self.startPos = event.pos()
            self.setMinimumWidth(self.width() + delta.x())  # Forçando o redimensionamento
        elif not event.buttons():
            self.updateCursor(event.pos())  # Isso aqui precisa para fazer o mouse mudar


    # Redefine todas as propriedades definidas no redirecionamento.
    def mouseReleaseEvent(self, event):
        self.startPos = self.section = None


    # Só para redefinir o cursor ao posicionar o mouse para fora da playlist.
    def leaveEvent(self, event):
        QApplication.setOverrideCursor(Qt.ArrowCursor)


########################################################################################################################


# Classe para o mapeamento de eventos do mouse e demais configurações no widget de vídeo.
class VideoWidget(QGraphicsView):
    def __init__(self, win):
        """
            :param win: O parâmetro precisa ser self.
        """
        self.win = win
        super(VideoWidget, self).__init__()

        # Cor de fundo
        color = self.palette()
        color.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(color)

        # Demais ajustes
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFrameShape(QFrame.NoFrame)  # Tira a borda

        # Melhorar qualidade e resolução
        self.setRenderHints(QPainter.Antialiasing |
                            QPainter.HighQualityAntialiasing |
                            QPainter.SmoothPixmapTransform)

        # Como foi usado fitInView vai aparecer uma barra de rolagem desnecessária que será desativada
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalScrollBar().setDisabled(True)

        # Mapeador de clique único que já vai executar as ações necessárias após o mapeamento
        self.click_handler = ClickPlayPause(self.win)


    # Clique único para executar ações em modo de tela cheia.
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:  # Ação para Executar e pausar com o botão esquerdo
            global state
            self.click_handler()  # Iniciando a escuta
            if self.win.mediaPlayer.state() == QMediaPlayer.PlayingState:
                state = 1  # Pause
            else:
                state = 2  # Play


    # Como não está sendo usado QVideoWidget, é necessário fazer o redirecionamento.
    def resizeEvent(self, event):
        self.win.videoWidget.fitInView(self.win.videoItem, Qt.KeepAspectRatio)


########################################################################################################################


# Cópia descarada do StackOverflow, porém com algumas alterações. Apenas com o diferencial de já executar as
# opções de executar e pausar. A ação de dois cliques não foi feita dessa forma.
class ClickPlayPause:
    def __init__(self, win):
        self.win = win
        """
            :param win: O parâmetro precisa ser self.win.
        """

        self.timer = QTimer()
        self.timer.setInterval(400)  # O segredo da parada
        self.timer.setSingleShot(True)  # Só vai haver um intervalo de tempo
        self.timer.timeout.connect(self.timeout)
        self.click_count = 0


    # Em 400ms essa função é acionada e se em 400ms teve mais de um clique,
    # ele vai executar as ações de executar ou pausar.
    def timeout(self):
        if self.click_count == 1:
            if state == 1:
                self.win.mediaPlayer.pause()
            if state == 2:
                self.win.mediaPlayer.play()
        self.click_count = 0


    # Carinha que faz a escuta e vai contando os cliques.
    def __call__(self):
        self.click_count += 1
        if not self.timer.isActive():
            self.timer.start()
