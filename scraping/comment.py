import os
import webbrowser
import urllib.request
import re
import xml.etree.ElementTree
import time
from bs4 import BeautifulSoup
import sys
import numpy as np

# Principes utilisés :
#   Distance HTML
#   Similarité de tags
#   Seuils

def isWord(string):
    test = re.split('\W+', string)
    test_enhanced = [x for x in test if x != '']
    if(len(test_enhanced) > 0):
        for j in test_enhanced:
            if '=' in j or '_' in j or '&' in j or '/' in j or '\\' in j or '.' in j or '{' in j or '[' in j or '}' in j or ']' in j:
                return False
            else:
                return True
    else:
        return False

def remove_useless_spaces(text):
	return text.replace('\t','').replace('  ','').replace('\n','').replace('\r','').strip()

def remove_tags_hard(text):
    f = (re.compile('<script.*?</script>')).sub('',text)
    g = (re.compile('<style.*?</style>')).sub('',f)
    p = re.compile(r'<.*?>')
    return p.sub('', g)


def levenshtein(source, target):
    if len(source) < len(target):
        return levenshtein(target, source)
    if len(target) == 0:
        return len(source)
    source = np.array(tuple(source))
    target = np.array(tuple(target))
    previous_row = np.arange(target.size + 1)
    for s in source:
        current_row = previous_row + 1
        current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], target != s))
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)
        previous_row = current_row
    return previous_row[-1]


#Mets en format CSV pour excel
def open_file_crawling2(liste, path):
    f_linklist_read = open(path,"r")
    liste = f_linklist_read.readlines()
    return liste

#Mets en format CSV pour excel
def format_to_csv2(text, f):
	text = str(text).replace(';',',')
	text = str(text).replace('\n',' ')
	text = text + "\n"
	f.write(text)

