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
        self.x = [0]
        self.y = [0]
        self.acceleration_y = [0]

    def calc_air_volume(self) :
        """Function calculating the air volume variations in the cylinder from its launch

        Args: 
            In order to calculate the volume of air, the following quantities are required:
        - The initial pressure (self.initial_pressure)
        - The bottle volume (self.bottle_volume)
        - The initial water volume (self.initial_water_volume)
        - The atmospheric pressure (self.p_atm)

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

        Args: 
            In order to calculate the internal pressure, the following quantities are required:
        - The air volume (self.air_volume)
        - The initial pressure (self.initial_pressure)
        - The bottle volume (self.bottle_volume)
        - The initial water volume (self.initial_water_volume)
        - The atmospheric pressure (self.p_atm)

        Returns:
            self.air_pressure (list):Returns the list of elements of the pressure completely filled (initially empty)
        """
        if len(self.air_pressure) == 0 :
            if len(self.air_volume) == 1 : 
                self.calc_air_volume()

            for i in range(50) : 
                self.air_pressure.append(((self.initial_pressure + self.p_atm)*(self.bottle_volume-self.initial_water_volume)/self.air_volume[i])-self.p_atm)
            for i in range(549) :
                self.air_pressure.append(0)
        return self.air_pressure
    
    def calc_ejection_velocity(self):
        """Function calculating the ejection velocity variation in two phases : water ejection and air ejection

        Args: 
            In order to calculate the ejection velocity, the following quantities are required:
            - The air pressure (self.air_pressure)
            - The beta depending on water density used (self.beta, self.r)
            - The air density (self.ra)

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
    
    def calc_time(self):
        """Function calculating the rocket launching time

        Args:
            In order to calculate the flight time, the following quantities are required:
            - The air volume (self.air_volume)
            - The ejection velocity (self.ejection_velocity)
            - The bottle volume (self.bottle_volume)
            - The initial water volume (self.initial_water_volume)
            - The output section (self.output_section)
            - The initial pressure (self.initial_pressure)
            - The beta (self.beta)

        Returns:
            self.time (list):  Returns the list of elements of time completely filled (initially empty)
        """

        if len(self.time) == 0 : 
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

        Args:
            In order to calculate the dust during the flight, the following quantities are required:
            - The ejection velocity (self.ejection_velocity)
            - The water density (self.r)
            - The air density (self.ra)
            - The output section (self.output_section)

        Returns:
            self.dust (list): Returns the list of elements of dust completely filled (initially empty)
        """
        if len(self.dust) == 0 : 
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

        Args:
            In order to calculate the rocket mass during the flight, the following quantities are required:
            - The air volume (self.air_volume)
            - The empty rocket mass (self.m_empty_rocket)
            - The water density (self.r)
            - The bottle volume (self.bottle_volume)
        
        Returns:
            self.rocket_mass (list): return the list containing the variation of the rocket mass
        """
        if len(self.rocket_mass) == 0 : 
            if len(self.air_volume) == 1 : 
                self.calc_air_volume()
            # First phase
            for i in range(30) :
                self.rocket_mass.append(self.m_empty_rocket+self.r*(self.bottle_volume-self.air_volume[i]))
            # Second phase
            for i in range(569) :
                self.rocket_mass.append(self.m_empty_rocket)
        return self.rocket_mass
    
    def calc_tilt_velocity_res(self) :
        """Function calculating simultaneously the rampe tilt, the rocket velocity and the air resistance 

        Args:
            In order to calculate the rampe tilt, the rocket velocity and the air resistance during the flight, the following quantities are required:
            - The flight time (self.time)
            - The air volume (self.air_volume)
            - The dust (self.dust)
            - The acceleration of gravity (self.g)
            - The water density (self.r)
            - The air density (self.ra)
            - The bottle section (self.bottle_section)
            - The aerodynamic coefficient (self.Cx)
            - The empty rocket mass (self.m_empty_rocket)
            - The bottle volume (self.bottle_volume)

        Returns:
            - self.rampe_tilt (list): returns the list containing the variation of the rampe tilt
            - self.v_rocket (list): return the list containing the variation of the rocket velocity
            - self.air_resistance (list): return the list containing the variation of the air resistance
        """
        if len(self.rampe_tilt) == 1 and len(self.v_rocket) == 1 and len(self.air_resistance) == 0 :
            if len(self.time) == 0 :
                self.calc_time()
            if len(self.air_volume) == 1 : 
                self.calc_air_volume()
            if len(self.dust) == 0 :
                self.calc_dust()
            
            # First phase
            for i in range(29) :
                self.rampe_tilt.append(self.rampe_tilt[i]-np.arctan(self.g*np.cos(self.rampe_tilt[i]*np.pi/180)*(self.time[i+1]-self.time[i])/self.v_rocket[i])*180/np.pi)

                self.air_resistance.append(0.5*self.ra*self.bottle_section*self.Cx*(self.v_rocket[i]**2)) 
            
                self.v_rocket.append(self.v_rocket[i]+((self.dust[i] - self.air_resistance[i])/(self.m_empty_rocket + self.r*(self.bottle_volume-self.air_volume[i+1])) - self.g*np.sin(self.rampe_tilt[i+1]*np.pi/180))*(self.time[i+1]-self.time[i]))
            
            self.air_resistance.append(0.5*self.ra*self.bottle_section*self.Cx*(self.v_rocket[29]**2))

            # Intermediate phase
            self.rampe_tilt.append(self.rampe_tilt[29]-np.arctan(self.g*np.cos(self.rampe_tilt[29]*np.pi/180)*(self.time[30]-self.time[29])/self.v_rocket[29])*180/np.pi)

            self.v_rocket.append(self.v_rocket[29]+(self.dust[30]/self.m_empty_rocket)*(self.time[30]-self.time[29]))

            self.air_resistance.append(0.5*self.ra*self.bottle_section*self.Cx*(self.v_rocket[30]**2))

            # Second phase
            for i in range(19) :
                self.rampe_tilt.append(self.rampe_tilt[i+30]-np.arctan(self.g*np.cos(self.rampe_tilt[i+30]*np.pi/180)*(self.time[i+31]-self.time[i+30])/self.v_rocket[i+30])*180/np.pi)

                self.v_rocket.append(np.abs(self.v_rocket[i+30]+((self.dust[i+31]-self.air_resistance[i+30])/self.m_empty_rocket-self.g*np.sin(self.rampe_tilt[i+31]*np.pi/180))*(self.time[i+31]-self.time[i+30])))

                self.air_resistance.append(0.5*self.ra*self.bottle_section*self.Cx*(self.v_rocket[i+31]**2))
            
            # Third phase
            for i in range(549) :
                if self.v_rocket[-2] < self.v_rocket[-1] :
                    self.rampe_tilt.append(-np.abs(self.rampe_tilt[-1]-np.arctan((self.g*np.cos(self.rampe_tilt[-1]*np.pi/180)*(self.time[49+i]-self.time[48+i]))/self.v_rocket[-1])*180/np.pi))
                else :
                    self.rampe_tilt.append(self.rampe_tilt[-1]-np.arctan((self.g*np.cos(self.rampe_tilt[-1]*np.pi/180)*(self.time[49+i]-self.time[48+i]))/self.v_rocket[-1])*180/np.pi)
            
                self.v_rocket.append(np.abs(self.v_rocket[-1]+((self.dust[49+i]-self.air_resistance[48+i])/self.m_empty_rocket -self.g*np.sin(self.rampe_tilt[-1]*np.pi/180))*(self.time[49+i]-self.time[48+i])))

                self.air_resistance.append(0.5*self.ra*self.bottle_section*self.Cx*(self.v_rocket[-1]**2))
            
        return self.rampe_tilt,self.v_rocket,self.air_resistance

    def calc_x_y(self) :
        """Function calculating simultaneously the x and y position of the rocket

        Args:
            In order to calculate the x and y position of the rocket, the following quantities are required:
            - The rocket velocity (self.v_rocket)
            - The rampe tilt (self.rampe_tilt)
            - The time of the flight (self.time)

        Returns:
            - self.x (list): returns the list containing the x position of the rocket
            - self.y (list): return the list containing the y position of the rocket
        """

        if len(self.x) == 1 and len(self.y) == 1 :
            if len(self.v_rocket) == 1 and len(self.rampe_tilt) == 1 :
                self.calc_tilt_velocity_res()
            if len(self.time) == 0 :
                self.calc_time()
            
            for i in range(1,599) :
                self.x.append(self.x[i-1]+self.v_rocket[i]*(self.time[i]-self.time[i-1])*np.cos(self.rampe_tilt[i]*np.pi/180))
                self.y.append(self.y[i-1]+self.v_rocket[i]*(self.time[i]-self.time[i-1])*np.sin(self.rampe_tilt[i]*np.pi/180))
        return self.x,self.y
    
    def calc_accel(self) :
        """Function calculating the rocket acceleration (following y)

        Args:
            In order to calculate the rocket acceleration, the following quantities are required:
            - The rocket velocity (self.v_rocket)
            - The time of the flight (self.time)

        Returns:
            - self.acceleration_y (list): returns the list containing the rocket acceleration following the y axis
        """
        if len(self.acceleration_y) == 1 :
            if len(self.v_rocket) == 1 :
                self.calc_tilt_velocity_res()
            if len(self.time) == 0 :
                self.calc_time()
            for i in range(1,599) :
                if i ==30 or i == 50 : 
                    self.acceleration_y.append(self.acceleration_y[-1]) # mettre un doublon à la frontière
                else : 
                    self.acceleration_y.append((self.v_rocket[i]-self.v_rocket[i-1])/(self.time[i]-self.time[i-1]))
        return self.acceleration_y
    
    def calc_all_caracteristics(self) :
        """Function calculating all caracteristics of the rocket flight

        Returns: self.air_volume, self.air_pressure, self.ejection_velocity, self.time, self.dust, self.rocket_mass, self.rampe_tilt, self.v_rocket, self.air_resistance, self.x, self.y, self.acceleration_y
        """
        if len(self.air_volume) == 1 :
            self.calc_air_volume()
        if len(self.air_pressure) == 0 :
            self.calc_pressur()
        if len(self.ejection_velocity) == 0 : 
            self.calc_ejection_velocity()
        if len(self.time) == 0 : 
            self.calc_time()
        if len(self.dust) == 0 : 
            self.calc_dust()
        if len(self.rocket_mass) == 0 : 
            self.calc_mass()
        if len(self.rampe_tilt) == 1 and len(self.v_rocket) == 1 and len(self.air_resistance) == 0 :
            self.calc_tilt_velocity_res()
        if len(self.x) == 1 and len(self.y) == 1 :
            self.calc_x_y()
        if len(self.acceleration_y) == 1 :
            self.calc_accel()
        
        return self.air_volume, self.air_pressure, self.ejection_velocity, self.time, self.dust, self.rocket_mass, self.rampe_tilt, self.v_rocket, self.air_resistance, self.x, self.y, self.acceleration_y