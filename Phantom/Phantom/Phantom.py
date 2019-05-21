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


def kotMedVektorji(v1, v2):
	return np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])


def elipsa(tocke, slika):
	"""
	Tocke je vektor iz treh tock za elipso
	Vrne parametre elipse
	"""
	slika = slika.copy()

	c = np.average(tocke, axis = 0)

	nove = list(tocke)
	for t in tocke:
		nove.append(list(c - np.array(t) + c))
		#cv.drawMarker(slika, tuple(np.array((c - np.array(t) + c), dtype = np.int)), (255, 200, 200), cv.MARKER_TILTED_CROSS, 15)
	(x, y), (MA, ma), kot = cv.fitEllipseDirect(np.array(nove).astype(np.int32))
	#MA, ma = int(MA * 1.05), int(ma * 1.05) # Da malo poveča elipso
	#E1, E2, E3 = (int(x), int(y)), (int(MA / 2), int(ma / 2)), int(kot)
	E1, E2, E3 = np.array([x, y]), np.array([MA / 2, ma / 2]), np.array(kot)

	# region Boljše prileganje 2
	hsv = cv.cvtColor(slika, cv.COLOR_BGR2HSV)

	nove = []
	preveriNajvec = 20 # Koliko tock naj najvec preveri predno obupa
	kotZacetni = kotMedVektorji(np.array([1, 0]), tocke[0] - E1)
	kotPremika = 2 * np.pi / preveriNajvec

	# Zmesa seznam (zmesa vrsti red po katerem bo iskal robove)
	vsi = np.arange(preveriNajvec)
	np.random.shuffle(vsi)

	for i in vsi:
		# Kot pod katerem trenutno iscem
		kot = kotPremika * i + kotZacetni
		# Enotski vektor v kateri smeri trenutno iscem
		v = np.array([np.cos(kot), np.sin(kot)]) 

		# Preveri linijo v katero kaze vektor v
		for s in range(int(np.min(E2) * 0.9), int(np.max(E2) * 1.1), 1):
			# Pixel, ki ga pregleduje
			pix = np.round(v * s + E1).astype(np.uint)

			# Ce je pixel preblizu tocke vrha odnehaj
			for t in tocke:
				if np.linalg.norm(pix - t) < 10:
					break
			else:

				# Ce je pixel izven meja slike odnehaj
				if pix[0] < 0 or pix[0] > hsv.shape[1] - 1 or pix[1] < 0 or pix[1] > hsv.shape[0] - 1:
					break

				#cv.drawMarker(slika, tuple(pix), (0, 100, 50), cv.MARKER_CROSS, 1)
			
				# Preveri ali je pixel dovolj temen
				if hsv[pix[1], pix[0], 2] < 50:
					#cv.drawMarker(slika, tuple(pix), (0, 255, 150), cv.MARKER_SQUARE, 10)
					nove.append(pix)
					break

		if len(nove) > 8:
			break
	
	#cv.imshow("debuggggg", slika)
	(x, y), (MA, ma), kot = cv.fitEllipseDirect(np.array(nove, dtype = np.int))
	E1, E2, E3 = (int(x), int(y)), (int(MA / 2), int(ma / 2)), int(kot)
	# endregion


	#E1, E2, E3 = (int(E1[0]), int(E1[1])), (int(E2[0]), int(E2[1])), int(E3)
	return E1, E2, E3
	
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
		ploscaCenter, (MA, ma), kot = elipsa(vrhovi, slikaOrg)
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

	# Brisi
	print(FPS.VrniFps())

	# Za posnet video
	if snemaj: video.DodajFrame(slikaOrg)

	# Za cv.imshow() da vidis kaj dela
	cv.waitKey(1)

	# Za FPS
	FPS.Klici(Izpisi = False)

# Za posnet video
if snemaj: video.Koncal()

cv.destroyAllWindows()
