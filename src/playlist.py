
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, QFileInfo, Qt


class PlaylistModel(QAbstractItemModel):
    Title, ColumnCount = range(2)

    def __init__(self, parent=None):
        super(PlaylistModel, self).__init__(parent)
        self.m_playlist = None


    def rowCount(self, parent=QModelIndex()):
        return self.m_playlist.mediaCount() if self.m_playlist is not None and not parent.isValid() else 0


    def columnCount(self, parent=QModelIndex()):
        return self.ColumnCount if not parent.isValid() else 0


    def index(self, row, column, parent=QModelIndex()):
        return self.createIndex(row, column) if self.m_playlist is not None and not parent.isValid() and 0 <= row < self.m_playlist.mediaCount() and 0 <= column < self.ColumnCount else QModelIndex()


    def parent(self, child):
        return QModelIndex()


    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            if index.column() == self.Title:
                location = self.m_playlist.media(index.row()).canonicalUrl()
                return QFileInfo(location.path()).fileName()
            return self.m_data[index]
        return None


    def playlist(self):
        return self.m_playlist


    def setPlaylist(self, playlist):
        if self.m_playlist is not None:
            self.m_playlist.mediaAboutToBeInserted.disconnect(
                self.beginInsertItems)
            self.m_playlist.mediaInserted.disconnect(self.endInsertItems)
            self.m_playlist.mediaAboutToBeRemoved.disconnect(
                self.beginRemoveItems)
            self.m_playlist.mediaRemoved.disconnect(self.endRemoveItems)
            self.m_playlist.mediaChanged.disconnect(self.changeItems)

        self.beginResetModel()
        self.m_playlist = playlist

        if self.m_playlist is not None:
            self.m_playlist.mediaAboutToBeInserted.connect(
                self.beginInsertItems)
            self.m_playlist.mediaInserted.connect(self.endInsertItems)
            self.m_playlist.mediaAboutToBeRemoved.connect(
                self.beginRemoveItems)
            self.m_playlist.mediaRemoved.connect(self.endRemoveItems)
            self.m_playlist.mediaChanged.connect(self.changeItems)

        self.endResetModel()


    def beginInsertItems(self, start, end):
        self.beginInsertRows(QModelIndex(), start, end)


    def endInsertItems(self):
        self.endInsertRows()


    def beginRemoveItems(self, start, end):
        self.beginRemoveRows(QModelIndex(), start, end)


    def endRemoveItems(self):
        self.endRemoveRows()


    def changeItems(self, start, end):
        self.dataChanged.emit(self.index(start, 0), self.index(end, self.ColumnCount))
