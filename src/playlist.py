
# Módulos do PyQt5
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, QFileInfo, Qt


########################################################################################################################


# Classe de playlist copiada dos projetos de exemplo do pyqt5.

class PlaylistModel(QAbstractItemModel):
    Title, ColumnCount = range(2)

    def __init__(self, parent=None):
        super(PlaylistModel, self).__init__(parent)
        self.m_playlist = None


    # Esse item, faz uma contagem dos itens da playlist.
    def rowCount(self, parent=QModelIndex()):
        return self.m_playlist.mediaCount() if self.m_playlist is not None and not parent.isValid() else 0


    # Esse item é necessário para calcular as colunas para serem criadas para serem preenchidas com a lista de
    # arquivos multimídia a serem executados.
    def columnCount(self, parent=QModelIndex()):
        return self.ColumnCount if not parent.isValid() else 0


    # Essa é a função responsável pela indexação os itens a lista de reprodução.
    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column) \
            if self.m_playlist is not None and not parent.isValid() and 0 <= row < self.m_playlist.mediaCount()\
            and 0 <= column < self.ColumnCount else QModelIndex()


    # Essa função é interessante. Ela coloca o nome os arquivos multimídia na lista. Sem ela a lista fica
    # sem os nomes dos arquivos.
    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            if index.column() == self.Title:
                location = self.m_playlist.media(index.row()).canonicalUrl()
                return QFileInfo(location.path()).fileName()  # Retorno da localização do arquivo
            return self.m_data[index]  # Para a indexação do arquivo à lista
        return None


    # Função para manipular a lista de reprodução.
    def setPlaylist(self, playlist):
        if self.m_playlist is not None:
            self.m_playlist.mediaAboutToBeInserted.disconnect(self.beginInsertItems)
            self.m_playlist.mediaInserted.disconnect(self.endInsertRows)
            self.m_playlist.mediaAboutToBeRemoved.disconnect(self.beginRemoveItems)
            self.m_playlist.mediaRemoved.disconnect(self.endRemoveRows)
            self.m_playlist.mediaChanged.disconnect(self.changeItems)

        self.beginResetModel()
        self.m_playlist = playlist

        if self.m_playlist is not None:
            self.m_playlist.mediaAboutToBeInserted.connect(self.beginInsertItems)
            self.m_playlist.mediaInserted.connect(self.endInsertRows)
            self.m_playlist.mediaAboutToBeRemoved.connect(self.beginRemoveItems)
            self.m_playlist.mediaRemoved.connect(self.endRemoveRows)
            self.m_playlist.mediaChanged.connect(self.changeItems)
        self.endResetModel()


    def beginInsertItems(self, start, end):
        self.beginInsertRows(QModelIndex(), start, end)


    def beginRemoveItems(self, start, end):
        self.beginRemoveRows(QModelIndex(), start, end)


    def changeItems(self, start, end):
        self.dataChanged.emit(self.index(start, 0), self.index(end, self.ColumnCount))


    # def parent(self, child):
    #     return QModelIndex()
    #
    #
    # def playlist(self):
    #     return self.m_playlist
