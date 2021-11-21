#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Módulos importados
from logging import warning, error
from os.path import isfile

# Módulos do PyQt5
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QStyle


########################################################################################################################


# Função que vai definir o ícone do programa
def setIcon(logo=False):

    # Por padrão, a função retorna o ícone do programa, a não ser que logo for
    # definida como True.
    if logo:
        img = 'logo'
    else:
        img = 'omp'

    icon = '/usr/share/pixmaps/' + img + '.png'
    l_icon = '../appdata/' + img + '.png'

    try:
        with open(icon):
            return icon
    except Exception as msg:
        warning('\033[33m %s.\033[32m Use a local icon...\033[m', msg)
        try:
            with open(l_icon):
                return l_icon
        except Exception as msg:
            # Exception for icon not found
            error('\033[31m %s \033[m', msg)
            return None


# Essa função tem duas utilidades. Se o tema selecionado for system essa função será usada para a definição dos
# ícones. E também caso um determinado tema não tenha um determinado ícone em específico. Aí pra não ficar sem
# ícone usa o do sistema mesmo.
def defaultSystemIcons(self, icon):
    if icon == 'play':
        return self.style().standardIcon(QStyle.SP_MediaPlay)
    elif icon == 'pause':
        return self.style().standardIcon(QStyle.SP_MediaPause)
    elif icon == 'stop':
        return self.style().standardIcon(QStyle.SP_MediaStop)
    elif icon == 'folder':
        return self.style().standardIcon(QStyle.SP_DirIcon)
    elif icon == 'settings':
        return self.style().standardIcon(QStyle.SP_CustomBase)
    elif icon == 'about':
        return self.style().standardIcon(QStyle.SP_MessageBoxInformation)


# Função que vai selecionar o tema dos ícones
def setIconTheme(self, theme, icon):
    icon_theme = '/usr/share/omp/icons/'
    l_icon_theme = '../icons/'

    if theme == 'system':
        return defaultSystemIcons(self, icon)
    elif isfile(icon_theme + theme + '/' + icon + '.svg'):
        return QIcon(icon_theme + theme + '/' + icon + '.svg')
    elif isfile(icon_theme + theme + '/' + icon + '.png'):
        return QIcon(icon_theme + theme + '/' + icon + '.png')
    elif isfile(l_icon_theme + theme + '/' + icon + '.svg'):
        warning('\033[33m ' + icon + ' icon not found in system.\033[32m Use a local theme icons...\033[m')
        return QIcon(l_icon_theme + theme + '/' + icon + '.svg')
    elif isfile(l_icon_theme + theme + '/' + icon + '.png'):
        return QIcon(l_icon_theme + theme + '/' + icon + '.png')
    else:
        warning('\033[33m ' + icon + ' icon not found.\033[32m Use a default icon...\033[m')
        return defaultSystemIcons(self, icon)
