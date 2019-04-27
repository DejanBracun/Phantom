import cv2 as cv
import numpy as np

def zdruziNajblizjeTocke(tocke, sredina):
	""" Tocke, ki so skupaj zdruzi v tisto, ki je najblizje sredini """
	while len(tocke) > 3:

		# Izracuna vse razdalje med vsemi tockami
		razdalje = []
		for v1 in tocke:
			for v2 in tocke:
				if v1 is v2:
					continue
				razdalje.append(np.array((v1, v2, np.sum((v1 - v2) ** 2))))

		# Najde najblizji točki
		najblizja = np.array((None, None, np.inf))		
		for r in razdalje:
			if r[2] < najblizja[2]:
				najblizja = r 
		
		# Doloci katero bo izbrisal
		r0 = np.sum((sredina - najblizja[0]) ** 2)
		r1 = np.sum((sredina - najblizja[1]) ** 2)
		brisi = najblizja[0] if r0 > r1 else najblizja[1]

		# Izbrise
		for i, t in enumerate(tocke):
			if np.all(np.equal(brisi, t)):
				tocke.pop(i)
				break

	return tocke

def tvorijoTrikotnik(tocke):
	""" Vrne True ce tocke tvorijo trikotni (s toleranco) """
	v1 = np.sum((tocke[0] - tocke[1]) ** 2)
	v2 = np.sum((tocke[1] - tocke[2]) ** 2)
	v3 = np.sum((tocke[2] - tocke[0]) ** 2)

	std = np.std(np.array((v1, v2, v3)))
	return std < 17000

def najdiVrhe(slika, izpisujOpozorila = False):
	""" Slika je slika na kateri isce
	Ce je izpisuj obvestila True bo v konzolo printal zakaj ni nasel vrhov
	Vrne tocke vrhovov robotov ali None"""

	slika = slika.copy()
	
	# Filtrira barvo
	maska = np.where(
		(slika[:, :, 0] >= 0)	& (slika[:, :, 0] <= 45) & 
		(slika[:, :, 1] >= 20)	& (slika[:, :, 1] <= 80) & 
		(slika[:, :, 2] >= 100)	& (slika[:, :, 2] <= 160), 255, 0).astype(np.uint8)
	maska = cv.medianBlur(maska, 5)

	# Zapiranje
	kernel = np.ones((11, 11), np.uint8)
	maska = cv.dilate(maska, kernel)
	maska = cv.erode(maska, kernel)
	#cv.imshow("vrhovi maska", maska)

	# Za iskanje točk najbližje sredini
	sredinaSlike = np.flip(np.floor(np.array(maska.shape) / 2))

	# Najde obrobe
	obroba = cv.findContours(maska, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

	# Ce ni nasel obrob
	if obroba is None:
		if izpisujOpozorila: print("Ne najdem robov")
		return None

	# Najblizja tocka vsake obrobe sredini slike
	vrhiRobotov = [] 

	for o in obroba[0]:
		# Če obroba ni prave dimenzije
		povrsina = cv.contourArea(o)
		if povrsina < 80 or povrsina > 800:
			continue

		# Iz vsake obrobe najde tocko najblizje sredini slike
		najblizja = np.array((np.inf, None))
		for point in o:
			p = point[0]
			raz = np.sqrt(np.sum((sredinaSlike - p) ** 2))
			if raz < najblizja[0]:
				najblizja = np.array((raz, p))

		# Shrani najblizjo tocko vsake obrobe
		vrhiRobotov.append(najblizja[1])

	#for v in vrhiRobotov:
	#	cv.circle(slika, tuple(v), 4, (255, 255, 255), -1)
	#cv.imshow("vrhovi", slika)

	le = len(vrhiRobotov)
	# Če ni našel treh vrhov
	if le < 3:
		if izpisujOpozorila: print("Nisem nasel treh tock")
		return None

	# Če je preveč vrhov
	elif le > 3:
		vrhiRobotov = zdruziNajblizjeTocke(vrhiRobotov, sredinaSlike)

	# Če so dokaj smiselno postavleni
	if not tvorijoTrikotnik(vrhiRobotov):
		if izpisujOpozorila: print("Ne tvorijo trikotnika")
		return None

	# Vrne vrhove
	return np.array(vrhiRobotov)
