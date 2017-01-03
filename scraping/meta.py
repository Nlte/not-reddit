#Créé par Vivien Letonnellier pour le projet WOTOY

import os
import webbrowser
import urllib.request
import re
import xml.etree.ElementTree
import time
from bs4 import BeautifulSoup
import sys

# Principe utilisé
#   Lecture des tags

#Mets en format CSV pour excel
def format_to_csv3(text, f):
	text = str(text).replace('\n',' ')
	text = text + "\n"
	f.write(text)

#Ouvre le fichier du crawling
def open_file_crawling3(liste, path):
    f_linklist_read = open(path,"r")
    liste = f_linklist_read.readlines()
    return liste

#Le scraping des meta données
def scraping_meta(PATH_CRAWLING_DATA, ID_PRESTA):

    print("\n--- Scraping Meta-data | RUN_ID : " + ID_PRESTA + " ---\n")

    #Initialisation des variables d'environnement
    linkList = []
    linkList = open_file_crawling3(linkList, PATH_CRAWLING_DATA)
    f = open("./scraping/data/" + ID_PRESTA + "_sortie_scraping_meta.csv","w")
    g = open("./scraping/data/" + ID_PRESTA + "_sortie_scraping_meta_langues.csv","w")
    liste_langue = {}

    #Parcours de la liste de liens
    for link in linkList:

        print("Analysing > " + str(link))

        #Si le site autorise le scraping
        try:
            #Lecture de la page web
            req = urllib.request.Request(link)
            response = urllib.request.urlopen(req)
            the_page = response.read()

            #Parser HTML
            soup = BeautifulSoup(the_page, "lxml")
            liste = []

            #Initialisation, pour éviter les doublons et les champs vides
            description_str = ""
            type_str = ""
            keywords_str = ""
            description_str_bool = False
            type_str_bool = False
            keywords_str_bool = False

    	    #Pour la langue
            for html in soup.find_all('html'):
               langue_found = False
               langue_str = str(html.get("lang"))
               if(langue_str != ""):
                    for langue in liste_langue:
                        if(langue_str == str(langue)):
                            liste_langue[langue_str] = liste_langue[langue_str] + 1
                            langue_found = True
                    if(langue_found == False):
                        liste_langue[langue_str] = 1

            print("Done > Language")

            #Pour le reste des meta données
            for meta_data in soup.find_all("meta"):
                property_str = str(meta_data.get("property")).lower()
                name_str = str(meta_data.get("name")).lower()
                content_str = str(meta_data.get("content"))
                if("og:description" in property_str and description_str_bool != True and content_str != ""):
                    description_str = content_str
                    description_str_bool = True
                if("og:type" in property_str and type_str_bool != True and content_str != ""):
                    type_str = content_str
                    type_str_bool = True
                # Balises simple HTML
                if("description" in name_str and description_str_bool != True):
                    description_str = content_str
                    description_str_bool = True
                if("keywords" in name_str and keywords_str_bool != True):
                    keywords_str = content_str
                    keywords_str_bool = True

            #On crée une liste de résultats
            liste.append(type_str)
            liste.append(description_str)
            liste.append(keywords_str)

            print("Done > Type")
            print("Done > Description")
            print("Done > Keywords")

            #On prépare la mise en forme pour le csv
            texte = ""
            for info in liste:
                texte = texte + str(info).replace(';',',') + ";"

            #On enregistre
            format_to_csv3(texte,f)

            print("Done > Saved\n")

        except:
            continue

    #On enregistre les statistiques de langue
    for langue, nombre in liste_langue.items():
        string = str(langue) + ";" + str(nombre)
        format_to_csv3(string,g)

    print("Done > Statistics")
