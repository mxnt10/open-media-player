#!/usr/bin/python3
# -*- coding: utf-8 -*-


########################################################################################################################
#
# Open Media Player — Reprodutor multimídia baseado em Python e PyQt5.
#
# Reprodutor multimídia inspirado na interface do Windows Media Player da Microsoft e no reprodutor Kantaris,
# sendo eles desenvolvidos apenas para Windows.
#
# Dependências:
#   — PyQt5
#   — PyUserInput
#
# Início do desenvolvimento: 14/11/2021
# Término do desenvolvimento: 20/11/2021
# Última atualização: 01/01/2022
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
from pymouse import PyMouse        # pip install PyUserInput
from os.path import dirname
from sys import argv

# Módulos do PyQt5
from PyQt5.QtCore import Qt, QDir, QUrl, QPoint, QFileInfo, QTimer, QEvent, QTime, pyqtSlot
from PyQt5.QtGui import QKeySequence, QPixmap, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtWidgets import (QApplication, QWidget, QFileDialog, QAction, QMenu, QHBoxLayout, QShortcut, QGridLayout,
                             QDesktopWidget, QFrame, QLabel, QGraphicsScene)

# Modulos integrados (src)
from about import AboutDialog
from controls import PlayerControls
from jsonTools import checkSettings, setJson, writeJson
from playlist import PlaylistModel
from utils import setIconTheme, setIcon
from widgets import VideoWidget, Slider, ListView, Label


# Classe Principal #####################################################################################################


