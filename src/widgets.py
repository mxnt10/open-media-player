
# Aqui, a ideia é personalizar todos os eventos de widgets e botões necessários e mandar tudo pra cá.
########################################################################################################################


# Módulos importados
from pymouse import PyMouse  # pip install PyUserInput

# Módulos do PyQt5
from PyQt5.QtCore import QSize, QTimer, pyqtSlot, Qt, pyqtSignal, QRect
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QPushButton, QLabel, QSlider, QApplication, QWidget, QStyle, QListView, QSizePolicy

# Essa variável vai servir para auxiliar o mapeamento de clique único
state = None


########################################################################################################################


# QSlider personalizado para funcionar quando você clica nele. É muito mais conveniente do que mover
# a barra deslizante para a posição desejada.
class Slider(QSlider):
    pointClicked = pyqtSignal(int)  # Pegar o sinal

    def __init__(self, parent=None):
        super(Slider, self).__init__(parent)
        self.setStyleSheet(open('css/progressbar.css').read())


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
            print(msg)
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


# Resolvi criar uma classe para a logo do programa para aproveitar o efeito do
# duplo clique, pois a tela cheia só deve funcionar dessa forma.
class PixmapLabel(QLabel):
    def __init__(self, win):
        """
            :param win: O parâmetro precisa ser self.
        """
        self.win = win
        super(QLabel, self).__init__()
        self.control = 0

        # Temporizador que fica mapeando a posição do mouse
        self.mouse = PyMouse()
        self.timer = QTimer()
        self.timer.timeout.connect(self.changeMouse)
        self.timer.start()


    # Duplo clique para ativar e desativar o modo de tela cheia.
    def mouseDoubleClickEvent(self, event):
        if self.win.isFullScreen() & event.button() == Qt.LeftButton:
            self.win.unFullScreen()
        else:
            self.win.onFullScreen()
        self.control = 0


    # Função para mapear os movimentos do mouse. Quando o mouse está se mexendo, os controles aparecem.
    def changeMouse(self):
        x = self.mouse.position()[0]
        if self.mouse.position()[0] != x:  # Se esses valores são diferentes, o mouse tá se mexendo.
            if self.control == 0:
                if self.win.isFullScreen():
                    self.win.panelSlider.show()
                    self.win.panelControl.show()
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.control = 1


    # Usei esse mapeador geral de eventos porque queria pegar evento de quando o mouse para.
    def event(self, event):
        if event.type() == 110:  # Executa ações quando o mouse para de se mexer
            if self.win.isFullScreen():  # Aqui eu estou controlando as ações em modo tela cheia
                self.win.panelSlider.hide()
                self.win.panelControl.hide()
            QApplication.setOverrideCursor(Qt.BlankCursor)
            self.control = 0
        return QWidget.event(self, event)


########################################################################################################################


# Classe para o mapeamento de eventos do mouse e demais configurações no widget de vídeo.
class VideoWidget(QVideoWidget):
    def __init__(self, win):
        """
            :param win: O parâmetro precisa ser self.
        """
        self.win = win
        super(VideoWidget, self).__init__()
        self.control = 0

        # Temporizador que fica mapeando a posição do mouse
        self.mouse = PyMouse()
        self.timer = QTimer()
        self.timer.timeout.connect(self.changeMouse)
        self.timer.start()

        # Correções na política de redirecionamento
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

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
        self.control = 0


    # Função para mapear os movimentos do mouse. Quando o mouse está se mexendo, os controles aparecem.
    def changeMouse(self):
        x = self.mouse.position()[0]
        if self.mouse.position()[0] != x:  # Se esses valores são diferentes, o mouse tá se mexendo.
            if self.control == 0:
                if self.win.isFullScreen():
                    self.win.panelSlider.show()
                    self.win.panelControl.show()
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.control = 1


    # Usei esse mapeador geral de eventos porque queria pegar evento de quando o mouse para.
    def event(self, event):
        if event.type() == 110:  # Executa ações quando o mouse para de se mexer
            if self.win.isFullScreen():  # Aqui é estou controlando as ações em modo tela cheia
                self.win.panelSlider.hide()
                self.win.panelControl.hide()
            QApplication.setOverrideCursor(Qt.BlankCursor)
            self.control = 0
        return QWidget.event(self, event)


    # Clique único para executar ações em modo de tela cheia.
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:  # Ação para Executar e pausar com o botão esquerdo
            global state
            self.click_handler()  # Iniciando a escuta
            if self.win.mediaPlayer.state() == QMediaPlayer.PlayingState:
                state = 1  # Pause
            else:
                state = 2  # Play


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
