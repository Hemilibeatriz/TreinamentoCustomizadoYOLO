# Créditos a: Jones Granatyr :)

import os
import cv2
import numpy as np
from tqdm import tqdm
import argparse
import fileinput

# função que transforma as coordenadas XMin, YMin, XMax, YMax no formato normalizado pro YOLO/darknet
def convert(nome_file, coords):
    os.chdir("..")
    imagem = cv2.imread(nome_file + ".jpg")
    coords[2] -= coords[0]         # diferença largura (x_fim - x_inicio)
    coords[3] -= coords[1]         # diferença altura (y_fim - y_inicio)
    x_dif = int(coords[2] / 2)     # converte diferença_largura pra int
    y_dif = int(coords[3] / 2)     # converte diferença_altura pra int
    coords[0] = coords[0] + x_dif  # x_inicio + diferença largura
    coords[1] = coords[1] + y_dif  # y_inicio + diferença altura
    largura = int(imagem.shape[1]) # = largura da imagem
    altura = int(imagem.shape[0])  # = altura da imagem
    coords[0] /= largura           # x = (int((<x fim> - <x inicio>) / 2) + <x inicio>) / <largura_imagem>
    coords[1] /= altura            # (int((<y fim> - <y inicio>) / 2) + <y inicio)) / <altura_imagem>
    coords[2] /= largura           # largura = (<x fim> - <x inicio>) / <largura_imagem>
    coords[3] /= altura            # altura (<y fim> - <y inicio>) / <altura_imagem>
    os.chdir("Label")
    return coords

ROOT_DIR = os.getcwd()

# cria um dicionario para mapear os nomes das classes em numeros para o YOLO
classes = {}
with open("classes.txt", "r") as myFile:
    for num, line in enumerate(myFile, 0):
        line = line.rstrip("\n")
        classes[line] = num
    myFile.close()
# vai ate o diretorio do dataset 
os.chdir(os.path.join("OID", "Dataset"))
DIRS = os.listdir(os.getcwd())

# percorre as pastas train, validation e test 
for DIR in DIRS:
    if os.path.isdir(DIR):
        
        # se contem ponto no nome da pasta entao pula pra proxima (pra por ex ignorar o .ipynb_checkpoints)
        if "." in DIR:
            continue
        
        os.chdir(DIR)
        print("Subdiretorio atual:", DIR)
        
        class_dirs = os.listdir(os.getcwd())
        # percorre todas as classes para alterar os annotations
        for class_dir in class_dirs:
            if os.path.isdir(class_dir):
                
                if "." in class_dir:
                    continue
                
                os.chdir(class_dir)
                print("Convertendo os annotations para a classe: ", class_dir)
                
                # vai até a pasta Label que é onde os annotations estão
                os.chdir("Label")

                for filename in tqdm(os.listdir(os.getcwd())):
                    nome_file = str.split(filename, ".")[0]
                    if filename.endswith(".txt"):
                        annotations = []
                        with open(filename) as f:
                            # agora altera os valores para cada linha dentro do txt 
                            for line in f:
                                for class_type in classes:
                                    line = line.replace(class_type, str(classes.get(class_type)))
                                labels = line.split()
                                coords = np.asarray([float(labels[1]), float(labels[2]), float(labels[3]), float(labels[4])])
                                coords = convert(nome_file, coords)
                                labels[1], labels[2], labels[3], labels[4] = coords[0], coords[1], coords[2], coords[3]
                                newline = str(labels[0]) + " " + str(labels[1]) + " " + str(labels[2]) + " " + str(labels[3]) + " " + str(labels[4])
                                line = line.replace(line, newline) # atualiza os valores da linha
                                annotations.append(line) # adiciona ao final da linha
                            f.close()
                        os.chdir("..")
                        # agora precisamos voltar um diretorio acima pois iremos salvar os novos txt na mesma pasta onde estão as imagens 
                        with open(filename, "w") as outfile:
                            for line in annotations:
                                outfile.write(line)
                                outfile.write("\n")
                            outfile.close()
                        os.chdir("Label")
                os.chdir("..")
                os.chdir("..")
        os.chdir("..")
