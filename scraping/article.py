#Créé par Vivien Letonnellier pour le projet WOTOY

import os
import webbrowser
import urllib.request
import re
import xml.etree.ElementTree
import time
from bs4 import BeautifulSoup
import sys

# Principes utilisés :
#   Distance HTML
#   Densité de texte
#   Densité de lien
#   Seuils

#Enlever les tags HTML
def remove_tags(text):
    return ''.join(xml.etree.ElementTree.fromstring(text).itertext())

#Enlever les tags HTML avec des REGEX
def remove_tags_hard(text):
    f = (re.compile('<script.*?</script>')).sub('',text)
    g = (re.compile('<style.*?</style>')).sub('',f)
    p = re.compile(r'<.*?>')
    return p.sub('', g)

#Définir ce qui semble être un mot
def isWord(string):
    test = re.split('\W+', string)
    test_enhanced = [x for x in test if x != '']
    if(len(test_enhanced) > 0):
        for j in test_enhanced:
            if '=' in j or '_' in j or '&' in j or '/' in j or '\\' in j or '.' in j or '{' in j or '[' in j or '}' in j or ']' in j or '@' in j or ';' in j or ':' in j:
                if "<br>" in string or "<strong>" in string or "</strong>" in string or "<em>" in string or "</em>" in string or "<i>" in string or "</i>" in string or "<br />" in string:
                    return True
                else:
                    return False
            else:
                return True
    else:
        return False

#Mets en format CSV pour excel
def format_to_csv(text, f):
	text = str(text).replace(';',',')
	text = str(text).replace('\n',' ')
	text = text + "\n"
	f.write(text)

#Ouvre un fichier et retourne son contenu
def open_file_crawling(liste, path):
    f_linklist_read = open(path,"r")
    liste = f_linklist_read.readlines()
    return liste

