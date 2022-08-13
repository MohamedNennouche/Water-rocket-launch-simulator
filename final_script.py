import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ! Conditions initiales de vols 
# TODO : Mettre sous forme d'Input et faire des vérifications sur le format
Vb = 2
Diametre_bouteille = 8.9
Diametre_sortie = 0.9
Masse_fusee_vide = 0.5 # Mo
Cx = 0.1
a = 89 # prévoir de le transformer en radians pour utiliser les fonctions trigo
lr = 22
Po = 10
Veo = 0.65

# ! Conversions
# Conversion des volumes en mètres cubes
Vb /= 1000
Veo /= 1000
# Conversion de la pression en pascal
Po *= 100000 # press
# Section de la bouteille en m^2
Section_bouteille = (Diametre_bouteille**2)*np.pi/40000
Section_goulot = (Diametre_sortie**2)*np.pi/40000
lr /= 100

# ! Paramètres environnementaux
g = 9.81 # gravité
r = 998 # densité de l'eau en Kg/m^3
ra = 1.2 # densité de l'air en Kg/m^3
Patm = 101325 # pression atmosphérique

# ! Constantes théoriques préalables
# Vitesse initiales
Ax = (Po*Section_goulot-(Masse_fusee_vide+1000*Veo)*g*np.cos((90-a)*np.pi/180))/(Masse_fusee_vide+1000*Veo) # Accélération suivant x
t = np.sqrt(2*lr/Ax)
Vx = Ax*t # Vitesse au lancement
Ax_g = Ax/g # en G
Vx_kmh = Vx * 3.6 # en km/h

# Beta
beta = r*(1 - ((Section_goulot/Section_bouteille)**2))

# ! Calcul des paramètres de vol
# 1. Volumes d'air
volumes_air = [Vb - Veo]
volumes_air_final = (Po + Patm)*(Vb-Veo)/Patm

# Premiere phase
for i in range(28) :
    volumes_air.append(volumes_air[i] + (Vb-volumes_air[0])/29)
# Fin premiere phase 
volumes_air.append(Vb)
volumes_air.append(Vb)
# Début deuxième phase
for i in range(30,48) :
    volumes_air.append(volumes_air[i] + (volumes_air_final-volumes_air[30])/19)
# Fin deuxième phase
volumes_air.append(volumes_air_final)

# 2. Pression de l'air
pression_air = list()
for i in range(len(volumes_air)) : 
    pression_air.append(((Po + Patm)*(Vb-Veo)/volumes_air[i])-Patm)

# 3. Vitesse d'éjection
# Phase 1
vitesse = list()
for i in range(30) :
    vitesse.append(np.sqrt(2*pression_air[i]/beta))
# Phase 2
for i in range(20) :
    vitesse.append(np.sqrt(2*pression_air[i+30]/ra))

# 4. Temps
# Phase 1
temps = list()
for i in range(30) : 
    temps.append(((2/3)*volumes_air[i]**1.5 - (2/3)*(Vb-Veo)**1.5)/(Section_goulot*np.sqrt(2*Po*(Vb-Veo)/beta)))
# Phase intermédiaire 1
temps.append((((2/3)*volumes_air[30]**1.5 - (2/3)*(Vb)**1.5)/(Section_goulot*np.sqrt(2*Po*(Vb-Veo)/beta)))+temps[29])
# Phase 2
for i in range(19) : 
    temps.append(temps[30+i]+((volumes_air[31+i]-volumes_air[30+i])/(Section_goulot*((vitesse[31+i]+vitesse[30+i])/2))))
# Phase intermédiaire 2
temps.append(temps[49])
temps.append(temps[50]+0.01)
# Phase 3
for i in range(547) :
    temps.append(temps[i + 51]+ 0.05)

# 5. Poussée
# Phase 1
poussee = list()
for i in range(30) : 
    poussee.append(r*Section_goulot*vitesse[i]**2) 
# Phase 2
for i in range(20) :
    poussee.append(ra*Section_goulot*vitesse[30+i]**2)

# 6. Masse de la fusée
# Phase 1
masse_fusee = list()
for i in range(30) :
    masse_fusee.append(Masse_fusee_vide+r*(Vb-volumes_air[i]))
# Phase 2
for i in range(569) :
    masse_fusee.append(Masse_fusee_vide)

# Egalisation des vecteurs
for i in range(549) :
    poussee.append(0)
    volumes_air.append(0)
    pression_air.append(0)
    vitesse.append(0)

