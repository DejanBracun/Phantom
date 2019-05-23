import sys
import os
import cv2 as cv
import numpy as np
from FPS import FPS
import phantomVrhovi
from ShraniVideo import ShraniVideo
import krogla
import Simulink
from RelativnaPozicija import relativnaPozicijaKrogle
from itertools import combinations
from trajektorijaNaPlosci import narisanaTrajektorija, VrniNaslednjo
import time
from tkinter import *

# za PID
alpha = 0.15
P = 18.0
I = 0
D = 3.9

# region GUI
def show_values(arg):
	global P, I, D, alpha
	P = w1.get()
	I = w2.get()
	D = w3.get()
	alpha = w4.get()

# Referencna tocka
refTocka = None

# Ce si v nacinu za vodenje po trajektoriji
nacinVodenja = "center"

# Za dolocitev tocke za premik centra
zadnjaRefTockaZaPremik = None

def button_klik_traj():
	global nacinVodenja
	narisanaTrajektorija(slikaOrg, [ploscaCenter, (MA, ma), kot], 2)
	nacinVodenja = "trajektorija"

def button_klik_center():
	global refTocka, nacinVodenja
	refTocka = None
	nacinVodenja = "center"

def button_klik_poljubnoSredisce():
	global refTocka, nacinVodenja
	refTocka = zadnjaRefTockaZaPremik
	nacinVodenja = "poljubnaTocka"

masterGui = Tk()
masterGui.geometry('%dx%d+%d+%d' % (600, 400, 0, 0))
w1 = Scale(masterGui, from_=0, to=25, resolution=0.1, command=show_values, orient=HORIZONTAL, width=40, length=1000)
w1.pack()
w1.set(P)
w2 = Scale(masterGui, from_=0, to=5, resolution=0.01, command=show_values, orient=HORIZONTAL, width=40, length=1000)
w2.pack()
w2.set(I)
w3 = Scale(masterGui, from_=0, to=15, resolution=0.01, command=show_values, orient=HORIZONTAL, width=40, length=1000)
w3.pack()
w3.set(D)
w4 = Scale(masterGui, from_=0, to=1, resolution=0.01, command=show_values, orient=HORIZONTAL, width=40, length=1000)
w4.pack()
w4.set(alpha)
w5 = Button(masterGui, text = "Trajektorija", command = button_klik_traj)
w7 = Button(masterGui, text = "Center", command = button_klik_center)
w8 = Button(masterGui, text = "Poljubna tocka", command = button_klik_poljubnoSredisce)
w5.pack()
w7.pack()
w8.pack()
# endregion

posPrejZoga = np.array((0,0), dtype=np.float)
prejnagibRad = 0.0
prejU = np.array((0,0), dtype=np.float)
cas = -1
error = np.array((0,0), dtype=np.float)
prejError = np.array((0,0), dtype=np.float)
prejPosZogaPiksli = np.array((0,0))

cvWindowName = "Slika"
cv.namedWindow(cvWindowName)
cv.moveWindow(cvWindowName, 600, 0)

def PID_regulator(posZoga, posRef, posZogaPiksli):
	
	global prejError, error, cas, prejU, prejnagibRad, alpha, posPrejZoga, P, I, D, prejPosZogaPiksli
	if cas == -1:
		cas = time.time() - 1/30
	
	posZogaPiksli = np.array(posZogaPiksli)
	a = time.time() - cas
	U = P*(posRef - posZoga) + I*(error) + D*((posPrejZoga - posZoga)/(a))
	posPrejZoga = posZoga
	U = U / 100
	cas = time.time()

	lingLang = np.linalg.norm(U)
	if lingLang > 1:
		nagib = 1
	else:
		nagib = lingLang

	#nagibRad = np.sin(nagib)
	nagibRad = nagib
	#nagibRad = 1.10134 + (-1.421521e-18 - 1.10134)/(1 + (nagibRad/0.4103627)**2.57016)
	nagibRad = prejnagibRad*alpha + nagibRad*(1-alpha)
	prejnagibRad = nagibRad
	U = prejU*alpha + U*(1-alpha)
	prejU = U
	

	trenutniError = posRef - posZoga
	#trenutniError = trenutniError*(1-0.2) + prejError*0.2
	#if prejError[0] == trenutniError[0] and prejError[1] == trenutniError[1]:
	#if np.isclose(prejError[0], trenutniError[0],  rtol=1e-02, atol=1e-02) and np.isclose(prejError[1], trenutniError[1],  rtol=1e-02, atol=1e-02):
	#if np.allclose(prejError, trenutniError,  rtol=0, atol=0.01):
	if (np.linalg.norm(posZogaPiksli - prejPosZogaPiksli) ) < 2 and np.linalg.norm(trenutniError) > 0.06:
		error += (posRef - posZoga)
		#print(f"napaka je:{np.linalg.norm(trenutniError)}")
		print(error)
	else: 
		#error = np.array((0,0), dtype=np.float)
		error = np.array((0,0), dtype=np.float)
		print("reset")
	prejError = posRef - posZoga
	prejPosZogaPiksli = posZogaPiksli
	return U, nagibRad