#Fonction principale de scraping des articles
def scraping_article(PATH_CRAWLING_DATA, ID_PRESTA) :

    print("\n--- Scraping Article | RUN_ID : " + ID_PRESTA + " ---\n")

    #Récupération du crawling
    linkList = []
    linkList = open_file_crawling(linkList, PATH_CRAWLING_DATA)

    #Chemin de sortie de l'algorithme
    f = open("./scraping/data/" + ID_PRESTA + "_sortie_scraping.csv","w")

    for link in linkList:

        print("Analysing > " + str(link))

        #Si le site autorise la collecte automatique
        try:
            #Téléchargement de la page web
            req = urllib.request.Request(link)
            response = urllib.request.urlopen(req)
            the_page = response.read()
            soup = BeautifulSoup(the_page, "lxml")

            #Seuil de la densité de texte
            MAX_WORDS = 80
            text_to_test = []
            distance_HTML = 0

            #Etude des blocs HTML
            for item in soup.find_all():

                distance_HTML += 1

                #Initialisation des variables d'analyse
                textBlock = ""
                linkString = []
                linkStrings = []
                numberLinkWords = 0
                numberWords = 0
                numberWordsWrapped = 0
                numberWrongWords = 0
                wrapsLine = 0
                number_words = 0

                #Récupération des liens pour la densité de liens
                linkStrings = item.find_all("a")
                linkWords = []

                #Récupération des mots compris dans des liens
                for linkString in linkStrings:
                    linkWords = str(linkString).split(" ")
                    for linkWord in linkWords:
                        if(isWord(linkWord)):
                            numberLinkWords += 1

                #Pré-traitement pour la détection de mots
                words = []
                item = str(item)
                item = item.replace(">","> ")
                item = item.replace("<"," <")
                words = item.split(" ")
                longueurTexte = 0

                #Détection de mots, et blocs de texte
                for word in words:
                    if(isWord(word)):
                        numberWords += 1
                        textBlock += word + " "
                        longueurTexte = len(textBlock)
                        if(longueurTexte % 80 == 0 and longueurTexte != 0):
                            wrapsLine += 1
                    else:
                        numberWrongWords += 1

                #Définition des caractéristiques d'un bloc de texte
                if(wrapsLine == 0):
                    numberWordsWrapped = numberWords
                    wrapsLine = 1
                else:
                    numberWordsWrapped = (80 * wrapsLine) - (longueurTexte % 80)

                #Calcul de la densité de texte
                textDensity = numberWordsWrapped / wrapsLine;
                if(numberWords != 0):
                    linkDensity = numberLinkWords / numberWords;
                else:
                    linkDensity = 0

                #Premier tri des blocs HTML
                if ((numberWords/6) > numberWrongWords):
                        try:
                            result = remove_tags(textBlock)
                            text_to_test.append([result,textDensity,linkDensity,distance_HTML])
                        except:
                            result = remove_tags_hard(textBlock)
                            text_to_test.append([result,textDensity,linkDensity,distance_HTML])

            print("Done > Text Blocks")
            print("Done > Text Density")
            print("Done > Link Density")

            #Initialisation des variables nécéssaires à l'algorithme C4.8
            i = 0
            text_to_test.insert(0, ["",0,0,0,False])
            text_to_test.append(["",0,0,0,False])

            #Arbre de décision C4.8, via des seuils définis par machine learning
            #Définition du contenu / non contenu
            while (i < (len(text_to_test) - 2)):
                i += 1
                if(len(text_to_test[i][0]) >= 80):
                    if (text_to_test[i][2] <= 0.333333):
                        if (text_to_test[i-1][2] <= 0.555556):
                            if(text_to_test[i][1] <= 9):
                                if(text_to_test[i+1][1] <= 10):
                                    if(text_to_test[i-1][1] <= 4):
                                        text_to_test[i].append(False)
                                    else:
                                        text_to_test[i].append(True)
                                else:
                                    text_to_test[i].append(True)
                            else:
                                if (text_to_test[i+1][1] == 0):
                                    text_to_test[i].append(False)
                                else:
                                    text_to_test[i].append(True)
                        else:
                            if (text_to_test[i+1][1] <= 11):
                                text_to_test[i].append(False)
                            else:
                                text_to_test[i].append(True)
                    else:
                        text_to_test[i].append(False)
                else:
                    text_to_test[i].append(False)

            #Suppression des blocs de non contenu
            i = 0
            for item in text_to_test:#
                if(item[4] == False):
                    del text_to_test[i]
                i += 1

            #Détection grossière des doublons
            i = 0
            j = 0
            while (i < (len(text_to_test) - j)):
                k = i+1
                while (k < (len(text_to_test) - j)):
                    if (text_to_test[k][0] in text_to_test[i][0]):
                        del text_to_test[i]
                        j += 1
                        i -= 1
                    k += 1
                    break
                i += 1

            #Suppression des doublons
            i = 0
            j = 0
            while (i < (len(text_to_test) - j)):
                if(text_to_test[i][4] == False):
                    del text_to_test[i]
                    i -= 1

                i += 1

            print("Done > Content Detection")

            #Initialisation des variables de seuil
            i = 1
            j = 0
            k = 0
            compteur = 0
            active = False
            seuil_debut = True

            #Détection du seuil de fin de texte, et suppression du post-seuil
            while (i < (len(text_to_test) - j)):
                if((text_to_test[i][3] - text_to_test[i-1][3]) > 60):
                    compteur = 0
                else:
                    compteur += 1
                    if(compteur > 4):
                        active = True
                        if(seuil_debut):
                            seuil_debut = False
                            k = i - compteur
                if(active and ((text_to_test[i][3] - text_to_test[i-1][3]) > 60)):
                    del text_to_test[i]
                    i -= 1
                i += 1

            #Détection du seuil de début, et suppression du pré-seuil
            i = 0
            while (i < k):
                del text_to_test[0]
                i += 1

            print("Done > Thresholds")

            #Concaténation des blocs de texte
            result = ""
            for item in text_to_test:
                try:
                    result = result + str(item[0])
                except:
                    continue

            print("Done > Merge Text")

            #Enregistrement du résultat en CSV
            format_to_csv(result, f)

            print("Done > Saved\n")

        except:
            continue