# 7. Inclinaison + Vitesse de la fusée + Résistance de l'air
# Initialisation
inclinaison_rampe=[a]
vitesse_fusee = [Vx]
resistance_air = list()
# Phase 1
for i in range(29) :
    inclinaison_rampe.append(inclinaison_rampe[i]-np.arctan(g*np.cos(inclinaison_rampe[i]*np.pi/180)*(temps[i+1]-temps[i])/vitesse_fusee[i])*180/np.pi)

    resistance_air.append(0.5*ra*Section_bouteille*Cx*(vitesse_fusee[i]**2)) 
    
    vitesse_fusee.append(vitesse_fusee[i]+((poussee[i] - resistance_air[i])/(Masse_fusee_vide + r*(Vb-volumes_air[i+1])) - g*np.sin(inclinaison_rampe[i+1]*np.pi/180))*(temps[i+1]-temps[i]))

resistance_air.append(0.5*ra*Section_bouteille*Cx*(vitesse_fusee[29]**2))

# Phase intermédiaire
inclinaison_rampe.append(inclinaison_rampe[29]-np.arctan(g*np.cos(inclinaison_rampe[29]*np.pi/180)*(temps[30]-temps[29])/vitesse_fusee[29])*180/np.pi)
vitesse_fusee.append(vitesse_fusee[29]+(poussee[30]/Masse_fusee_vide)*(temps[30]-temps[29]))
resistance_air.append(0.5*ra*Section_bouteille*Cx*(vitesse_fusee[30]**2))

# Phase 2
for i in range(19) :
    inclinaison_rampe.append(inclinaison_rampe[i+30]-np.arctan(g*np.cos(inclinaison_rampe[i+30]*np.pi/180)*(temps[i+31]-temps[i+30])/vitesse_fusee[i+30])*180/np.pi)

    vitesse_fusee.append(np.abs(vitesse_fusee[i+30]+((poussee[i+31]-resistance_air[i+30])/Masse_fusee_vide-g*np.sin(inclinaison_rampe[i+31]*np.pi/180))*(temps[i+31]-temps[i+30])))

    resistance_air.append(0.5*ra*Section_bouteille*Cx*(vitesse_fusee[i+31]**2))

# Phase 3
for i in range(549) :
    if vitesse_fusee[-2] < vitesse_fusee[-1] :
        inclinaison_rampe.append(-np.abs(inclinaison_rampe[-1]-np.arctan((g*np.cos(inclinaison_rampe[-1]*np.pi/180)*(temps[49+i]-temps[48+i]))/vitesse_fusee[-1])*180/np.pi))
    else : 
        inclinaison_rampe.append(inclinaison_rampe[-1]-np.arctan((g*np.cos(inclinaison_rampe[-1]*np.pi/180)*(temps[49+i]-temps[48+i]))/vitesse_fusee[-1])*180/np.pi)
    
    vitesse_fusee.append(np.abs(vitesse_fusee[-1]+((poussee[49+i]-resistance_air[48+i])/Masse_fusee_vide -g*np.sin(inclinaison_rampe[-1]*np.pi/180))*(temps[49+i]-temps[48+i])))

    resistance_air.append(0.5*ra*Section_bouteille*Cx*(vitesse_fusee[-1]**2))


# 8. X(m) et Y(m)
x = [0]
y = [0]
for i in range(1,599) :
    x.append(x[i-1]+vitesse_fusee[i]*(temps[i]-temps[i-1])*np.cos(inclinaison_rampe[i]*np.pi/180))
    y.append(y[i-1]+vitesse_fusee[i]*(temps[i]-temps[i-1])*np.sin(inclinaison_rampe[i]*np.pi/180))

# 9. Accélération
acceleration = [0]
for i in range(1,599) :
    if i ==30 or i == 50 : 
        acceleration.append(acceleration[-1]) # mettre un doublon à la frontière
    else : 
        acceleration.append((vitesse_fusee[i]-vitesse_fusee[i-1])/(temps[i]-temps[i-1]))

# ! Tableau final
my_data = np.array([volumes_air,pression_air,temps,vitesse,poussee,masse_fusee,inclinaison_rampe,vitesse_fusee,resistance_air,x,y,acceleration]).T

colonnes = ["Volume d'air","Pression d'air","Temps","Vitesse","Poussée","Masse de la fusée","Inclinaison","Vitesse de la fusée","Résistance de l'air","x(t)","y(t)","Accélération"]

tableau_complet = pd.DataFrame(my_data, columns=colonnes)