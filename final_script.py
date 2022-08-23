import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme(style='darkgrid')

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image

# ! Conditions initiales de vols 
# TODO : Mettre sous forme d'Input et faire des vérifications sur le format
# TODO : Mettre en place une librairie 
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

# ! Enregistrement sous format CSV
# mettre ou sauvegarder le fichier sous forme d'input
calcul_reel = tableau_complet[tableau_complet["y(t)"]>=0]
calcul_reel.to_csv("simulateur_tir.csv",index=False)

# ! Graphiques
# Trajectoire
## Avec moments forts 
plt.figure(figsize=(15,6))
plt.plot(calcul_reel["x(t)"],calcul_reel["y(t)"], label="Trajectoire de tir")
plt.scatter(calcul_reel["x(t)"].loc[calcul_reel["y(t)"].argmax()],calcul_reel["y(t)"].loc[calcul_reel["y(t)"].argmax()], label='Apogée', marker="x", s=90, color=(0.25,0.25,0.5))
plt.scatter(calcul_reel["x(t)"].loc[calcul_reel["Vitesse de la fusée"].argmax()],calcul_reel["y(t)"].loc[calcul_reel["Vitesse de la fusée"].argmax()], label='Vitesse max', marker="+", s=90, color=(0.1,0.5,0.1))
plt.scatter(calcul_reel["x(t)"].loc[calcul_reel["Poussée"].argmax()],calcul_reel["y(t)"].loc[calcul_reel["Poussée"].argmax()], label='Poussée max', marker="x", s=90, color=(0.9,0.4,0.5))
plt.scatter(calcul_reel["x(t)"].loc[calcul_reel["Accélération"].argmax()],calcul_reel["y(t)"].loc[calcul_reel["Accélération"].argmax()], label='Accélération max', marker="x", s=90, color=(0.3,0.4,0.5))

plt.scatter(calcul_reel["x(t)"].loc[calcul_reel["Résistance de l'air"].argmax()],calcul_reel["y(t)"].loc[calcul_reel["Résistance de l'air"].argmax()], label="Résistance de l'air max", marker="2", s=90, color=(0.1,0.1,0.1))
plt.legend()
font = {'family': 'sans-serif',
        'color':  'black',
        'weight': 'bold',
        'size': 16,
        }
