import cv2 as cv
import numpy as np

def vrniKroglo(slika, elipsa, izpisujOpozorila = False):
	""" slika - rabi sliko na kateri isce
	elipsa - kje naj isce
	izpisujOpozorila - ali izpisuje opozorila v cmd
	Vrne tocko kje se nahaja krogla """

	slika = slika.copy()

	# maskiram da isce samo znotraj elipse
	slika *= cv.ellipse(np.zeros(slika.shape, dtype = np.uint8), elipsa[0], elipsa[1], elipsa[2], 0, 360, (1, 1, 1), -1)

	# maskiram po barvi zogice
	slika = cv.bitwise_and(slika, slika, mask = np.where(
		(slika[:, :, 0] >= 13) & (slika[:, :, 0] <= 50) &
		(slika[:, :, 1] >= 22) & (slika[:, :, 1] <= 60) &
		(slika[:, :, 2] >= 37) & (slika[:, :, 2] <= 70)
		, 255, 0).astype(np.uint8))

	# Odstrani majhne tocke
	slika = cv.medianBlur(slika, 5)

	# V crno belo
	slika = cv.threshold(slika, 1, 255, cv.THRESH_BINARY)[1]
	
	# Zapolni zogo (zapiranje)
	kernel = np.ones((3, 3), np.uint8) 
	slika = cv.dilate(slika, kernel)
	slika = cv.erode(slika, kernel)

	cv.imshow("testna", slika)
	
	
	# Jajca
	obroba = cv.findContours(slika.astype(np.float), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
	if obroba is None:
		if izpisujOpozorila: print("Ne najdem robov")
		return None

	for o in obroba[0]:
		povrsina = cv.contourArea(o)
		if povrsina < 0 or povrsina > 9999999:
			continue






	return None, None

