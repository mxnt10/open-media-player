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
# Arquivos de playlist testados:
#   - m3u
#
# Formatos Incompatíveis: Não mapeado ainda.
#
# Início do desenvolvimento: 14/11/2021
# Término do desenvolvimento: 20/11/2021
# Última atualização: 28/11/2021
#
# Licença: GNU General Public License Version 3 (GLPv3)
#
# Mantenedor: mauricio Ferrari
# E-Mail: m10ferrari1200@gmail.com
# Telegram: @maurixnovatrento
#
########################################################################################################################


# Módulos importados
from pykeyboard import PyKeyboard  # pip install PyUserInput
from os.path import dirname
from sys import argv

# Módulos do PyQt5
from PyQt5.QtCore import Qt, QDir, QUrl, QPoint, QFileInfo, QTimer
from PyQt5.QtGui import QKeySequence, QPixmap, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtWidgets import (QApplication, QWidget, QFileDialog, QVBoxLayout, QAction, QMenu, QHBoxLayout, QShortcut,
                             QGridLayout, QDesktopWidget, QFrame, QListView)

# Modulos integrados (src)
from about import AboutDialog
from controls import PlayerControls
from jsonTools import checkSettings, set_json, write_json
from playlist import PlaylistModel
from utils import setIconTheme, setIcon
from widgets import VideoWidget, PixmapLabel, Slider


########################################################################################################################


theme = 'circle'

# Foi usado QWidget ao invés de QMainWindow, senão não funciona a visualização do widget de vídeo.
# Essa classe cria a interface principal que irá fazer a reprodução dos arquivos multimídia.

class MultimediaPlayer(QWidget):
    def __init__(self, playlist, parent=None):
        super(MultimediaPlayer, self).__init__(parent)
        self.getduration = 0
        self.maximize = False
        self.oldPos = None

        # Hack para enganar o pc, impedindo o bloqueio de tela
        self.key = PyKeyboard()
        self.caffeine = 1

        # Temporizador para o hack
        self.hack = QTimer()
        self.hack.setInterval(10000)
        self.hack.timeout.connect(self.runHack)
        self.hack.start()

        # Atribuindo as propriedades da interface principal do programa
        self.setWindowTitle('Open Media Player')
        self.setWindowIcon(QIcon(setIcon()))
        self.setMinimumSize(800, 600)
        self.setAcceptDrops(True)  # Suporte para arrastar itens ao programa
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

        # Necessário para a criação da playlist
        self.playlist = QMediaPlaylist()
        self.mediaPlayer.setPlaylist(self.playlist)

        # Necessário para o funcionamento a playlist
        self.playlistModel = PlaylistModel()
        self.playlistModel.setPlaylist(self.playlist)

        # Define a lista dos itens que serão visualizados na playlist
        self.playlistView = QListView()
        self.playlistView.setModel(self.playlistModel)
        self.playlistView.setCurrentIndex(self.playlistModel.index(self.playlist.currentIndex(), 0))
        self.playlistView.activated.connect(self.jump)
        self.playlistView.setStyleSheet(open('css/playist.css').read())

        # Essa aqui é a barra que mostra o progresso da reprodução do arquivo multimídia
        self.positionSlider = Slider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.pointClicked.connect(self.setPosition)
        self.positionSlider.setStyleSheet(open('css/progressbar.css').read())

        # Layout só para ajustar a barra de progresso de reprodução
        self.positionLayout = QHBoxLayout()
        self.positionLayout.setContentsMargins(10, 5, 10, 5)
        self.positionLayout.addWidget(self.positionSlider)

        # Essa aqui cria uma linha horizontal no programa. A função dessa linha é só para
        # efeito visual mesmo.
        QHLine = QFrame(self)
        QHLine.setFrameShape(QFrame.HLine)
        QHLine.setFrameShadow(QFrame.Raised)
        QHLine.setStyleSheet('background: #333333; border: 1px solid #000000')

        # Container só para dar uma corzinha diferente para o layout da playlist
        self.panelSHPlaylist = QWidget()
        self.panelSHPlaylist.setStyleSheet('background: #000000')
        self.panelSHPlaylist.setFixedWidth(300)

        # Layout só para ajustar as propriedades da playlist
        self.positionSHPlaylist = QHBoxLayout(self.panelSHPlaylist)
        self.positionSHPlaylist.setContentsMargins(6, 6, 6, 6)
        self.positionSHPlaylist.setSpacing(0)
        self.positionSHPlaylist.addWidget(self.playlistView)

        # Widget para aplicar funcionalidades nos controles em playerControls
        self.controls = PlayerControls(self)
        self.controls.setState(self.mediaPlayer.state())  # Pega o estado do reprodutor
        self.controls.play.connect(self.setPlay)
        self.controls.pause.connect(self.mediaPlayer.pause)
        self.controls.next.connect(self.playlist.next)
        self.controls.previous.connect(self.setPrevious)
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

        if not set_json('playlist'):
            self.panelSHPlaylist.hide()

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

        # Atalhos de teclado dos controles
        self.shortcutC1 = QShortcut(QKeySequence(Qt.Key_P), self)
        self.shortcutC1.activated.connect(self.controls.pressPlay)
        self.shortcutC2 = QShortcut(QKeySequence(Qt.Key_S), self)
        self.shortcutC2.activated.connect(self.setStop)
        self.shortcutC3 = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.shortcutC3.activated.connect(self.controls.pressNext)
        self.shortcutC4 = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.shortcutC4.activated.connect(self.controls.pressPrevious)

        # Demais ações
        self.mediaPlayer.stateChanged.connect(self.controls.setState)   # Ação para o botão play/pause
        self.mediaPlayer.positionChanged.connect(self.positionChanged)  # Alteração da barra de execução
        self.mediaPlayer.durationChanged.connect(self.durationChanged)  # Setar o tempo de execução na barra
        self.playlist.currentIndexChanged.connect(self.playlistPositionChanged)  # Muda a posição na playlist.
        self.addToPlaylist(playlist)  # Adicionar itens a lista de execução