# Ce je True konca glavno zanko
koncajProgram = False
def onMouse(event, x, y, flags, param):
	""" Se klice ob dogodkih miske nad oknom slike """
	global koncajProgram, zadnjaRefTockaZaPremik
	koncajProgram = event == cv.EVENT_LBUTTONDBLCLK
	b, g, r = param[y, x]
	h, s, v = cv.cvtColor(param, cv.COLOR_BGR2HSV)[y, x]
	print("{x: %3d, y: %3d} {b: %3d, g: %3d, r: %3d} {h: %3d, s: %3d, v: %3d}" % (x, y, b, g, r, h, s, v))
	if event == cv.EVENT_LBUTTONUP:
		zadnjaRefTockaZaPremik = [x, y]


# Initializacija kamere
cap = cv.VideoCapture(1)
#cap.set(cv.CAP_PROP_EXPOSURE, 0)
cap.set(cv.CAP_PROP_AUTOFOCUS, 0)

# Za posnet video
snemaj = False
if snemaj: video = ShraniVideo("Test video")

# Za FPS
FPS = FPS()
#FPS.NastaviZeljeniFPS(30)

while(cap.isOpened() and not koncajProgram):

    # GUI
	masterGui.update()

	ret, slikaOrg = cap.read() # Vrne sliko iz kamere
	slika = np.copy(slikaOrg)

	# Za sprehod po trajektoriji
	if nacinVodenja == "trajektorija":
		naslednjaIzTrajektorije = VrniNaslednjo()
		if naslednjaIzTrajektorije is not None:
			refTocka = np.flip(naslednjaIzTrajektorije)

	if refTocka is not None:
		cv.drawMarker(slika, tuple(refTocka), (200, 100, 255), cv.MARKER_TILTED_CROSS, 10, 2)

	vrhovi = phantomVrhovi.najdiVrhe(slikaOrg, True)
	if vrhovi is not None:

		# Za elipso
		ploscaCenter, (MA, ma), kot = phantomVrhovi.elipsa(vrhovi, slikaOrg, True)
		cv.ellipse(slika, ploscaCenter, (MA, ma), kot, 0, 360, (255, 255, 255))

		# Za center plosce
		if refTocka is None:
			cv.drawMarker(slika, ploscaCenter, (0, 255, 255), cv.MARKER_TILTED_CROSS, 15)

		# Za vrhove robotov
		for v in vrhovi.astype(np.uint):
			cv.drawMarker(slika, tuple(v), (255, 255, 0), cv.MARKER_TILTED_CROSS, 15)

		# Za kroglo
		kroglaTocka, kroglaPolmer = krogla.vrniKroglo(slikaOrg, [ploscaCenter, (MA, ma), kot])
		if kroglaTocka is not None:
			# Narise kroglo
			cv.circle(slika, kroglaTocka, kroglaPolmer, (255, 0, 255), 2)
			
			#refTocka = [290, 130]
			#refTocka = None
			# Izracun normirane relativne pozicije krogle na plosci
			pozicijaProcent, _ = relativnaPozicijaKrogle(kroglaTocka, (ploscaCenter, (MA, ma), kot), refTocka, nacinVodenja == "trajektorija")

			# Nelinearizacija
			#pp = np.abs(pozicijaProcent)
			##ppa = 1.0 * pp ** 2 + 2.70616862252382e-16 * pp - 9.02056207507939e-17
			#ppa = -0.0005566703 + 0.4013623*pp + 2.085112*pp**2 - 1.490928*pp**3
			#pozicijaProcent = np.multiply( np.sign(pozicijaProcent), ppa )

			# Pid regulator
			napaka, nagib = PID_regulator(pozicijaProcent, np.array([0, 0]), kroglaTocka)

			# Poslji na simulink
			Simulink.poslji(napaka[0], napaka[1], nagib)
			#Simulink.poslji(0, 0, 1.23456)  #test centra

		# Za trajektorijo (trenutno se izvaja ves cas)
		#narisanaTrajektorija(slikaOrg, [ploscaCenter, (MA, ma), kot], 2)

	cv.putText(slika, "Dvojni klik, da zapres", (10, 20), 4, 0.5, (255, 255, 255))
	if nacinVodenja == "trajektorija":
		 cv.putText(slika, "Vodenje po trajektoriji", (10, 40), 4, 0.5, (255, 255, 255))
	if nacinVodenja == "center":
		 cv.putText(slika, "Vodenje v sredisce", (10, 40), 4, 0.5, (255, 255, 255))
	if nacinVodenja == "poljubnaTocka":
		 cv.putText(slika, "Vodenje v poljubno tocko", (10, 40), 4, 0.5, (255, 255, 255))
	cv.putText(slika, f"FPS: %.2f" % FPS.VrniFps(), (5, slika.shape[0] - 15), 4, 0.5, (255, 255, 255))
	cv.imshow(cvWindowName, slika)
	cv.setMouseCallback(cvWindowName, onMouse, slikaOrg)

	# Za posnet video
	if snemaj: video.DodajFrame(slikaOrg)

	# Za cv.imshow() da vidis kaj dela
	cv.waitKey(1)

	# Za FPS
	FPS.Klici(Izpisi = False)

# Za posnet video
if snemaj: video.Koncal()

cv.destroyAllWindows()