plt.title("Trajectoire de vol avec les moments forts",fontdict=font)
plt.xlabel("Distance (m)",fontsize=14)
plt.ylabel("Hauteur (m)", fontsize=14)
plt.savefig("./img/fig1.png",bbox_inches='tight')
## En décomposant
plt.figure(figsize=(15,6))
plt.plot(calcul_reel["x(t)"].loc[:29],calcul_reel["y(t)"].loc[:29], label="Poussée de l'eau", marker="+", alpha=0.7)
plt.plot(calcul_reel["x(t)"].loc[30:49],calcul_reel["y(t)"].loc[30:49], label="Poussée de l'air", marker="x", alpha=0.7)
plt.plot(calcul_reel["x(t)"].loc[50:],calcul_reel["y(t)"].loc[50:], label="Poussée résiduelle", marker="o", alpha=0.7)
plt.legend()
plt.title("Trajectoire de vol décomposée", fontdict=font)
plt.xlabel("Distance (m)",fontsize=14)
plt.ylabel("Hauteur (m)", fontsize=14)
plt.savefig("./img/fig2.png", bbox_inches='tight')
# Vitesse de la fusée
## En fonction de x 
plt.figure(figsize=(17,6))
plt.plot(calcul_reel["x(t)"],calcul_reel["Vitesse de la fusée"], label="Evolution de la vitesse de vol")
plt.scatter(calcul_reel["x(t)"].loc[119],calcul_reel["Vitesse de la fusée"].loc[119], marker="+", label="Apogée", c="r", s=150)
x_cast = "{:.2f}".format(calcul_reel["x(t)"].loc[calcul_reel["y(t)"].argmax()])
y_cast = "{:.2f}".format(calcul_reel["y(t)"].loc[calcul_reel["y(t)"].argmax()])
plt.text(calcul_reel["x(t)"].loc[119]+0.5,calcul_reel["Vitesse de la fusée"].loc[119], "x = {}\ny = {}".format(x_cast,y_cast))
plt.legend()
plt.title("Vitesse de la fusée en fonction de x", fontdict=font)
plt.xlabel("Distance (m)",fontsize=14)
plt.ylabel("Vitesse (m/s)", fontsize=14)
plt.savefig("./img/fig3.png", bbox_inches='tight')
## En fonction du temps 
plt.figure(figsize=(17,6))
plt.plot(calcul_reel["Temps"],calcul_reel["Vitesse de la fusée"], label="Evolution de la vitesse de vol")
plt.scatter(calcul_reel["Temps"].loc[119],calcul_reel["Vitesse de la fusée"].loc[119], marker="+", label="Apogée", c="r", s=150)
x_cast = "{:.2f}".format(calcul_reel["x(t)"].loc[calcul_reel["y(t)"].argmax()])
y_cast = "{:.2f}".format(calcul_reel["y(t)"].loc[calcul_reel["y(t)"].argmax()])
plt.text(calcul_reel["Temps"].loc[119]+0.5,calcul_reel["Vitesse de la fusée"].loc[119], "x = {}\ny = {}".format(x_cast,y_cast))
plt.legend()
plt.title("Vitesse de la fusée en fonction du temps", fontdict=font)
plt.xlabel("Temps (s)",fontsize=14)
plt.ylabel("Vitesse (m/s)", fontsize=14)
plt.savefig("./img/fig4.png", bbox_inches='tight')
# Poussée
## Sans décomposition
plt.figure(figsize=(16,6))
plt.plot(calcul_reel["Temps"],calcul_reel["Poussée"], marker = 'x', label="Poussée")
plt.title("Evolution de la poussée en fonction du temps", fontdict=font)
plt.xlabel("Temps (s)",fontsize=14)
plt.ylabel("Poussée (N)", fontsize=14)
plt.legend(fontsize=14)
plt.xlim(0,1.3)
plt.savefig("./img/fig5.png",bbox_inches='tight')
## Avec décomposition
plt.figure(figsize=(16,6))
plt.plot(calcul_reel["Temps"].iloc[:30],calcul_reel["Poussée"].iloc[:30], marker = 'x', label="Poussée de l'eau")
plt.plot(calcul_reel["Temps"].iloc[30:],calcul_reel["Poussée"].iloc[30:], marker = 'x', label="Poussée de l'air")
plt.title("Evolution de la poussée en fonction du temps décomposée", fontdict=font)
plt.xlabel("Temps (s)",fontsize=14)
plt.ylabel("Poussée (N)", fontsize=14)
plt.legend(fontsize=14)
plt.xlim(0,1.3)
plt.savefig("./img/fig6.png",bbox_inches='tight')
# Vitesse d'éjection
## Eau
plt.figure(figsize=(17,6))
plt.plot(temps[:30], vitesse[0:30],marker='x')
plt.title("Evolution de la vitesse d'éjection de l'eau", fontdict=font)
plt.xlabel("Temps (s)", fontsize=14)
plt.ylabel("Vitesse d'éjection (m/s)", fontsize=14)
plt.savefig("./img/fig7.png", bbox_inches='tight')
## Air
plt.figure(figsize=(17,6))
plt.plot(temps[30:], vitesse[30:],marker='x')
plt.xlim(0.25,1.5)
plt.title("Evolution de la vitesse d'éjection de l'air", fontdict=font)
plt.xlabel("Temps (s)", fontsize=14)
plt.ylabel("Vitesse d'éjection (m/s)", fontsize=14)
plt.savefig("./img/fig8.png", bbox_inches='tight')
# Tableau des moments forts 
data =  [
            [         'Valeur'],
            [ 'Vitesse maximale (m/s)', calcul_reel["Vitesse de la fusée"].max()],
            [ 'Vitesse maximale (km/h)', calcul_reel["Vitesse de la fusée"].max()*3.6],
            ['Poussée maximale (N)', calcul_reel["Poussée"].max()],
            ['Accélération maximale (m/s²)', calcul_reel["Accélération"].max()],
            ["Résistance de l'air maximale (N)", calcul_reel["Résistance de l'air"].max()],
            ['Hauteur maximale (m)', calcul_reel["y(t)"].max()],
            ['Etendue maximale (m)', calcul_reel["x(t)"].max()],
            ["Durée de l'éjection de l'eau (s)", calcul_reel["Temps"].loc[29]],
            ["Durée de l'éjection de l'air (s)", calcul_reel["Temps"].loc[49]-calcul_reel["Temps"].loc[29]],
            ["Durée de vol total (s)", calcul_reel["Temps"].loc[206]]
        ]
