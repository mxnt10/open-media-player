
# Essa função aqui, que retorna essa parada grandona, é o que define o estilo da barra de execução da música. Aquela
# barra não ia combinar com os temas dos ícones.
def styleSheet():
    return """

QSlider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #444444;
    border-radius: 6px;
    width: 16px;
    margin: -3px 0;
}

QSlider::groove:horizontal {
    background: qlineargradient(y1: 0, y2: 1, stop: 0 #2e3436, stop: 1.0 #ffffff);
    border: 1px solid #444444;
    border-radius: 4px;
    height: 6px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient( y1: 0, y2: 1, stop: 0 #729fcf, stop: 1 #2a82da);
    border: 1px solid #444444;
    border-radius: 4px;
}

QSlider::sub-page:horizontal:disabled {
    background: #bbbbbb;
    border-color: #999999;
}

QSlider::add-page:horizontal:disabled {
    background: #2a82da;
    border-color: #999999;
}

QSlider::handle:horizontal:disabled {
    background: #2a82da;
}

QLineEdit {
    background: black;
    color: #585858;
    border: 0px solid #076100;
    font-size: 8pt;
    font-weight: bold;
}
    """


# Essa função apenas retorna o estilo que será usado para as linhas.
def styleLine():
    return 'background: #444444; border: 1px solid #000000'
