#!/usr/bin/python3
# -*- coding: utf-8 -*-


########################################################################################################################
#
# Open Media Player - Reprodutor multimídia baseado em Python e PyQt5.
#
# Reprodutor multimídia inspirado na interface do Windows Media Player da Microsoft e no reprodutor Kantaris,
# sendo eles desenvolvidos apenas para Windows.
#
# O tema padrão vai ter um toque estilo walkman da sony, feito para android.
#
# Formatos de vídeos testados:
#   - mp4
#   - mpg
#
# Formatos de áudio testados:
#   - mp3
#
# Formatos Incompatíveis: Não mapeado ainda.
#
# Início do desenvolvimento: 14/11/2021
# Término do desenvolvimento:
# Última atualização:
#
# Licença: GNU General Public License Version 3 (GLPv3)
#
# Mantenedor: mauricio Ferrari
# E-Mail: m10ferrari1200@gmail.com
# Telegram: @maurixnovatrento
#
########################################################################################################################


# Módulos importados
from sys import argv

# Módulos do PyQt5
from PyQt5.QtCore import Qt, QDir, QUrl, QPoint, QFileInfo
from PyQt5.QtGui import QKeySequence, QPixmap, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtWidgets import (QApplication, QWidget, QFileDialog, QVBoxLayout, QAction, QMenu, QHBoxLayout, QShortcut,
                             QGridLayout, QDesktopWidget, QFrame, QListView)

# Modulos integrados (src)
from src.about import AboutDialog
from src.controls import PlayerControls
from src.playlist import PlaylistModel
from src.style import styleSheet
from src.utils import setIconTheme, setIcon
from src.widgets import VideoWidget, PixmapLabel, Slider


########################################################################################################################


theme = 'circle'

# Foi usado QWidget ao invés de QMainWindow, senão não funciona a visualização do widget de vídeo.
# Essa classe cria a interface principal que irá fazer a reprodução dos arquivos multimídia.