# Pop the headers from the data array
column_headers = data.pop(0)
row_headers = [x.pop(0) for x in data]

cell_text = []
for row in data:
    cell_text.append([f'{x:3.4f}' for x in row])

rcolors = plt.cm.BuPu(np.full(len(row_headers), 0.1))
ccolors = plt.cm.BuPu(np.full(len(column_headers), 0.1))

plt.figure()
the_table = plt.table(cellText=cell_text,
                      rowLabels=row_headers,
                      rowColours=rcolors,
                      cellLoc='center',
                      rowLoc='right',
                      colLoc='center',
                      colColours=ccolors,
                      colLabels=column_headers,
                      loc='center')
the_table.scale(1, 1.5)
plt.box(on=None)

ax = plt.gca()
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

fig = plt.gcf()
plt.savefig('table_highlights.png',
            bbox_inches='tight',
            dpi=150
            )
# ! Génération du PDF
# TODO : Ajouter la partie théorique au rapport PDF ainsi que les variables d'entrées
## Styles 
def create_style(styleName, fontName='Helvetica', fontSize=12, parent='Normal', alignment='right', spaceAfter=10) :

    alignement_dict = {"left" : 0, "center" : 1, "right" : 2}
    style = getSampleStyleSheet()
    return ParagraphStyle(styleName,
                          fontName=fontName,
                          fontSize=fontSize,
                          parent=style[parent],
                          alignment=alignement_dict[alignment],
                          spaceAfter=spaceAfter
    )

myTitle = create_style('myheading', fontName='Helvetica-Bold', fontSize=32, parent='Heading1', alignment='center',spaceAfter=24)
mySubtitle = create_style('mysubheading', fontName='Helvetica-Bold', fontSize=20, parent='Heading2', alignment='left',spaceAfter=16)
mySubSubtitle = create_style('mysubsubheading', fontName='Helvetica-Bold', fontSize=14, parent='Heading3', alignment='left',spaceAfter=12)
myPara = create_style('mypara', fontName='Helvetica', fontSize=12, parent='Normal', alignment='left',spaceAfter=10)

## Template
doc = SimpleDocTemplate(
        "report_draft.pdf",
        pagesize=A4,
        rightMargin=62, leftMargin=62,
        topMargin=72, bottomMargin=34,
        title="Rapport",author="Mohamed"
        )
flowable = list()
reportName = Paragraph("<u>Rapport de vol</u>", myTitle)
spacer = Spacer(1, 0.25*inch)
spacer_item = Spacer(1, 0.125*inch)
moment = Paragraph("Moments forts", mySubtitle)
monimage = Image("table_highlights.png", width=350, height=200)
commentary = Paragraph("Commentaires", mySubtitle)

item1 = Paragraph("La vitesse maximale est de <b>{:3.4f} m/s</b> et correspond aux coordonnées :<br /><b>&nbsp;&nbsp;&nbsp;&nbsp;x = {:3.4f} m<br />&nbsp;&nbsp;&nbsp;&nbsp;y = {:3.4f} m</b>".format(calcul_reel["Vitesse de la fusée"].max(),calcul_reel["x(t)"].loc[calcul_reel["Vitesse de la fusée"].argmax()],calcul_reel["y(t)"].loc[calcul_reel["Vitesse de la fusée"].argmax()]), bulletText='-')

