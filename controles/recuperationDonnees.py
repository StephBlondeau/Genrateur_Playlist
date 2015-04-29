
from Initialisations.connexion import mes_morceaux
from Initialisations.connexion import connexion
from Initialisations.argument import argumentsParser
import sqlalchemy
import random
import logging
from Initialisations.loggingConf import logging

'''
Created on 15 oct. 2014
@author: kitsune
'''

#Liste des arguments du programme
Attributs=[('g', "genre"),('ar', "artiste"),('sg', "sousgenre"),('alb', "album"),('t', "titre")]

def rechercheBase(Attributs, valeurRechercher, arg):
    '''
    On recherche dans la base les morceaux correspondant à un argument et a sa valeur
    @param Attributs: ensemble des arguments possibles de la ligne de commande (ex: ('g', "genre"),('ar', "artiste"))
    @param valeurRechercher:valeur saisie par l'utilisateur pour un argument (ex: Rock)
    @param arg: l'argument pour lequel on recherche la valeur (ex: g)
    @return: une liste de morceaux qui corresponde a un argument de la ligne de commande
    '''

    #Initialisation d'un compteur pour parcourir la liste des arguments
    i = 0
    trouve = False
    
    #Recherche dans la liste des arguments
    while (i < len(Attributs) and trouve == False):

        if Attributs[i][0] == arg:
            nameColumn = Attributs[i][1]

            #On essais de se connecter a la base et de recupere des donnees
            try :
                playList = list(connexion.execute(sqlalchemy.select([mes_morceaux]).where(getattr(mes_morceaux.c, nameColumn) == valeurRechercher)))
                trouve = True
                logging.info("Connexion à la base avec succés.")
            except Exception:
                logging.error("Le programme n'a pas pu acceder à la base de donnees")

        i += 1
    return playList

def verificationChoisi(selection, arg):
    '''
    Fonction qui permet de recherche dans la base de donnees si la valeur voulu d'un argument existe
    @param selection: valeur saisie par l'utilisateur pour un argument (ex: Rock)
    @param arg: l'argument pour lequel on recherche la valeur (ex: g)
    @return: un boolean qui permet de savoir si on a trouvé des morceaux ou non
    '''

    #On recherche dans la base
    select = rechercheBase(Attributs, selection, arg)

    #Si le resultat n'est pas vide
    if select != []:
        #On retourne true car il existe
        return True
    else :
        #On retourne false car il n'existe pas
        return False

#Module qui permet de recuperer une liste de morceaux selon les arguments de la commande
def recuperationDonnees(argumentsParser, existe):
    '''
    Fonction qui permet de recuperer une liste de morceaux selon les arguments de la ligne de commande
    @param argumentsParser: arguments saisie dans la ligne de commande
    @param existe: boolean qui permet de savoir s'il y a des arguments optionnels ou non
    @return une liste de liste qui contiendra l'ensemble des morceaux voulus pour chaque argument
    '''

    def filtrerListe(listeFinale, listeAFiltrer, quantiteEscomptee):
        '''
        Permet de choisir dans la liste de morceaux ceux qui va correspondre a la duree demande
        @param listeFinale: liste final correspondant à la quantite de morceaux voulus
        @param listeAFiltrer: la liste de morceaux de depart qui correspond à un argument
        @return: la listeFinale  
        '''

        #Si la quantite demander est superieur a 0
        if quantiteEscomptee > 0:
            #On range le dernier morceaux de la playlist dans la liste final et on la supprime de l'ensemble
            morceauChoisi = listeAFiltrer[0]

            #On remelange la liste a filtrer
            random.shuffle(listeAFiltrer)

            #On l'ajout a la playlist final
            listeFinale.append(morceauChoisi)

            #On decrément la quantite du morceaux ajoute au total de la quantiter voulue
            quantiteEscomptee -= morceauChoisi.duree
            #On rappel la fonction avec une diminution des parametres
            filtrerListe(listeFinale, listeAFiltrer, quantiteEscomptee)
        else:
            return listeFinale

    #On creer une liste de liste
    collectionListesFiltrees = list()

    #Initialisation d'un compteur
    i=0

    while (i < len(Attributs)):

        #On regarde s'il est rentree dans la commande
        if getattr(argumentsParser, Attributs[i][0]):
            #On parcourt l'ensemble d'un attribut
            for unArgument in getattr(argumentsParser, Attributs[i][0]):
                playList = rechercheBase(Attributs, unArgument[0], Attributs[i][0])
                #On applique la fonction de selection morceaux
                final = filtrerListe(collectionListesFiltrees, playList, unArgument[1] * argumentsParser.duree_playlist / 100 * 60)

                if (final is not None):
                    #on passe en parametre la quantite à garder à l'interieur de la sous playlist
                    collectionListesFiltrees.append(final)
        i+=1

    #S'il n'y a pas d'arguments optionnels
    if existe == False:
        try:
            #on recupere l'ensemble des morceaux de la base de donnees
            playList = list(connexion.execute(sqlalchemy.select([mes_morceaux])))
            #On applique la fonction de selection morceaux
            final = filtrerListe(collectionListesFiltrees, playList, argumentsParser.duree_playlist * 60)
        except Exception:
            logging.error("Le programme n'a pas pu recuperer une liste de morceaux")

        if (final is not None):
            #on passe en parametre la quantite à garder à l'interieur de la sous playlist
            collectionListesFiltrees.append(final)

    return collectionListesFiltrees