class MultimediaPlayer(QWidget):
    def __init__(self, parent=None):
        super(MultimediaPlayer, self).__init__(parent)
        self.getduration = 0
        self.maximize = False
        self.oldPos = None

        # Atribuindo as propriedades da interface principal do programa
        self.setWindowTitle('Open Media Player')
        self.setWindowIcon(QIcon(setIcon()))
        self.setMinimumSize(800, 600)
        self.center()

        # Instrução para habilitar o menu de contexto no Open Media Player. O programa não contará
        # com uma barra de menu habilitada por padrão, então será usado menu de contexto.
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested[QPoint].connect(self.contextMenuRequested)

        # Parte principal do programa. O mediaPlayer vai ser definido com a engine QMediaPlayer que
        # irá fazer a reprodução dos arquivos multimídia.
        self.mediaPlayer = QMediaPlayer()

        # Criar um widget para a visualização do vídeo
        self.videoWidget = VideoWidget(self)
        self.mediaPlayer.setVideoOutput(self.videoWidget)

        # Necessário para a criação da playlist.
        self.playlist = QMediaPlaylist()
        self.mediaPlayer.setPlaylist(self.playlist)

        # Necessário para o funcionamento a playlist, o que vai fazer funcionar tudo
        self.playlistModel = PlaylistModel()
        self.playlistModel.setPlaylist(self.playlist)

        # Define a lista dos itens que serão visualizados na playlist e a visualização da playlist
        self.playlistView = QListView()
        self.playlistView.setModel(self.playlistModel)
        self.playlistView.setCurrentIndex(self.playlistModel.index(self.playlist.currentIndex(), 0))
        self.playlistView.activated.connect(self.jump)
        self.playlistView.setStyleSheet('border: 2px outset #444444;'
                                        'color: #ffffff;'
                                        'background: #100022')

        # Essa aqui é a barra que mostra o progresso da execução do arquivo multimídia
        self.positionSlider = Slider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.pointClicked.connect(self.setPosition)
        self.positionSlider.setStyleSheet(styleSheet())

        # Layout só para ajustar a barra de execução
        self.positionLayout = QHBoxLayout()
        self.positionLayout.setContentsMargins(10, 5, 10, 5)
        self.positionLayout.addWidget(self.positionSlider)

        # Essa aqui cria uma linha horizontal no programa. A função dessa linha é só para
        # efeito visual mesmo.
        QHLine = QFrame(self)
        QHLine.setFrameShape(QFrame.HLine)
        QHLine.setFrameShadow(QFrame.Raised)
        QHLine.setStyleSheet('background: #444444;'
                             'border: 1px solid #000000')

        # Container só para dar uma corzinha diferente para o layout da playlist
        self.panelSHPlaylist = QWidget()
        self.panelSHPlaylist.setStyleSheet('background: #000000')
        self.panelSHPlaylist.setFixedWidth(300)

        # Layout só para ajustar o botão de mostrar e ocultar a playlist
        self.positionSHPlaylist = QHBoxLayout(self.panelSHPlaylist)
        self.positionSHPlaylist.setContentsMargins(6, 6, 6, 6)
        self.positionSHPlaylist.setSpacing(0)
        self.positionSHPlaylist.addWidget(self.playlistView)

        # Widget para aplicar funcionalidades nos controles em playerControls
        self.controls = PlayerControls(self)
        self.controls.setState(self.mediaPlayer.state())  # Pega o estado do reprodutor
        self.controls.play.connect(self.setPlay)
        self.controls.pause.connect(self.mediaPlayer.pause)
        self.controls.stop.connect(self.setStop)

        # Layout especial para o ajuste dos controles abaixo do widget de vídeo
        self.controlLayout = QHBoxLayout()
        self.controlLayout.setContentsMargins(0, 0, 0, 5)
        self.controlLayout.addStretch(1)
        self.controlLayout.addWidget(self.controls)
        self.controlLayout.addStretch(1)  # Esse addStretch adiciona um espaçamento

        # Isso aqui funciona como um conteiner para colorir os layouts dos controles
        self.panelControl = QWidget()
        self.panelControl.setStyleSheet('background: #100022')

        # O layout para botar tudo o que é de controle barra e tal, dentro do conteiner
        self.lay = QVBoxLayout(self.panelControl)
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.lay.setSpacing(0)
        self.lay.addWidget(QHLine)
        self.lay.addLayout(self.positionLayout)
        self.lay.addLayout(self.controlLayout)

        # Acho legal entrar com uma logo no programa.
        self.startLogo = PixmapLabel(self)
        self.startLogo.setPixmap(QPixmap(setIcon(logo=True)))
        self.startLogo.setAlignment(Qt.AlignCenter)

        # self.startLogo.setScaledContents(True)
        # self.movie = QMovie('../gif_view/effects1.gif')
        # self.startLogo.setMovie(self.movie)
        # self.movie.start()

        # Criando um layout para mostrar o conteiner com os widgets e layouts personalizados
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.videoWidget, 0, 0)
        self.layout.addWidget(self.startLogo, 0, 0)
        self.layout.addWidget(self.panelSHPlaylist, 0, 1)
        self.layout.addWidget(self.panelControl, 1, 0, 1, 2)  # Os layouts dos controles
        self.setLayout(self.layout)
        # self.panelSHPlaylist.hide()

        # Configurações de atalhos de teclado
        self.shortcut1 = QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_A), self)
        self.shortcut1.activated.connect(self.openFile)
        self.shortcut2 = QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_O), self)
        self.shortcut2.activated.connect(self.openFile)
        self.shortcut3 = QShortcut(QKeySequence(Qt.AltModifier + Qt.Key_Return), self)
        self.shortcut3.activated.connect(self.controlFullScreen)
        self.shortcut4 = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.shortcut4.activated.connect(self.unFullScreen)
        self.shortcut5 = QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Q), self)
        self.shortcut5.activated.connect(self.close)

        self.mediaPlayer.stateChanged.connect(self.controls.setState)   # Ação para o botão play/pause
        self.mediaPlayer.positionChanged.connect(self.positionChanged)  # Alteração da barra de execução
        self.mediaPlayer.durationChanged.connect(self.durationChanged)  # Setar o tempo de execução na barra


