import cv2 as cv
import numpy as np

def vrniKroglo(slika, elipsa, izpisujOpozorila = False):
	"""
	slika - rabi sliko na kateri isce
	elipsa - kje naj isce
	izpisujOpozorila - ali izpisuje opozorila v cmd
	Vrne tocko kje se nahaja krogla
	"""

	slika = slika.copy()

	#brisi = slika.copy()

	# Maskiram po plosci
	slika *= cv.ellipse(np.zeros(slika.shape, dtype = np.uint8), elipsa[0], elipsa[1], elipsa[2], 0, 360, (1, 1, 1), -1)

	# Pretvorim v hsv prostor
	slika = cv.cvtColor(slika, cv.COLOR_BGR2HSV)

	# Maskiram po barvi zogice
	slika = cv.inRange(slika, (0, 1, 0), (30, 160, 100))
	#cv.imshow("krogla maska1", slika)

	# Odstrani majhne tocke
	slika = cv.medianBlur(slika, 3)

	# Zapolni zogo (zapiranje)
	kernel = np.ones((3, 3), np.uint8) 
	slika = cv.dilate(slika, kernel)
	slika = cv.erode(slika, kernel)

	#cv.imshow("krogla maska2", slika)

	# Najde obrobe
	obroba = cv.findContours(slika, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
	
	# Če ni našel obrob
	if obroba is None:
		if izpisujOpozorila: print("Ne najdem robov")
		return None, None

	# Razvrstim obrobe po povrsini
	obrobe = []
	for o in obroba[0]:
		obrobe.append({"o": o, "povrsina": cv.contourArea(o)})
	obrobe = sorted(obrobe, key = lambda o: o["povrsina"], reverse = True)

	for o in obrobe:
		# Površina obrobe more vstrezat
		""" Te meje bi lahko določil z razmerjem vrhov.. če so roboti dvignjeni so blizje kameri in zato je zogica vecja """
		if o["povrsina"] < 270 or o["povrsina"] > 650:
			continue

		# Če imam manj kot 5 točk ne morem določit elipse
		if o["o"].shape[0] < 5:
			continue

		# Določim elipso na dane točke obrobe
		tocka, (MA, ma), kot = cv.fitEllipse(o["o"])
		(MA, ma) = (MA / 2, ma / 2)

		#cv.ellipse(brisi, (int(tocka[0]), int(tocka[1])), (int(MA), int(ma)), int(kot), 0, 360, (255, 255, 255))
		#cv.imshow("krogla slika", brisi)

		# Ali je približno krog
		avg = np.average(np.array((MA, ma)))
		if np.abs(MA - ma) > avg * 0.25:
			continue

		# Vrne zaokroženo
		return (int(tocka[0]), int(tocka[1])), int(avg)

	return None, None