########################################################################################################################


    # Função para executar o hack contra o bloqueio
    def runHack(self):
        if self.caffeine == 1 & self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.key.tap_key(self.key.control_key)


    # Função usada para abrir arquivos multimídia no programa.
    def openFile(self):
        fileNames, event = QFileDialog.getOpenFileNames(self, "Open Multimedia Files", QDir.homePath())
        self.addToPlaylist(fileNames)


    # Esse recurso vai adicionar os itens a lista de execução do programa.
    def addToPlaylist(self, fileNames):
        for name in fileNames:
            fileInfo = QFileInfo(name)
            if fileInfo.exists():
                url = QUrl.fromLocalFile(fileInfo.absoluteFilePath())

                # Adicionar os itens do arquivo m3u pelo método convencional, é furada. Dependendo da lista
                # que você adicionar, vai dar zica. Os caracteres não vão reconhecer e aí na hora de adicionar
                # os itens do arquivo m3u, vai zoar esses caracteres e o item da lista não será reconhecido.
                # Por isso, reinventei a roda e fiz essa manobra que funciona.
                if fileInfo.suffix().lower() == 'm3u':
                    local = dirname(name)
                    with open(name, 'r', encoding='utf8') as m3u:
                        for linha in m3u:
                            if not '#' in linha:
                                self.playlist.addMedia(QMediaContent(
                                    QUrl.fromLocalFile(local + '/' + linha.rstrip())))
                else:
                    self.playlist.addMedia(QMediaContent(url))
            else:
                url = QUrl(name)
                if url.isValid():
                    self.playlist.addMedia(QMediaContent(url))
        if self.getduration == 0:
            self.mediaPlayer.play()  # Play automático


    # Isso aqui permite que seja mudado o posicionamento do item selecionado. Sem isso, os itens na playlist não
    # ficam selecionados ao reproduzir os arquivos multimídia e nem mudam a seleção ao tocar a próxima mídia ou
    # a anterior. Por isso esse controle precisa ser feito.
    def playlistPositionChanged(self, position):
        self.playlistView.setCurrentIndex(self.playlistModel.index(position, 0))


    # essa função é chamada quando você dá um duplo clique em um item da playlist,
    # para que esse item possa ser reproduzido.
    def jump(self, index):
        if index.isValid():
            self.playlist.setCurrentIndex(index.row())
            self.mediaPlayer.play()


    # Função que só é necessária por conta da redefinição do positionSlider em setStop. É necessário definir
    # novamente o positionSlider para que ele possa funcionar perfeitamente.
    def setPlay(self):
        self.positionSlider.setMaximum(self.getduration)
        self.mediaPlayer.play()


    # É só por frescura mesmo. Se o primeiro item da lista estiver reproduzindo, ao pressionar previous ele executa
    # o último item como se estivesse fazendo o retorno.
    def setPrevious(self):
        if self.playlist.currentIndex() == 0:
            self.playlist.setCurrentIndex(self.playlistModel.rowCount())
        self.playlist.previous()


    # Função para parar a reprodução e também forçar o positionSlider a voltar para o início, pois não é
    # visualmente aceitável parar a execução e progresso da execução ficar onde está.
    def setStop(self):
        self.mediaPlayer.stop()
        self.positionSlider.setMaximum(0)


    # Função necessária para posicionar o tempo de execução no slider que mostra o progresso de execução.
    def positionChanged(self, position):
        if not self.positionSlider.isSliderDown():
            # Desativando os eventos preventivamente para evitar que a atualização desencadeie um evento
            # setPosition causando travamentos.
            self.positionSlider.blockSignals(True)
            self.positionSlider.setValue(position)
            self.positionSlider.blockSignals(False)


    # Ao abrir e executar um arquivo multimídia, o tempo de execução será definido no positionSlider.
    def durationChanged(self, duration):
        self.getduration = duration
        self.positionSlider.setMaximum(duration)


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
        self.panelSHPlaylist.hide()
        self.panelControl.hide()
        self.showFullScreen()


    # E esse desabilita a tela cheia.
    def unFullScreen(self):
        if self.isFullScreen():
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.panelControl.show()
            self.showNormal()
            if self.maximize:
                self.showMaximized()
                self.maximize = False
            if set_json('playlist'):
                self.panelSHPlaylist.show()


    # Mostrar e ocultar a playlist através de menu de contexto.
    def showPlayList(self):
        if not set_json('playlist'):
            self.panelSHPlaylist.show()
            write_json('playlist', True)
        else:
            self.panelSHPlaylist.hide()
            write_json('playlist', False)


    # Função especial que vai ser acionada ao pressionar o botão direito do mouse
    # para exibir o menu de contexto.
    def contextMenuRequested(self, point):
        QApplication.setOverrideCursor(Qt.ArrowCursor)

        # Verificação das configurações da lista de reprodução
        if set_json('playlist') is False:
            text = 'Show Playlist'
        else:
            text = 'Hide Playlist'

        # Menu de contexto personalizado para o programa no capricho
        menu = QMenu()
        menu.setStyleSheet(open('css/contextmenu.css').read())

        openMenu = QAction(setIconTheme(self, theme, 'folder'), 'Open', self)
        openMenu.setShortcut('Ctrl+O')
        openMenu.triggered.connect(self.openFile)

        controlPlaylist = QAction(setIconTheme(self, theme, 'playlist'), text, self)
        controlPlaylist.triggered.connect(self.showPlayList)

        fullScreen = QAction(setIconTheme(self, theme, 'fullscreen'), 'FullScreen', self)
        fullScreen.setShortcut('Alt+Enter')
        fullScreen.triggered.connect(self.onFullScreen)

        openSettings = QAction(setIconTheme(self, theme, 'settings'), 'Settings', self)
        openSettings.setShortcut('Alt+S')

        openAbout = QAction(setIconTheme(self, theme, 'about'), 'About', self)
        openAbout.triggered.connect(self.showAbout)

        # Montando o menu de contexto
        menu.addAction(openMenu)
        menu.addSeparator()
        menu.addAction(controlPlaylist)
        menu.addAction(fullScreen)
        menu.addSeparator()
        menu.addAction(openSettings)
        menu.addSeparator()
        menu.addAction(openAbout)

        # O menu de contexto não precisa aparecer em modo fullscreen.
        if not self.isFullScreen():
            menu.exec_(self.mapToGlobal(point))


    # Verificando se o objeto arrastado pode ser solto em nosso aplicativo. Sim, com isso o programa terá
    # suporte para arrastar e soltar os itens na lista de reprodução.
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()


    # Função para adicionar os itens arrastados à lista de reprodução.
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            self.playlist.addMedia(QMediaContent(url))
        self.playlistModel.layoutChanged.emit()

        # Se não tem nada sendo reproduzido no momento, vai ser reproduzido o primeiro dos recém-adicionados.
        if self.mediaPlayer.state() != QMediaPlayer.PlayingState:
            i = self.playlist.mediaCount() - len(event.mimeData().urls())
            self.playlist.setCurrentIndex(i)
            self.mediaPlayer.play()


    # Para executar ações quando o mouse é movido para dentro do programa.
    def enterEvent(self, event):
        self.caffeine = 1  # Ativa o hack para não bloquear a tela.


    # Para executar ações quando o mouse é movido para fora do programa.
    def leaveEvent(self, event):
        self.caffeine = 0  # Desativa o hack.


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
    checkSettings()
    openMediaplayer = QApplication(argv)
    multimediaPlayer = MultimediaPlayer(argv[1:])
    # multimediaPlayer.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    multimediaPlayer.show()
    exit(openMediaplayer.exec_())  # Finalização correta do programa
