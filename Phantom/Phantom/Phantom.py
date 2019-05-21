import sys
import cv2 as cv
import numpy as np
from FPS import FPS
import phantomVrhovi
#import keyboard
from ShraniVideo import ShraniVideo
import krogla
import Simulink
from RelativnaPozicija import relativnaPozicijaKrogle
from itertools import combinations
from simple_pid import PID
from trajektorijaNaPlosci import narisanaTrajektorija

# region Zacasni sliderji za PID
from tkinter import *
P = 0.9
I = 0
D = 0.21
pid_X = PID(P, I, D, setpoint=0)
pid_Y = PID(P, I, D, setpoint=0)
def show_values(arg):
	global P, I, D
	P = w1.get()
	I = w2.get()
	D = w3.get()
	pid_X.tunings = (P, I, D)
	pid_Y.tunings = (P, I, D)

master = Tk()
w1 = Scale(master, from_=0, to=5, resolution=0.1, command=show_values, orient=HORIZONTAL, width=40, length=1000)
w1.pack()
w1.set(P)
w2 = Scale(master, from_=0, to=5, resolution=0.01, command=show_values, orient=HORIZONTAL, width=40, length=1000)
w2.pack()
w2.set(I)
w3 = Scale(master, from_=0, to=5, resolution=0.01, command=show_values, orient=HORIZONTAL, width=40, length=1000)
w3.pack()
w3.set(D)
#Button(master, text='Show', command = show_values).pack()
# endregion
	
# Ce je True konca glavno zanko
koncajProgram = False
def onMouse(event, x, y, flags, param):
	""" Se klice ob dogodkih miske nad oknom slike """
	global koncajProgram
	koncajProgram = event == cv.EVENT_LBUTTONDBLCLK
	b, g, r = param[y, x]
	h, s, v = cv.cvtColor(param, cv.COLOR_BGR2HSV)[y, x]
	print("{x: %3d, y: %3d} {b: %3d, g: %3d, r: %3d} {h: %3d, s: %3d, v: %3d}" % (x, y, b, g, r, h, s, v))

# Initializacija kamere
cap = cv.VideoCapture(0)

# Za posnet video
snemaj = False
if snemaj: video = ShraniVideo("Test video")

# Za FPS
FPS = FPS()
#FPS.NastaviZeljeniFPS(30)

while(cap.isOpened() and not koncajProgram):

    # Zacasni sliderji za PID
	master.update()

	ret, slikaOrg = cap.read() # Vrne sliko iz kamere
	slika = np.copy(slikaOrg)

	vrhovi = phantomVrhovi.najdiVrhe(slikaOrg, True)
	if vrhovi is not None:

		# Za elipso
		ploscaCenter, (MA, ma), kot = phantomVrhovi.elipsa(vrhovi, slikaOrg)
		cv.ellipse(slika, ploscaCenter, (MA, ma), kot, 0, 360, (255, 255, 255))

		# Za center plosce
		cv.drawMarker(slika, ploscaCenter, (0, 255, 255), cv.MARKER_TILTED_CROSS, 15)

		# Za vrhove robotov
		for v in vrhovi.astype(np.uint):
			cv.drawMarker(slika, tuple(v), (255, 255, 0), cv.MARKER_TILTED_CROSS, 15)

		# Za kroglo
		kroglaTocka, kroglaPolmer = krogla.vrniKroglo(slikaOrg, [ploscaCenter, (MA, ma), kot])
		if kroglaTocka is not None:
			# Narise kroglo
			cv.circle(slika, kroglaTocka, kroglaPolmer, (255, 0, 255), 2)
			
			# Izracun normirane relativne pozicije krogle na plosci
			pozicijaProcent, referencnaTocka = relativnaPozicijaKrogle(kroglaTocka, (ploscaCenter, (MA, ma), kot), None) #, [310, 88]

			# Nelinearizacija
			pp = np.abs(pozicijaProcent)
			#ppa = 1.0 * pp ** 2 + 2.70616862252382e-16 * pp - 9.02056207507939e-17
			ppa = -0.0005566703 + 0.4013623*pp + 2.085112*pp**2 - 1.490928*pp**3
			pozicijaProcent = np.multiply( np.sign(pozicijaProcent), ppa )

			# Pid regulator
			u_x = pid_X(pozicijaProcent[0])
			u_y = pid_Y(pozicijaProcent[1])

			# Poslji na simulink
			Simulink.poslji(u_x, u_y, 0)

		# Za trajektorijo (trenutno se izvaja ves cas)
		#narisanaTrajektorija(slikaOrg, [ploscaCenter, (MA, ma), kot], 2)

	cv.putText(slika, "Dvojni klik, da zapres", (10, 20), 4, 0.5, (255, 255, 255))
	cv.putText(slika, "klikni y za potrditev trajektorije", (10, 40), 4, 0.5, (255, 255, 255))
	cv.putText(slika, f"FPS: %.2f" % FPS.VrniFps(), (5, slika.shape[0] - 15), 4, 0.5, (255, 255, 255))
	cv.imshow("Slika", slika)
	cv.setMouseCallback("Slika", onMouse, slikaOrg)

	# Za posnet video
	if snemaj: video.DodajFrame(slikaOrg)

	# Za cv.imshow() da vidis kaj dela
	cv.waitKey(1)

	# Za FPS
	FPS.Klici(Izpisi = False)

# Za posnet video
if snemaj: video.Koncal()

cv.destroyAllWindows()