########################################################################################################################


    # Função necessária para a entrada de parâmetros no programa.
    def loadFilm(self, file):
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(file)))
        self.addToPlaylist(file)
        self.mediaPlayer.play()  # Play automático


    # Função usada para abrir arquivos multimídia no programa.
    def openFile(self):
        fileNames, event = QFileDialog.getOpenFileNames(self, "Open Multimedia Files", QDir.homePath())
        self.addToPlaylist(fileNames)
        if self.getduration == 0:
            self.mediaPlayer.play()  # Play automático


    # Esse recurso vai adicionar os itens a lista de execução do programa.
    def addToPlaylist(self, fileNames):
        for name in fileNames:
            fileInfo = QFileInfo(name)
            if fileInfo.exists():
                url = QUrl.fromLocalFile(fileInfo.absoluteFilePath())
                if fileInfo.suffix().lower() == 'm3u':
                    self.playlist.load(url)
                else:
                    self.playlist.addMedia(QMediaContent(url))
            else:
                url = QUrl(name)
                if url.isValid():
                    self.playlist.addMedia(QMediaContent(url))


    # essa função é chamada quando você dá um duplo clique em um item da playlist,
    # para que esse item possa ser executado.
    def jump(self, index):
        if index.isValid():
            self.playlist.setCurrentIndex(index.row())
            self.mediaPlayer.play()


    # Função que só é necessária por conta da redefinição do positionSlider em setStop. É necessário definir
    # novamente o positionSlider para que ele possa funcionar perfeitamente.
    def setPlay(self):
        self.positionSlider.setRange(0, self.getduration)
        self.mediaPlayer.play()  # Play automático


    # Função para parar a execução e também forçar o positionSlider a voltar para o início, pois não é visualmente
    # aceitável parar a execução e progresso da execução ficar onde está.
    def setStop(self):
        self.mediaPlayer.stop()
        self.positionSlider.setRange(0, 0)


    # Função necessária para posicionar o tempo de execução no slider que mostra o progresso de execução.
    def positionChanged(self, position):
        self.positionSlider.setValue(position)


    # Ao abrir e executar um arquivo multimídia, o tempo de execução será definido no positionSlider.
    def durationChanged(self, duration):
        self.getduration = duration
        self.positionSlider.setRange(0, duration)


    # A barra vai atualizar ao ocorrer mudanças no valor do tempo de execução.
    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)


    # Função que faz o programa abrir no centro da janela, claro se ele já não abrir maximizado.
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    # Isso é apenas para exibir a janela sobre do programa.
    @staticmethod
    def showAbout():
        about = AboutDialog()
        about.exec_()


    # Controle do modo tela cheia feito pelo Alt+Enter.
    def controlFullScreen(self):
        if self.isFullScreen():
            self.unFullScreen()
        else:
            self.onFullScreen()


    # Esses carinhas vão ser executados de dentro de VideoWidget e PixmapLabel. Esse aqui,
    # é para habilitar o modo de tela cheia.
    def onFullScreen(self):
        if multimediaPlayer.isMaximized():
            self.maximize = True
        QApplication.setOverrideCursor(Qt.BlankCursor)
        self.showFullScreen()
        self.panelSHPlaylist.hide()
        self.panelControl.hide()


    # E esse desabilita a tela cheia.
    def unFullScreen(self):
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        self.panelSHPlaylist.show()
        self.panelControl.show()
        self.showNormal()
        if self.maximize:
            self.showMaximized()


    # Menu de contexto personalizado para o programa, bem no capricho.
    def contextMenuRequested(self, point):
        if not self.isFullScreen():
            # Menu para abrir com arquivos de multimídia
            openMenu = QAction(setIconTheme(self, theme, 'folder'), 'Open', self)
            openMenu.setShortcut('Ctrl+O')
            openMenu.triggered.connect(self.openFile)

            # Menu para abrir a janela de configurações
            fullScreen = QAction(setIconTheme(self, theme, 'fullscreen'), 'FullScreen', self)
            fullScreen.setShortcut('Alt+Enter')
            fullScreen.triggered.connect(self.onFullScreen)

            # Menu para abrir a janela de configurações
            openSettings = QAction(setIconTheme(self, theme, 'settings'), 'Settings', self)
            openSettings.setShortcut('Alt+S')

            # Menu para abrir a janela sobre
            openAbout = QAction(setIconTheme(self, theme, 'about'), 'About', self)
            openAbout.triggered.connect(self.showAbout)

            # Montagem do menu de contexto
            menu = QMenu()
            menu.addAction(openMenu)
            menu.addAction(fullScreen)
            # menu.addAction(openSettings)
            menu.addSeparator()
            menu.addAction(openAbout)
            menu.setStyleSheet('background-color: #150033;'
                               'color: #ffffff;'
                               'border: 6px solid #150033;')
            menu.exec_(self.mapToGlobal(point))


    # def mouseReleaseEvent(self, event):
    #     if event.button() == Qt.RightButton:
    #         print('foi')

    # def mousePressEvent(self, evt):
    #     self.oldPos = evt.globalPos()
    #
    # def mouseMoveEvent(self, evt):
    #     delta = QPoint(evt.globalPos() - self.oldPos)
    #     self.move(self.x() + delta.x(), self.y() + delta.y())
    #     self.oldPos = evt.globalPos()


########################################################################################################################


# início do programa

if __name__ == '__main__':
    openMediaplayer = QApplication(argv)
    multimediaPlayer = MultimediaPlayer()
    # multimediaPlayer.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    multimediaPlayer.show()

    # Entrada de argumentos
    if len(argv) > 1:
        multimediaPlayer.loadFilm(argv[1])

    exit(openMediaplayer.exec_())  # Finalização correta do programa
