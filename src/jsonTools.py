#!/usr/bin/python3
# -*- coding: utf-8 -*- 

# Import modules
from json import dump, load
from logging import warning
from os import makedirs, remove
from os.path import expanduser, isdir

j_folder = expanduser('~/.config/omp')
j_file = j_folder + '/settings.json'

default_js = {
  "playlist": False,
  "theme": "circle"
}


# Função para verificar se o arquivo de configuração está disponível. Caso contrário, ele será criado.
def checkSettings():
    try:
        with open(j_file):
            pass
    except Exception as msg:
        warning("\033[33m %s. \033[32mCreate a settings.json ...\033[m", msg)
        if not isdir(j_folder):
            makedirs(j_folder)
        with open(j_file, 'w') as jfile:
            dump(default_js, jfile, indent=2)


# Lê um item do arquivo de configuração.
def set_json(op):
    with open(j_file) as jf:
        objJson = load(jf)
    return objJson[op]


# Altera uma opção no arquivo de configuração.
def write_json(op, val):
    with open(j_file, 'r') as jf:
        objJson = load(jf)
        objJson[op] = val

    # Substituindo o arquivo original.
    remove(j_file)
    with open(j_file, 'w') as jf:
        dump(objJson, jf, indent=2)
