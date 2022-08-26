__author__ = "Mohamed Nennouche"
__copyright__ = "Copyright 20XX, WaterRocketPy Team"
__license__ = "MIT"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os 
import shutil

sns.set_theme(style='darkgrid')

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image

# TODO : réfléchir sur la possibilité de mettre 2 fichiers séparés : calcul pour la fusée / graphiques et la génération des PDF 
# TODO : Mettre des fonctions pour l'affichage de chaque grandeur
# TODO : Fonction qui affiche tout
# TODO : Définir des noms cohérents aux variables 
# TODO : Voir comment générer automatiquement les commentaires pour définir les fonctions

class WaterRocket : 
    def __init__(self, Vb = 2, Diametre_bouteille = 8.9, Diametre_sortie = 0.9, Masse_fusee_vide = 0.5, Cx = 0.1, a = 89, lr = 22, Po = 10, Veo = 0.65) :
        
        return 0