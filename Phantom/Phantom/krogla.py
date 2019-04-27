import cv2 as cv
import numpy as np

def vrniKroglo(slika, elipsa, izpisujOpozorila = False):
	""" slika - rabi sliko na kateri isce
	elipsa - kje naj isce
	izpisujOpozorila - ali izpisuje opozorila v cmd
	Vrne tocko kje se nahaja krogla """

	slika = slika.copy()

	# Maskiram da isce samo znotraj elipse
	slika *= cv.ellipse(np.zeros(slika.shape, dtype = np.uint8), elipsa[0], elipsa[1], elipsa[2], 0, 360, (1, 1, 1), -1)

	""" TO JE ŠE TREBA POPRAVIT DA NE ZAZNA BARVE ROKE """

	# Maskiram po barvi zogice
	slika = cv.bitwise_and(slika, slika, mask = np.where(
		(slika[:, :, 0] >= 3) & (slika[:, :, 0] <= 90) &
		(slika[:, :, 1] >= 6) & (slika[:, :, 1] <= 105) &
		(slika[:, :, 2] >= 15) & (slika[:, :, 2] <= 130)
		, 255, 0).astype(np.uint8))

	# Odstrani majhne tocke
	slika = cv.medianBlur(slika, 5)

	# V crno belo
	slika = np.where((slika[:, :, 0] > 0) & (slika[:, :, 1] > 0) & (slika[:, :, 2] > 0), 255, 0).astype(np.uint8)

	# Zapolni zogo (zapiranje)
	kernel = np.ones((3, 3), np.uint8) 
	slika = cv.dilate(slika, kernel)
	slika = cv.erode(slika, kernel)

	#cv.imshow("maska", slika)

	# Najde obrobe
	obroba = cv.findContours(slika, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
	
	# Če ni našel obrob
	if obroba is None:
		if izpisujOpozorila: print("Ne najdem robov")
		return None, None

	for o in obroba[0]:
		# Površina obrobe more vstrezat
		""" Te meje bi lahko določil z razmerjem vrhov.. če so roboti dvignjeni so blizje kameri in zato je zogica vecja """
		povrsina = cv.contourArea(o)
		if povrsina < 300 or povrsina > 600:
			continue

		# Če imam manj kot 5 točk ne morem določit elipse
		if o.shape[0] < 5:
			continue

		# Določim elipso na dane točke obrobe
		tocka, (MA, ma), kot = cv.fitEllipse(o)
		(MA, ma) = (MA / 2, ma / 2)
		#cv.ellipse(testnaSlika, (int(tocka[0]), int(tocka[1])), (int(MA), int(ma)), int(kot), 0, 360, (255, 255, 255))

		# Ali je približno krog
		avg = np.average(np.array((MA, ma)))
		if np.abs(MA - ma) > avg * 0.2:
			continue

		# Vrne zaokroženo
		return (int(tocka[0]), int(tocka[1])), int(avg)

	return None, None

