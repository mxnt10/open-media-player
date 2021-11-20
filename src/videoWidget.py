
# Módulos do PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QSizePolicy


########################################################################################################################


# Classe para o mapeamento de eventos do mouse e demais configurações no widget de vídeo.

class VideoWidget(QVideoWidget):
    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setStyleSheet('background-color: #000000')

        # Após o término do vídeo reproduzido, ao tentar executar o vídeo novamente, o fundo não fica mais preto.
        # Esse recurso vai garantir que a cor no fundo do vídeo vai ser preto e deu e tá acabado.
        p = self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)
        self.setAttribute(Qt.WA_OpaquePaintEvent)


    # Mapeamento de eventos de clique de mouse, necessário para o funcionamento do modo tela cheia.
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.setFullScreen(False)
            event.accept()
        elif event.key() == Qt.Key_Enter and event.modifiers() & Qt.Key_Alt:
            self.setFullScreen(not self.isFullScreen())
            event.accept()
        else:
            super(VideoWidget, self).keyPressEvent(event)


    # Duplo clique para ativar e desativar o modo de tela cheia.
    def mouseDoubleClickEvent(self, event):
        self.setFullScreen(not self.isFullScreen())
        event.accept()