#Fonction principale de scraping des articles
def scraping_comments(PATH_CRAWLING_DATA, ID_PRESTA) :

    #Récupération du crawling
    linkList = []
    linkList = open_file_crawling2(linkList, PATH_CRAWLING_DATA)
    f = open("./scraping/data/" + ID_PRESTA + "_sortie_scraping_comments.csv","w")
    for link in linkList:
        try:
            req = urllib.request.Request(link)
            response = urllib.request.urlopen(req)
            the_page = response.read()

            soup = BeautifulSoup(the_page, "lxml")
            liste = []

            for item in soup.findAll():
                sous_liste = []
                prec = ""
                for child in item.children:
                    try:
                        if(child.attrs != {}):
                            sous_liste.append(str(child.attrs))
                            sous_liste.append(str(child))
                            #prec = str(child.attrs)
                    except:
                        continue
                if(sous_liste != []):
                    liste.append(sous_liste)

            i = 0
            for elem in liste:
                if(len(elem) < 4):
                    del liste[i]
                i += 1


            score_list = []
            for elem in liste:
                i = 0
                score = 0
                while(i < len(elem) - 2):
                    score += score + levenshtein(str(elem[i][0]),str(elem[i+1][0]))
                    if(score > 999999999999):
                        score = 999999999999
                    i += 1
                score_list.append([score,elem])

            del score_list[0]
            maximum = 0
            index_max = 0
            i = 0
            for test_score in score_list:
                if(test_score[0] > maximum):
                    maximum = test_score[0]
                    index_max = i
                i += 1


            bli = score_list[index_max]
            print(bli[0])
            print(len(bli[1]))

            i = 0
            new_liste_comments = []
            for truc in bli[1]:
                text_comment = str(truc)
                if(text_comment != "" and i%2 != 0):

                    oup = BeautifulSoup(text_comment, "lxml")
                    hihi = oup.find_all('a')

                    [s.extract() for s in oup('a')]
                    liste_balise_comment = oup.find_all()

                    #Elimination des doublons de texte
                    l = 0
                    j = 1
                    k = 0
                    while (l < (len(liste_balise_comment) - j)):
                        k = l+1
                        while (k < (len(liste_balise_comment) - j)):
                            #print("########################\nTest : \n" + remove_tags_hard(remove_useless_spaces(str(liste_balise_comment[k]))) + "\n dans : \n" +remove_tags_hard(remove_useless_spaces(str(liste_balise_comment[l]))) )
                            if remove_tags_hard(remove_useless_spaces(str(liste_balise_comment[k]))) in remove_tags_hard(remove_useless_spaces(str(liste_balise_comment[l]))):
                                #print("SUPPRIME")
                                del liste_balise_comment[l]
                                j += 1
                                k -= 1
                                break
                            k += 1
                        l += 1

                    #Analyse d'un commentaire
                    k = 0
                    for item in liste_balise_comment:
                        words = []
                        item = str(item)
                        item = item.replace(">","> ")
                        item = item.replace("<"," <")
                        words = item.split(" ")
                        num_words = 0
                        num_wrong_words = 0
                        #test avec balises
                        for word in words:
                            if(isWord(word)):
                                num_words += 1
                            else:
                                num_wrong_words += 1
                        #enlevage des trucs pourris
                        if((num_words/3) < num_wrong_words):
                            #print(remove_tags_hard(remove_useless_spaces(str(liste_balise_comment[k]))))
                            del liste_balise_comment[k]
                            k -= 1
                            continue


                        #test sans balises
                        item = remove_tags_hard(remove_useless_spaces(item))
                        words = item.split(" ")
                        num_words = 0
                        num_wrong_words = 0
                        for word in words:
                            if(isWord(word)):
                                num_words += 1
                            else:
                                num_wrong_words += 1
                        #print(num_words)
                        #print(item)
                        #print(num_wrong_words)
                            # text_density = (num_words - (num_words % 10)) / (num_words/10)
                            # if(text_density == 0 or text_density < 10):
                            #     del liste_balise_comment[k]
                            #     k -= 1
                            #     continue
                            # else:
                            #     print(text_density)
                        k += 1


                    #text_fin = re.compile(r'<a.*?</a>').sub('',text_comment)
                    #print(str(hihi) + "\n")
                    n = 0

                    for item in liste_balise_comment:
                        if(len(remove_tags_hard(remove_useless_spaces(str(item)))) < 40):
                            del liste_balise_comment[n]
                            continue
                        else:
                            b = 0
                            for item2 in liste_balise_comment:
                                if(remove_tags_hard(remove_useless_spaces(str(item2))).replace(' ','') != ""):
                                    #print(remove_tags_hard(remove_useless_spaces(str(item2))).replace(' ',''))
                                    #print(remove_tags_hard(remove_useless_spaces(str(item))).replace(' ',''))
                                    #print("\n\n")
                                    if(remove_tags_hard(remove_useless_spaces(str(item2))).replace(' ','') in remove_tags_hard(remove_useless_spaces(str(item))).replace(' ','')):
                                        #print("OK")
                                        #del liste_balise_comment[n]
                                        continue
                                    else:
                                        new_liste_comments.append(remove_tags_hard(remove_useless_spaces(str(item))))
                                        break
                                        #print(remove_tags_hard(remove_useless_spaces(str(item2))).replace(' ',''))
                                        #print(remove_tags_hard(remove_useless_spaces(str(item))).replace(' ',''))
                                        #print("\n\n")


                                #if((remove_tags_hard(remove_useless_spaces(str(item2))) in remove_tags_hard(remove_useless_spaces(str(item)))) and (remove_tags_hard(remove_useless_spaces(str(item2))).replace(' ','') in remove_tags_hard(remove_useless_spaces(str(item))).replace(' ',''))):
                                    #print(remove_tags_hard(remove_useless_spaces(str(item2))))
                                    #print("suppr")
                                #    del liste_balise_comment[n]
                                #    continue
                                #b += 1
                        #print(remove_tags_hard(remove_useless_spaces(str(item))))
                        n += 1
                    #lalongueur = len(liste_balise_comment)


                    #if(lalongueur > 0):
                        #WTF ne pas laisser ça
                        #print(remove_tags_hard(remove_useless_spaces(str(liste_balise_comment)))+"\n\n\n")



                i += 1

            d = 0
            s = 1
            new_liste_comments.append("")
            while(d < len(new_liste_comments) - s):
                z = d + 1
                while(z < len(new_liste_comments) - s):
                    #print(str(z) + " < " + str(len(new_liste_comments) - s))
                    if(levenshtein(new_liste_comments[d],new_liste_comments[z]) < 80):
                        del new_liste_comments[d]
                        z -= 1
                        s += 1
                        #print(new_liste_comments[d] + "\n\n" + new_liste_comments[z] + "\n\n\n")
                    z += 1
                d += 1

            d = 0
            s = 1
            booleen = False
            while(d < len(new_liste_comments) - s):
                if(new_liste_comments[d+1] in new_liste_comments[d]):
                    #print("PROUT\n")
                    del new_liste_comments[d]
                    d -= 1
                    s += 1
                    booleen = True
                    continue
                else:
                    if(booleen):
                        booleen = False
                        del new_liste_comments[d]
                        del new_liste_comments[d+1]
                        s += 2
                d += 1
            result = ""
            for commentaire in new_liste_comments:
                if(len(commentaire) > 150):
                    result = result + " " + commentaire.replace("  ", "")

            format_to_csv(result, f)
        except:
            continue