# Foi usado QWidget ao invés de QMainWindow, senão não funciona a visualização do widget de vídeo.
# Essa classe cria a interface principal que irá fazer a reprodução dos arquivos multimídia.
class MultimediaPlayer(QWidget):
    def __init__(self, playlist, parent=None):
        super(MultimediaPlayer, self).__init__(parent)
        self.maximize = self.block = self.actMenu = self.sizeCheck = False
        self.getduration = self.control = 0
        self.theme = setJson('theme')
        self.oldPos = None

        # Hack para enganar o PC, impedindo o bloqueio de tela
        self.key = PyKeyboard()
        self.caffeine = 1

        # Temporizador para o hack
        self.hack = QTimer()
        self.hack.setInterval(10000)
        self.hack.timeout.connect(self.runHack)
        self.hack.start()

        # Temporizador que fica mapeando a posição do mouse
        self.mouse = PyMouse()
        self.timer = QTimer()
        self.timer.timeout.connect(self.changeMouse)
        self.timer.start()

        # Atribuindo as propriedades da interface principal do programa
        self.setWindowTitle('Open Media Player')
        self.setWindowIcon(QIcon(setIcon()))
        self.setMinimumSize(800, 600)
        self.setAcceptDrops(True)  # Suporte para arrastar itens ao programa
        self.center()

        # Cor de fundo
        color = self.palette()
        color.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(color)

        # Instrução para habilitar o menu de contexto no Open Media Player. O programa não contará
        # com uma barra de menu habilitada por padrão, então será usado menu de contexto.
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested[QPoint].connect(self.contextMenuRequested)

        # Criar widgets para a visualização do vídeo e playlist
        self.videoWidget = VideoWidget(self)
        self.videoItem = QGraphicsVideoItem()
        self.scene = QGraphicsScene(self.videoWidget)
        self.scene.addItem(self.videoItem)
        self.videoWidget.setScene(self.scene)
        self.playlist = QMediaPlaylist()

        # Parte principal do programa. O mediaPlayer vai ser definido com a engine QMediaPlayer que
        # irá fazer a reprodução de arquivos multimídia.
        self.mediaPlayer = QMediaPlayer()
        self.mediaPlayer.mediaStatusChanged.connect(self.mediaData)
        self.mediaPlayer.stateChanged.connect(self.setAction)
        self.mediaPlayer.setVideoOutput(self.videoItem)
        self.mediaPlayer.setPlaylist(self.playlist)

        # Necessário para o funcionamento a playlist
        self.playlistModel = PlaylistModel()
        self.playlistModel.setPlaylist(self.playlist)

        # Define a lista dos itens que serão visualizados na playlist
        self.playlistView = ListView()
        self.playlistView.setModel(self.playlistModel)
        self.playlistView.setCurrentIndex(self.playlistModel.index(self.playlist.currentIndex(), 0))
        self.playlistView.activated.connect(self.jump)
        self.playlistView.setStyleSheet(open('qss/playist.qss').read())

        # Essa aqui é a barra que mostra o progresso da reprodução do arquivo multimídia
        self.positionSlider = Slider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.pointClicked.connect(self.setPosition)
        self.positionSlider.eventPoint.connect(self.changeBlock)

        # Labels para cuidar do tempo de duração e o progresso de execução do arquivo multimídia
        self.progress = Label()
        self.duration = Label()
        self.progress.setText('--:--')
        self.duration.setText('--:--')
        self.progress.eventPoint.connect(self.changeBlock)
        self.duration.eventPoint.connect(self.changeBlock)

        # Isso aqui funciona como um conteiner para colorir os layouts dos controles.
        # Aplicando gradiente na barra de progresso.
        self.panelSlider = QWidget()
        self.positionLayout = QHBoxLayout(self.panelSlider)
        self.positionLayout.setContentsMargins(5, 2, 5, 2)
        self.positionLayout.addWidget(self.progress)
        self.positionLayout.addWidget(self.positionSlider)
        self.positionLayout.addWidget(self.duration)

        # Cria uma linha para melhor delimitação e efeito visual na lista de reprodução
        self.line = QFrame()
        self.line.setFrameShape(QFrame.VLine)
        self.line.setFrameShadow(QFrame.Raised)

        # Container só para dar uma corzinha diferente para o layout da playlist
        self.panelSHPlaylist = QWidget()
        self.panelSHPlaylist.setMinimumWidth(300)
        self.panelSHPlaylist.setStyleSheet(open('qss/playist.qss').read())

        # Layout só para ajustar as propriedades da playlist
        self.positionSHPlaylist = QHBoxLayout(self.panelSHPlaylist)
        self.positionSHPlaylist.setContentsMargins(5, 7, 10, 0)
        self.positionSHPlaylist.setSpacing(0)
        self.positionSHPlaylist.addWidget(self.line)
        self.positionSHPlaylist.addWidget(self.playlistView)

        # Widget para aplicar funcionalidades nos controles em playerControls
        self.controls = PlayerControls(self)
        self.controls.setState(self.mediaPlayer.state())  # Pega o estado do reprodutor
        self.controls.setVolume(self.mediaPlayer.volume())
        self.controls.setMuted(self.controls.isMuted())
        self.controls.play.connect(self.setPlay)
        self.controls.pause.connect(self.mediaPlayer.pause)
        self.controls.next.connect(self.playlist.next)
        self.controls.previous.connect(self.setPrevious)
        self.controls.stop.connect(self.setStop)
        self.controls.changeVolume.connect(self.mediaPlayer.setVolume)
        self.controls.changeMuting.connect(self.mediaPlayer.setMuted)
        self.controls.eventPoint.connect(self.changeBlock)

        # Aplicar gladiente na barra de progresso e ajustar os controles abaixo do widget de vídeo
        self.panelControl = QWidget()
        self.panelControl.setStyleSheet(open('qss/controls.qss').read())
        self.controlLayout = QHBoxLayout(self.panelControl)
        self.controlLayout.setContentsMargins(0, 0, 0, 8)
        self.controlLayout.addWidget(self.controls)

        # Acho legal entrar com uma logo no programa
        self.startLogo = QLabel()
        self.startLogo.setPixmap(QPixmap(setIcon(logo=True)))
        self.startLogo.setAlignment(Qt.AlignCenter)

        # Criando um layout para mostrar o conteiner com os widgets e layouts personalizados
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.videoWidget, 0, 0)
        self.layout.addWidget(self.startLogo, 0, 0)
        self.layout.addWidget(self.panelSHPlaylist, 0, 1, 1, 2)
        self.layout.addWidget(self.panelSlider, 1, 0, 1, 3)
        self.layout.addWidget(self.panelControl, 2, 0, 1, 3)
        self.setLayout(self.layout)

        if not setJson('playlist'):
            self.panelSHPlaylist.hide()
            self.hideControls()

        # Configurações de atalhos de teclado
        self.shortcut1 = QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_A), self)
        self.shortcut1.activated.connect(self.openFile)
        self.shortcut2 = QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_O), self)
        self.shortcut2.activated.connect(self.openFile)
        self.shortcut3 = QShortcut(QKeySequence(Qt.AltModifier + Qt.Key_Return), self)
        self.shortcut3.activated.connect(self.controlFullScreen)
        self.shortcut4 = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.shortcut4.activated.connect(self.unFullScreen)
        self.shortcut5 = QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_H), self)
        self.shortcut5.activated.connect(self.controls.setShuffle)
        self.shortcut6 = QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_T), self)
        self.shortcut6.activated.connect(self.controls.setReplay)
        self.shortcut7 = QShortcut(QKeySequence(Qt.ControlModifier + Qt.Key_Q), self)
        self.shortcut7.activated.connect(self.close)

        # Atalhos de teclado dos controles
        self.shortcutC1 = QShortcut(QKeySequence(Qt.Key_P), self)
        self.shortcutC1.activated.connect(self.controls.pressPlay)
        self.shortcutC2 = QShortcut(QKeySequence(Qt.Key_S), self)
        self.shortcutC2.activated.connect(self.setStop)
        self.shortcutC3 = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.shortcutC3.activated.connect(self.controls.pressNext)
        self.shortcutC4 = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.shortcutC4.activated.connect(self.controls.pressPrevious)

        # Demais ações
        self.mediaPlayer.stateChanged.connect(self.controls.setState)   # Ação para o botão play/pause
        self.mediaPlayer.positionChanged.connect(self.positionChanged)  # Alteração da barra de execução
        self.mediaPlayer.durationChanged.connect(self.durationChanged)  # Setar o tempo de execução na barra
        self.playlist.currentIndexChanged.connect(self.playlistPositionChanged)  # Muda a posição na playlist
        self.mediaPlayer.volumeChanged.connect(self.controls.setVolume)  # Controle de volume
        self.mediaPlayer.mutedChanged.connect(self.controls.setMuted)  # Áudio no mudo
        self.addToPlaylist(playlist)  # Adicionar itens a lista de execução


