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
# TODO : Ajouter un module de simulation par rapport à une des variables d'entrée pour évaluer son changement et son impact sur l'apogée
# TODO : ajouter éventuellement la masse volumique du liquide en entrée pour évaluer l'utilisation d'autres liquide que l'eau
# TODO : Ajouter fonction d'affichage de la vitesse de sortie et du beta
# TODO : Pour l'affichage de la vitesse de sortie de vitesse ajouter la fonctionnalité en m/s en km/h ou en G

# Vb = bottle_volume
# Diametre_bouteille = d_bottle
# Diametre_sortie = d_out
# Masse_fusee_vide = m_empty_rocket
# Cx = Cx
# a = tilt_angle
# lr = length_rampe
# Po = initial_pressure
# Veo = initial_water_volume
# Section_bouteille = bottle_section
# Section_goulot = output_section

# Variables calculées
# volumes_air = air_volume
# pression_air = air_pressure
# vitesse = ejection_velocity
# temps = time
# poussée = dust
# masse_fusee = rocket_mass
# inclinaison_rampe = rampe_tilt
# vitesse_fusee = v_rocket
# resistance_air = air_resistance
# x = x
# y = y 
# acceleration = acceletation_y


# CONSTANTE
g = 9.81 # gravité
r = 998 # densité de l'eau en Kg/m^3
ra = 1.2 # densité de l'air en Kg/m^3
Patm = 101325 # pression atmosphérique

class WaterRocket : 

    def __init__(
        self, 
        bottle_volume = 2, 
        d_bottle = 8.9, 
        d_output = 0.9, 
        m_empty_rocket = 0.5, 
        Cx = 0.1, 
        tilt_angle = 89, 
        length_rampe = 22, 
        initial_pressure = 10, 
        initial_water_volume = 0.65) :


        # conversion des volumes en mètre cube
        self.bottle_volume = bottle_volume/1000
        self.initial_water_volume = initial_water_volume/1000
        # calcul des sections en m²
        self.bottle_section = (d_bottle**2)*np.pi/40000
        self.output_section = (d_output**2)*np.pi/40000
        # conversion en mètre
        self.length_rampe = length_rampe/100

        ## Calcul de la vitesse de sortie de rampe
        # Accélération suivant x
        self.ax = (initial_pressure*d_output-(m_empty_rocket+1000*initial_water_volume)*g*np.cos((90-tilt_angle)*np.pi/180))/(m_empty_rocket+1000*initial_water_volume)
        # Calcul du temps de sortie de rampe avec l'accélération x
        self.t_ramp_output = np.sqrt(2*length_rampe/self.ax)
        # calcul de la vitesse
        self.v_ramp_output = self.ax * self.t_ramp_output

        # Calcul du beta
        self.beta = r*(1 - ((self.output_section/self.bottle_section)**2))
        # Cx
        self.Cx = Cx

        # Initialisation des variables
        self.air_volume = [self.bottle_volume - self.initial_water_volume]
        self.air_pressure = list()
        self.ejection_velocity = list()
        self.time = list()
        self.dust = list()
        self.rocket_mass = list()
        self.rampe_tilt = [tilt_angle]
        self.v_rocket = [self.v_ramp_output]
        self.air_resistance = list()
        self.x = list()
        self.y = list()
        self.acceleration_y = [0]
