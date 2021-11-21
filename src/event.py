
# Aqui, a ideia é personalizar todos os eventos de widgets e botões necessários e mandar tudo pra cá.
########################################################################################################################

# Módulos do PyQt5
from PyQt5.QtCore import QSize, QTimer, pyqtSlot
from PyQt5.QtWidgets import QPushButton


########################################################################################################################


# Essa classe controla todos os efeitos dos botões do programa.
class PushButton(QPushButton):
    def __init__(self, num, parent=None):
        """
            @param num: Aqui você entra com o tamanho dos ícones.
        """
        super(PushButton, self).__init__(parent)
        self.__fading_button = None
        self.num = num
        self.pressed.connect(lambda: self.onEffect(num))
        self.setStyleSheet('border: 0')


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