# Funções ##############################################################################################################


    # Ação a ser executada após alterar o estado de execução. Nesse caso, a logo será exibida ao parar a execução.
    @pyqtSlot(QMediaPlayer.State)
    def setAction(self, state):
        if state == QMediaPlayer.StoppedState:
            self.startLogo.show()


    # Função para executar o hack contra o bloqueio.
    def runHack(self):
        if self.caffeine == 1 & self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.key.tap_key(self.key.control_key)


    # Função que será usada para a extração de informações dos arquivos multimídia.
    def mediaData(self):
        # Aqui, o widget de vídeo só vai ser liberado se o arquivo multimídia for um vídeo. Não precisa esconder a
        # logo se o arquivo a ser reproduzido for um áudio.
        if self.mediaPlayer.state() == 1:
            if self.mediaPlayer.metaData('VideoCodec') is not None:
                self.startLogo.hide()
            elif self.mediaPlayer.metaData('AudioCodec') is not None:
                self.startLogo.show()


    # Função usada para abrir arquivos multimídia no programa.
    def openFile(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 'Open Multimedia Files', QDir.homePath(),
            'Video Files (*.3gp *.3gpp *.m4v *.mp4 *.m2v *.mp2 *.mpeg *.mpg *.vob *.ogg *.ogv *.mov *.rmvb *.webm '
            '*.flv *.mkv *.wmv *.avi *.divx);;'
            'Audio Files (*.ac3 *.flac *.mid *.midi *.m4a *.mp3 *.opus *.mka *.wma *.wav);;'
            '3GPP Multimedia Files (*.3ga *.3gp *.3gpp);;3GPP2 Multimedia Files (*.3g2 *.3gp2 *.3gpp2);;'
            'AVI Video (*.avf *.avi *.divx);;Flash Video (*.flv);;Matroska Video (*.mkv);;'
            'Microsoft Media Format (*.wmp);;MPEG Video (*.m2v *.mp2 *.mpe *.mpeg *.mpg *.ts *.vob *.vdr);;'
            'MPEG-4 Video (*.f4v *.lrv *.m4v *.mp4);;OGG Video (*.ogg *.ogv);;'
            'QuickTime Video (*.moov *.mov *.qt *.qtvr);;RealMedia Format (*.rv *.rvx *.rmvb);;'
            'WebM Video (*.webm);;Windows Media Video (*.wmv);;'
            'AAC Audio (*.aac *.adts *.ass );;Dolby Digital Audio (*.ac3);;FLAC Audio (*.flac);;'
            'Matroska Audio (*.mka);;MIDI Audio (*.kar *.mid *.midi);;MPEG-4 Audio (*.f4a *.m4a);;'
            'MP3 Audio (*.mp3 *.mpga);;OGG Audio (*.oga *.opus *.spx);;Windows Media Audio (*.wma);;'
            'WAV Audio (*.wav);;WavPack Audio (*.wp *.wvp);;Media Playlist (*.m3u *.m3u8);;All Files (*);;')
        self.addToPlaylist(files)


    # Esse recurso vai adicionar os itens a lista de execução do programa.
    def addToPlaylist(self, fileNames):
        for name in fileNames:
            fileInfo = QFileInfo(name)
            if fileInfo.exists():
                url = QUrl.fromLocalFile(fileInfo.absoluteFilePath())

                # Adicionar os itens do arquivo m3u pelo método convencional, é furada. Dependendo da lista
                # que você adicionar, vai dar zica. Os caracteres não vão reconhecer e na hora de adicionar
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
        if self.playlist.currentIndex() != (-1):
            location = self.playlist.media(self.playlist.currentIndex()).canonicalUrl()


    # Essa função é chamada quando é dado um duplo clique num item da playlist,
    # para que esse item possa ser reproduzido.
    def jump(self, index):
        if index.isValid():
            self.playlist.setCurrentIndex(index.row())
            self.mediaPlayer.play()


    # Função que só é necessária por conta da redefinição do positionSlider em setStop. É necessário definir
    # novamente o positionSlider para ele poder funcionar perfeitamente.
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
        # Desativando os eventos preventivamente para evitar que a atualização desencadeie um evento
        # setPosition causando travamentos.
        self.positionSlider.blockSignals(True)
        self.positionSlider.setValue(position)
        self.positionSlider.blockSignals(False)
        if self.mediaPlayer.state() != QMediaPlayer.StoppedState:
            time = QTime(0, 0, 0, 0)
            time = time.addMSecs(self.mediaPlayer.position())
            self.progress.setText(time.toString())


    # Definindo o tamanho para a variável progress, que vai exibir o progresso de execução.
    def sizeLabel(self):
        if not self.sizeCheck:
            self.progress.setFixedWidth(self.progress.size().width() + 3)
            self.sizeCheck = True


    # Ao abrir e executar um arquivo multimídia, o tempo de execução será definido no positionSlider.
    def durationChanged(self, duration):
        self.getduration = duration
        self.positionSlider.setMaximum(duration)
        time = QTime(0, 0, 0, 0)
        time = time.addMSecs(self.mediaPlayer.duration())
        self.duration.setText(time.toString())
        self.videoWidget.fitInView(self.videoItem, Qt.KeepAspectRatio)  # Rendenizando o vídeo

        # Ajustes para a variável progress para a barra de execução não ficar mexendo do lugar
        QTimer.singleShot(500, self.sizeLabel)


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


    # Função para a exibição dos controles.
    def showControls(self):
        self.panelSlider.show()
        self.panelControl.show()


    # Função para ocultar os controles.
    def hideControls(self):
        self.panelSlider.hide()
        self.panelControl.hide()


    # Controle do modo tela cheia feito pelo Alt+Enter.
    def controlFullScreen(self):
        if self.isFullScreen():
            self.unFullScreen()
        else:
            self.onFullScreen()
        self.control = 0


    # Esses carinhas vão ser executados de dentro de VideoWidget e PixmapLabel. Esse aqui,
    # é para habilitar o modo de tela cheia.
    def onFullScreen(self):
        if multimediaPlayer.isMaximized():
            self.maximize = True
        QApplication.setOverrideCursor(Qt.BlankCursor)
        self.panelSHPlaylist.hide()
        self.hideControls()
        self.showFullScreen()


    # E esse desabilita a tela cheia.
    def unFullScreen(self):
        if self.isFullScreen():
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.showNormal()
            if self.maximize:
                self.showMaximized()
                self.maximize = False
            if setJson('playlist'):
                self.panelSHPlaylist.show()
                self.showControls()


    # Mostrar e ocultar a playlist através de menu de contexto.
    def showPlayList(self):
        if not setJson('playlist'):
            self.panelSHPlaylist.show()
            self.panelSlider.show()
            self.panelControl.show()
            writeJson('playlist', True)
        else:
            self.panelSHPlaylist.hide()
            writeJson('playlist', False)


    # Função especial que vai ser acionada ao pressionar o botão direito do mouse
    # para exibir o menu de contexto.
    def contextMenuRequested(self, point):
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        self.actMenu = True

        # Verificação das configurações da lista de reprodução
        if not setJson('playlist'):
            text = 'Show Playlist'
        else:
            text = 'Hide Playlist'

        # Menu de contexto personalizado para o programa no capricho
        menu = QMenu()
        menu.setStyleSheet(open('qss/contextmenu.qss').read())

        openMenu = QAction(setIconTheme(self, self.theme, 'folder'), 'Open', self)
        openMenu.setShortcut('Ctrl+O')
        openMenu.triggered.connect(self.openFile)

        controlPlaylist = QAction(setIconTheme(self, self.theme, 'playlist'), text, self)
        controlPlaylist.triggered.connect(self.showPlayList)

        fullScreen = QAction(setIconTheme(self, self.theme, 'fullscreen'), 'FullScreen', self)
        fullScreen.setShortcut('Alt+Enter')
        fullScreen.triggered.connect(self.controlFullScreen)

        shuffle = QAction(setIconTheme(self, self.theme, 'shuffle-menu'), 'Shuffle', self)
        shuffle.setShortcut('Ctrl+H')
        shuffle.triggered.connect(self.controls.setShuffle)

        replay = QAction(setIconTheme(self, self.theme, 'replay-menu'), 'Replay', self)
        replay.setShortcut('Ctrl+T')
        replay.triggered.connect(self.controls.setReplay)

        openSettings = QAction(setIconTheme(self, self.theme, 'settings'), 'Settings', self)
        openSettings.setShortcut('Alt+S')

        openAbout = QAction(setIconTheme(self, self.theme, 'about'), 'About', self)
        openAbout.triggered.connect(self.showAbout)

        # Montando o menu de contexto
        if self.isFullScreen():
            menu.addAction(openMenu)
            menu.addSeparator()
            menu.addAction(fullScreen)
            menu.addSeparator()
            menu.addAction(shuffle)
            menu.addAction(replay)
        else:
            menu.addAction(openMenu)
            menu.addSeparator()
            menu.addAction(controlPlaylist)
            menu.addAction(fullScreen)
            menu.addSeparator()
            menu.addAction(shuffle)
            menu.addAction(replay)
            menu.addSeparator()
            menu.addAction(openSettings)
            menu.addSeparator()
            menu.addAction(openAbout)
        menu.exec_(self.mapToGlobal(point))


    # Somente para impedir a minimização dos controles ao posicionar o mouse sobre ele.
    def changeBlock(self, event):
        if event == 1:
            self.block = True
        elif event == 2:
            self.block = False


    # Função para mapear os movimentos do mouse. Quando o mouse está se mexendo, os controles aparecem.
    def changeMouse(self):
        x = self.mouse.position()[0]
        if self.mouse.position()[0] != x:  # Se esses valores são diferentes, o mouse tá se mexendo
            if self.control == 0:
                if not self.block and not self.actMenu:
                    if not setJson('playlist') or self.isFullScreen():
                        self.showControls()
                    QApplication.setOverrideCursor(Qt.ArrowCursor)
                    self.control = 1