item2 = Paragraph("La poussée maximale est <b>{:3.4f}  N</b> et correspond aux décollage :<br /><b>&nbsp;&nbsp;&nbsp;&nbsp;x = {:3.4f} m<br />&nbsp;&nbsp;&nbsp;&nbsp;y = {:3.4f} m</b>".format(calcul_reel["Poussée"].max(),calcul_reel["x(t)"].loc[calcul_reel["Poussée"].argmax()],calcul_reel["y(t)"].loc[calcul_reel["Poussée"].argmax()]), bulletText='-')

item3 = Paragraph("L'accélération maximale est <b>{:3.4f} m/s² </b> et correspond aux coordonnées :<br /><b>&nbsp;&nbsp;&nbsp;&nbsp;x = {:3.4f} m<br />&nbsp;&nbsp;&nbsp;&nbsp;y = {:3.4f} m</b>".format(calcul_reel["Accélération"].max(),calcul_reel["x(t)"].loc[calcul_reel["Accélération"].argmax()],calcul_reel["y(t)"].loc[calcul_reel["Accélération"].argmax()]), bulletText='-')

item4 = Paragraph("Les coordonnées dors de la fin de l'éjection de l'eau :<br /><b>&nbsp;&nbsp;&nbsp;&nbsp;x = {:3.4f} m<br />&nbsp;&nbsp;&nbsp;&nbsp;y = {:3.4f} m</b>".format(calcul_reel["x(t)"].loc[29],calcul_reel["y(t)"].loc[29]), bulletText='-')

item5 = Paragraph("Les coordonnées dors de la fin de l'éjection de l'air :<br /><b>&nbsp;&nbsp;&nbsp;&nbsp;x = {:3.4f} m<br />&nbsp;&nbsp;&nbsp;&nbsp;y = {:3.4f} m</b>".format(calcul_reel["x(t)"].loc[49],calcul_reel["y(t)"].loc[49]), bulletText='-')

item6 = Paragraph("Les coordonnées de l'apogée sont :<br /><b>&nbsp;&nbsp;&nbsp;&nbsp;x = {:3.4f} m<br />&nbsp;&nbsp;&nbsp;&nbsp;y = {:3.4f} m</b>".format(calcul_reel["x(t)"].loc[calcul_reel["y(t)"].argmax()],calcul_reel["y(t)"].loc[calcul_reel["y(t)"].argmax()]), bulletText='-')

mesgraphiques = Paragraph("Graphiques",mySubtitle)
graphique1 = Paragraph("<u>Trajectoire de vol :</u>",mySubSubtitle)
fig1 = Image("./img/fig1.png", width=500, height=200)
fig2 = Image("./img/fig2.png", width=500, height=200)
graphique2 = Paragraph("<u>Evolution de la vitesse :</u>",mySubSubtitle)
fig3 = Image("./img/fig3.png", width=500, height=200)
fig4 = Image("./img/fig4.png", width=500, height=200)
graphique3 = Paragraph("<u>Evolution de la poussée :</u>",mySubSubtitle)
#fig5 = Image("./img/fig5.png", width=500, height=200)
fig6 = Image("./img/fig6.png", width=500, height=200)
graphique4 = Paragraph("<u>Vitesses d'éjection :</u>",mySubSubtitle)
fig7 = Image("./img/fig7.png", width=500, height=200)
fig8 = Image("./img/fig8.png", width=500, height=200)

flowable += [reportName, spacer, moment, monimage, commentary, spacer, item1, spacer_item, item2, spacer_item, item3, spacer_item, item4, spacer_item, item5, spacer_item, item6, spacer, mesgraphiques, spacer_item, graphique1,spacer_item, fig1,spacer_item, fig2, spacer_item, graphique2, spacer_item, fig3, fig4, spacer_item, graphique3, spacer_item, fig6, spacer_item, graphique4, spacer_item, fig7, fig8]

doc.build(flowable)