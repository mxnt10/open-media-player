
# Aqui, a ideia é personalizar todos os eventos de widgets e botões necessários e mandar tudo pra cá.
########################################################################################################################

# Módulos do PyQt5
from PyQt5.QtCore import QSize, QTimer, pyqtSlot, Qt, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QPushButton, QLabel, QSlider, QApplication

# Essa variável vai servir para o auxilio do mapeamento de clique único
state = None


########################################################################################################################


# QSlider personalizado para funcionar quando você clica nele. É muito mais conveniente do que mover
# a barra deslizante para a posição desejada.
class Slider(QSlider):
    pointClicked = pyqtSignal(int)  # Pegar o sinal


    # Evento para mapear o clique no QSlider feito com o botão esquerdo.
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.pos().x()
            value = (self.maximum() - self.minimum()) * x / self.width() + self.minimum()
            self.pointClicked.emit(value)  # Emitindo o valor atual
        else:
            return super().mousePressEvent(self, event)


########################################################################################################################


# Essa classe controla todos os efeitos dos botões do programa.
class PushButton(QPushButton):
    def __init__(self, num):
        """
            @param num: Aqui você entra com o tamanho dos ícones.
        """
        super(PushButton, self).__init__()
        self.__fading_button = None
        self.num = num
        self.setFixedSize(num, num)
        self.setIconSize(QSize(num, num))
        self.setStyleSheet('border: 0')
        self.pressed.connect(lambda: self.onEffect(num))


    # Esse evento funciona quando o mouse passa encima dos botões.
    def enterEvent(self, event):
        self.setIconSize(QSize(self.num + 2, self.num + 2))


    # Já esse funciona ao tirar o mouse de cima dos botões.
    def leaveEvent(self, event):
        self.setIconSize(QSize(self.num, self.num))


    # Efeito visual ao clicar nos botões. Esse efeito consiste em reduzir os botões em 2px.
    @pyqtSlot()
    def onEffect(self, num):
        self.__fading_button = self.sender()  # Mapear o sinal do botão a ser alterado
        self.__fading_button.setIconSize(QSize(num - 2, num - 2))
        QTimer.singleShot(100, lambda: self.unEffect(num))  # Timer do efeito


    # Para completar o efeito visual ao clicar nos botões. Depois da redução, o tamanho
    # precisa voltar ao normal.
    def unEffect(self, num):
        self.__fading_button.setIconSize(QSize(num + 2, num + 2))
        self.__fading_button = None  # Finalizar o estado do botão


########################################################################################################################


# Resolvi criar uma nova classe para a logo do programa para aproveitar o efeito do
# duplo clique, pois a tela cheia só deve funcionar dessa forma.
class PixmapLabel(QLabel):
    def __init__(self, win):
        """
            @param win: Aqui você entra com self.
        """
        self.win = win
        super(QLabel, self).__init__()
        self.control = 0


    # Duplo clique para ativar e desativar o modo de tela cheia.
    def mouseDoubleClickEvent(self, event):
        if self.win.isFullScreen() & event.button() == Qt.LeftButton:
            self.win.unFullScreen()
        else:
            self.win.onFullScreen()


    # Ação para mostrar os controles clicando com o botão direito
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            if self.control == 0:
                self.win.panelControl.show()
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.control = 1
            else:
                self.win.panelControl.hide()
                QApplication.setOverrideCursor(Qt.BlankCursor)
                self.control = 0


########################################################################################################################


# Classe para o mapeamento de eventos do mouse e demais configurações no widget de vídeo.
class VideoWidget(QVideoWidget):
    def __init__(self, win):
        """
            @param win: Aqui você entra com self.
        """
        self.win = win
        super(VideoWidget, self).__init__()
        self.control = 0

        # Após o término do vídeo reproduzido, ao tentar executar o vídeo novamente, o fundo não fica mais preto.
        # Esse recurso vai garantir que a cor no fundo do vídeo vai ser preto e deu e tá acabado.
        self.setStyleSheet('background-color: #000000')

        # Mapeador de clique único que já vai executar as ações necessárias após o mapeamento
        self.click_handler = ClickPlayPause(self.win)


    # Duplo clique para ativar e desativar o modo de tela cheia.
    def mouseDoubleClickEvent(self, event):
        if self.win.isFullScreen() & event.button() == Qt.LeftButton:
            self.win.unFullScreen()
        else:
            self.win.onFullScreen()


    # Clique único para executar ações em modo de tela cheia.
    def mouseReleaseEvent(self, event):

        # Ação para Executar e pausar com o botão esquerdo
        if event.button() == Qt.LeftButton:
            global state
            self.click_handler()  # Iniciando a escuta
            if self.win.mediaPlayer.state() == QMediaPlayer.PlayingState:
                state = 1  # Pause
            else:
                state = 2  # Play

        # Ação para mostrar os controles clicando com o botão direito
        if event.button() == Qt.RightButton:
            if self.control == 0:
                self.win.panelControl.show()
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.control = 1
            else:
                self.win.panelControl.hide()
                QApplication.setOverrideCursor(Qt.BlankCursor)
                self.control = 0


########################################################################################################################


# Cópia descarada da internet, porém com algumas alterações. Apenas com o diferencial de já executar as
# opções de executar e pausar. A ação de dois cliques não foi feita dessa forma.
class ClickPlayPause:
    def __init__(self, win):
        """
            @param win: Aqui você entra com self.win.
        """

        self.timer = QTimer()
        self.timer.setInterval(400)  # O segredo da parada
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda: self.timeout(win))
        self.click_count = 0


    # Em 400ms essa função é acionada e se em 400ms teve mais de um clique,
    # ele vai executar as ações de executar ou pausar.
    def timeout(self, win):
        if self.click_count == 1:
            if state == 1:
                win.mediaPlayer.pause()
            if state == 2:
                win.mediaPlayer.play()
        self.click_count = 0


    # Carinha que faz a escuta e vai contando os cliques.
    def __call__(self):
        self.click_count += 1
        if not self.timer.isActive():
            self.timer.start()