# Eventos ##############################################################################################################


    # Verificando se o objeto arrastado pode ser solto no programa. Sim, com isso o programa terá
    # suporte para arrastar e soltar os itens na lista de reprodução.
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()


    # Função para adicionar os itens arrastados à lista de reprodução
    def dropEvent(self, event):
        for url in event.mimeData().urls():
            self.playlist.addMedia(QMediaContent(url))
        self.playlistModel.layoutChanged.emit()

        # Se não tem nada sendo reproduzido no momento, vai ser reproduzido o primeiro dos recém-adicionados
        if self.mediaPlayer.state() != QMediaPlayer.PlayingState:
            i = self.playlist.mediaCount() - len(event.mimeData().urls())
            self.playlist.setCurrentIndex(i)
            self.mediaPlayer.play()


    # Para executar ações quando o mouse é movido para dentro do programa
    def enterEvent(self, event):
        self.caffeine = 1  # Ativa o hack para não bloquear a tela
        if not setJson('playlist'):
            if self.actMenu:
                self.hideControls()
                self.control = 0
            elif not self.isFullScreen():
                self.showControls()
        self.actMenu = False


    # Para executar ações quando o mouse é movido para fora do programa
    def leaveEvent(self, event):
        self.caffeine = 0  # Desativa o hack
        if not setJson('playlist'):
            self.hideControls()


    # Evento para executar ações ao pressionar os botões da janela
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if int(self.windowState()) == 0:  # Restaurar
                writeJson('maximized', False)
            elif int(self.windowState()) == 1:  # Minimização
                pass
            elif int(self.windowState()) == 2:  # Maximização
                writeJson('maximized', True)
            elif int(self.windowState()) == 3:  # Minimização direta
                pass


    # Duplo clique para ativar e desativar o modo de tela cheia
    def mouseDoubleClickEvent(self, event):
        if self.isFullScreen() and event.button() == Qt.LeftButton:
            self.unFullScreen()
        elif not self.block:
            self.onFullScreen()
        self.control = 0


    # Usei esse mapeador geral de eventos porque queria pegar evento de quando o mouse para
    def event(self, event):
        if event.type() == 110:  # Executa ações quando o mouse para de se mexer
            if not self.block:
                if not setJson('playlist') or self.isFullScreen():
                    self.hideControls()
                QApplication.setOverrideCursor(Qt.BlankCursor)
                self.control = 0
        return QWidget.event(self, event)


########################################################################################################################


# início do programa
if __name__ == '__main__':
    checkSettings()
    openMediaplayer = QApplication(argv)
    multimediaPlayer = MultimediaPlayer(argv[1:])
    if setJson('maximized') is True:
        multimediaPlayer.showMaximized()
    else:
        multimediaPlayer.show()
    exit(openMediaplayer.exec_())  # Finalização correta do programa
