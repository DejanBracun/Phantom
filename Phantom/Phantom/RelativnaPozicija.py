import cv2 as cv
import numpy as np

def vrniNajblizjoTocko(tocka, obroba):
	"""
	Vrne tocko, ki je na obrobi in je najblizja parametru tocka 
	tocka - okrog katere tocke me zanima
	obroba - na kateri obrobi iscem
	"""
	obroba = obroba[0]
	index = 0
	najboljsa = 1e+9
	for i in range(obroba.shape[0]):
		razdalja = np.linalg.norm(tocka - obroba[i][0])
		if razdalja < najboljsa:
			najboljsa = razdalja
			index = i
	return obroba[index][0]

def relativnaPozicijaKrogle(krogla, elipsa):
	"""
	Izracuna relativno pozicijo krogle na elipsi
	krogla - tocka pozicija krogle
	elipsa - elipsa plosce
	"""
	ploscaCenter, (MA, ma), kot = elipsa

	vk = np.array(krogla) - np.array(ploscaCenter) + np.array((ma, MA))
	maska = np.zeros((MA * 2, ma * 2), dtype = np.uint8)
	maska = cv.ellipse(maska, (ma, MA), (MA, ma), kot, 0, 360, 255, -1)
	obroba = cv.findContours(maska, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
	robnaTocka = vrniNajblizjoTocko(vk, obroba[0])

	relativno = (vk - np.array((ma, MA))) / np.linalg.norm(robnaTocka - np.array((ma, MA)))

	#cv.circle(maska, tuple(robnaTocka), 3, 0, -1)
	#cv.circle(maska, tuple(vk.astype(np.int)), 3, 0, -1)
	#maska = cv.drawContours(maska, obroba[0], -1, 128, -1)
	#cv.imshow("test", maska)
	return relativno