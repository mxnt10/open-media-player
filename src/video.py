
# Módulos do PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QSizePolicy, QLabel


########################################################################################################################

# Resolvi criar uma nova classe para a logo do programa aqui mesmo para aproveitar o efeito do
# duplo clique, pois a tela cheia só deve funcionar dessa forma.

class PixmapLabel(QLabel):
    def __init__(self, win, parent=None):
        self.win = win
        super(QLabel, self).__init__(parent)


    # Duplo clique para ativar e desativar o modo de tela cheia.
    def mouseDoubleClickEvent(self, event):
        if self.win.isFullScreen():
            self.win.onFullScreen()
        else:
            self.win.unFullScreen()


########################################################################################################################


# Classe para o mapeamento de eventos do mouse e demais configurações no widget de vídeo.
class VideoWidget(QVideoWidget):
    def __init__(self, win, parent=None):
        self.win = win

        super(VideoWidget, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setStyleSheet('background-color: #000000')

        # Após o término do vídeo reproduzido, ao tentar executar o vídeo novamente, o fundo não fica mais preto.
        # Esse recurso vai garantir que a cor no fundo do vídeo vai ser preto e deu e tá acabado.
        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)
        self.setAttribute(Qt.WA_OpaquePaintEvent)


    # Duplo clique para ativar e desativar o modo de tela cheia.
    def mouseDoubleClickEvent(self, event):
        if self.win.isFullScreen():
            self.win.onFullScreen()
        else:
            self.win.unFullScreen()
