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
import Trajektorija
import CenterTrikotnika
import CenterTrikotnik2
import CenterTrikotnik3
import Trajektorija

def elipsa(tocke, slika):
	"""
	Tocke je vektor iz treh tock za elipso
	Vrne parametre elipse
	"""
	slika = slika.copy()

	#c = CenterTrikotnika.vrniCenter(tocke)
	c1 = CenterTrikotnik2.VrniCenter(tocke)
	#c33 = CenterTrikotnik3.VrniCenter(tocke)
	c2 = np.average(tocke, axis = 0)
	c = np.average(np.array([c1, c2]), axis = 0)

	nove = list(tocke)
	for t in tocke:
		nove.append(list(c - np.array(t) + c))
		#cv.drawMarker(slika, tuple(np.array((c - np.array(t) + c), dtype = np.int)), (255, 200, 200), cv.MARKER_TILTED_CROSS, 15)
	(x, y), (MA, ma), kot = cv.fitEllipseDirect(np.array(nove).astype(np.int32))
	return (int(x), int(y)), (int(MA / 2), int(ma / 2)), int(kot)
	
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
FPS.NastaviZeljeniFPS(30)

while(cap.isOpened() and not koncajProgram):

	#region Za Keyboard
	#try:  # used try so that if user pressed other than the given key error will not be shown
	#	if keyboard.is_pressed('q'):  # if key 'q' is pressed 
	#		print('You Pressed A Key!')
	#		break  # finishing the loop
	#	else:
	#		pass
	#except:
	#	break  # if user pressed a key other than the given key the loop will break
	#endregion

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
			cv.circle(slika, kroglaTocka, kroglaPolmer, (255, 0, 255), 2)
			
			# Za posiljanje na simulink
			pozicijaProcent = relativnaPozicijaKrogle(kroglaTocka, (ploscaCenter, (MA, ma), kot))
			Simulink.poslji(pozicijaProcent[0], -pozicijaProcent[1], 0)

		# Za trajektorijo
		Trajektorija.NajdiTrajektorijo(slikaOrg, [ploscaCenter, (MA, ma), kot])

	cv.putText(slika, "Dvojni klik, da zapres", (5, 20), 4, 0.5, (255, 255, 255))
	cv.putText(slika, f"FPS: %.2f" % FPS.VrniFps(), (5, slika.shape[0] - 15), 4, 0.5, (255, 255, 255))
	cv.imshow("Slika", slika)
	cv.setMouseCallback("Slika", onMouse, slikaOrg)

	# Za posnet video
	if snemaj: video.DodajFrame(slika)

	# Za cv.imshow() da vidis kaj dela
	cv.waitKey(1)

	# Za FPS
	FPS.Klici(Izpisi = False)


# Za posnet video
if snemaj: video.Koncal()

cv.destroyAllWindows()