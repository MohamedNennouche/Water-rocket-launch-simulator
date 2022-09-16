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
# TODO : Revoir la structure des fonctions pour éviter les dépendances circulaires et les erreurs d'index (peut être n'avoir qu'une seule et même fonction qui calcule toutes les variables)
# TODO : ajouter une doc pour toutes les fonctions et ajouter des variables d'entrées plus expressive (a : int) 

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
        bottle_volume:float= 2, 
        d_bottle:float= 8.9, 
        d_output:float= 0.9, 
        m_empty_rocket:float= 0.5, 
        Cx:float= 0.1, 
        tilt_angle:float= 89, 
        length_rampe:float= 22, 
        initial_pressure:float= 10, 
        initial_water_volume:float= 0.65,
        g:float=9.81,
        r:float=998,
        ra:float=1.2,
        Patm:float=101325) :
        """Constructor of the WaterRocket class, it takes as physical parameters of the bottle as well as environmental to initialize all the variables that we can calculate

        Args:
            - bottle_volume (float, optional): Volume of the bottle used for the shooting (in liter). Defaults to 2.
            - d_bottle (float, optional): diameter of the bottle (in cm). Defaults to 8.9.
            - d_output (float, optional): diameter of the output (in cm). Defaults to 0.9.
            - m_empty_rocket (float, optional): Mass of the empty rocket (in Kg). Defaults to 0.5.
            - Cx (float, optional): Aerodynamic coefficient of the rocket calculated from its geometry. Defaults to 0.1.
            - tilt_angle (float, optional): Angle of inclination of the shooting ramp (in degrees). Defaults to 89.
            - length_rampe (float, optional): Length of the shooting ramp (in cm). Defaults to 22.
            - initial_pressure (float, optional): Initial bottle pressure (in bar). Defaults to 10.
            - initial_water_volume (float, optional): Initial water volume inside the bottle (in liter). Defaults to 0.65.
            - g (float, optional): Gravity acceleration (in m/s²). Defaults to 9.81.
            - r (float, optional): Water density (in Kg/m^3). Defaults to 998.
            - ra (float, optional): Air density (in Kg/m^3). Defaults to 1.2.
            - Patm (float, optional): Atmospheric pressure (in Pascal). Defaults to 101325.
        """

        #Initialization of constants
        self.g = g
        self.r = r
        self.ra = ra
        self.p_atm = Patm
        self.m_empty_rocket = m_empty_rocket
        # conversion of volumes into cubic meters
        self.bottle_volume = bottle_volume/1000
        self.initial_water_volume = initial_water_volume/1000
        # calculation of the sections in m².
        self.bottle_section = (d_bottle**2)*np.pi/40000
        self.output_section = (d_output**2)*np.pi/40000
        # conversion to meters
        self.length_rampe = length_rampe/100
        # conversion to pascal
        self.initial_pressure= initial_pressure*100000

        ## Calculation of the ramp output speed
        # Acceleration according to x
        self.ax = (initial_pressure*d_output-(m_empty_rocket+1000*initial_water_volume)*g*np.cos((90-tilt_angle)*np.pi/180))/(m_empty_rocket+1000*initial_water_volume)
        # Calculation of the ramp exit time with the acceleration x
        self.t_ramp_output = np.sqrt(2*length_rampe/self.ax)
        # Calculation of the velocity
        self.v_ramp_output = self.ax * self.t_ramp_output

        # Calculation of beta
        self.beta = r*(1 - ((self.output_section/self.bottle_section)**2))
        # Cx
        self.Cx = Cx

        # Variable initialization
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

    def calc_air_volume(self) :
        """Function calculating the air volume variations in the cylinder from its launch

        Returns:
            self.air_volume (list): Returns the list of elements of the air volume completely filled (initially containing only the first element)
        """
        if len(self.air_volume) == 1 :
            final_air_volume = (self.initial_pressure + self.p_atm)*(self.bottle_volume-self.initial_water_volume)/self.p_atm
            # First phase
            for i in range(28) :
                self.air_volume.append(self.air_volume[i] + (self.bottle_volume-self.air_volume[0])/29)
            self.air_volume+[self.bottle_volume,self.bottle_volume]
            # Second phase
            for i in range(30,48) :
                self.air_volume.append(self.air_volume[i] + (final_air_volume-self.air_volume[30])/19)
            # Final phase
            self.air_volume.append(final_air_volume)
            for i in range(549) :
                self.air_volume.append(0)
        return self.air_volume
    
    def calc_pressure(self):
        """Function calculating the relative pressure variation inside the bottle

        Returns:
            self.air_pressure (list):Returns the list of elements of the pressure completely filled (initially empty)
        """
        if len(self.air_volume) == 1 : 
            self.calc_air_volume()
        for i in range(50) : 
            self.air_pressure.append(((self.initial_pressure + self.p_atm)*(self.bottle_volume-self.initial_water_volume)/self.air_volume[i])-self.p_atm)
        for i in range(549) :
            self.air_pressure.append(0)
        return self.air_pressure
    
    def calc_ejection_velocity(self):
        """Function calculating the ejection velocity variation in two phases : water ejection and air ejection

        Returns:
            self.ejection_velocity (list): Returns the list of elements of the ejection velocity completely filled (initially empty)
        """
        if len(self.ejection_velocity) == 0 : 
            if len(self.air_pressure) == 0 :
                self.calc_pressure()
            # First phase : water
            for i in range(30) :
                self.ejection_velocity.append(np.sqrt(2*self.air_pressure[i]/self.beta))
            # Second phase : air
            for i in range(20) :
                self.ejection_velocity.append(np.sqrt(2*self.air_pressure[i+30]/self.ra))
            for i in range(549) :
                self.ejection_velocity.append(0)
        return self.ejection_velocity
    
    def calcTemps(self):
        """Function calculating the rocket launching time

        Returns:
            self.time (list):  Returns the list of elements of time completely filled (initially empty)
        """
        if len(self.air_volume) == 1 : 
            self.calc_air_volume()
        if len(self.ejection_velocity) == 0 : 
            self.calc_ejection_velocity()

        # First phase
        for i in range(30) : 
            self.time.append(((2/3)*self.air_volume[i]**1.5 - (2/3)*(self.bottle_volume-self.initial_water_volume)**1.5)/(self.output_section*np.sqrt(2*self.initial_pressure*(self.bottle_volume-self.initial_water_volume)/self.beta)))
        # Intermediate phase 1
        self.time.append((((2/3)*self.air_volume[30]**1.5 - (2/3)*(self.bottle_volume)**1.5)/(self.output_section*np.sqrt(2*self.initial_pressure*(self.bottle_volume-self.initial_water_volume)/self.beta)))+self.time[29])
        # Second phase
        for i in range(19) : 
            self.time.append(self.time[30+i]+((self.air_volume[31+i]-self.air_volume[30+i])/(self.output_section*((self.ejection_velocity[31+i]+self.ejection_velocity[30+i])/2))))
        # Intermediate phase 2
        self.time.append(self.time[49])
        self.time.append(self.time[50]+0.01)
        # Third phase
        for i in range(547) :
            self.time.append(self.time[i + 51]+ 0.05)
        return self.time
        
    def calc_dust(self) :
        """Function calculating the rocket dust (in water phase and air phase)

        Returns:
            self.dust (list): Returns the list of elements of dust completely filled (initially empty)
        """
        if len(self.ejection_velocity) == 0 : 
            self.calc_ejection_velocity()
        # First phase : water phase
        for i in range(30) : 
            self.dust.append(self.r*self.output_section*self.ejection_velocity[i]**2) 
        # Second phase : air phase
        for i in range(20) :
            self.dust.append(self.ra*self.output_section*self.ejection_velocity[30+i]**2)
        for i in range(549) :
            self.dust.append(0)
        return self.dust

    def calc_mass(self):
        """Function calculating the rocket mass variation during the flight

        Returns:
            self.rocket_mass (list): return the list containing the variation of the rocket mass
        """
        if len(self.air_volume) == 1 : 
            self.calc_air_volume()
        # First phase
        for i in range(30) :
            self.rocket_mass.append(self.m_empty_rocket+self.r*(self.bottle_volume-self.air_volume[i]))
        # Second phase
        for i in range(569) :
            self.rocket_mass.append(self.m_empty_rocket)
        return self.rocket_mass