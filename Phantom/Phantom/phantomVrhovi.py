import cv2 as cv
import numpy as np
import operator

def zdruziNajblizjeTocke(tocke, sredina):
	""" Tocke, ki so skupaj zdruzi v tisto, ki je najblizje sredini """
	while len(tocke) > 3:

		""" To lahko optimiziram.. Ne rabim vedno razdalje na novo računat in da jih ne podvaja"""
		# Izracuna vse razdalje med vsemi tockami
		razdalje = []
		for v1 in tocke:
			for v2 in tocke:
				if v1 is v2:
					continue
				razdalje.append({"t1": v1, "t2": v2, "razdalja": np.linalg.norm(v1 - v2)})

		# Najde najblizji točki
		najblizja = {"t1": None, "t2": None, "razdalja": np.inf}
		for r in razdalje:
			if r["razdalja"] < najblizja["razdalja"]:
				najblizja = r 
		
		""" Dodaj da če je najmanjsa razdalja med tockam recimo 70 neha brisat in vrne najblizje 3 tocke """
		#if najblizja["razdalja"] > 70:
		#	for t1 in razdalje:
		#		for t2 in razdalje:
		#			if t1

		#	sort = sorted(razdalje, key = operator.itemgetter("razdalja"))
		#	return sort[0:3]
		
		# Doloci katero bo izbrisal
		r0 = np.linalg.norm(sredina - najblizja["t1"])
		r1 = np.linalg.norm(sredina - najblizja["t2"])
		brisi = najblizja["t1"] if r0 > r1 else najblizja["t2"]

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

	v = np.array((v1, v2, v3))
	std = np.std(v)
	avg = np.average(v)
	return std / avg < 0.3

def najdiVrhe(slika, izpisujOpozorila = False):
	""" Slika je slika na kateri isce
	Ce je izpisuj obvestila True bo v konzolo printal zakaj ni nasel vrhov
	Vrne tocke vrhovov robotov ali None"""

	slika = slika.copy()
	
	""" Zgleda da bi bilo bolje to filtrirat v HSV """
	# Filtrira barvo
	maska = np.where(
		(slika[:, :, 0] >= 0)	& (slika[:, :, 0] <= 45) & 
		(slika[:, :, 1] >= 20)	& (slika[:, :, 1] <= 80) & 
		(slika[:, :, 2] >= 95)	& (slika[:, :, 2] <= 160), 255, 0).astype(np.uint8)
	maska = cv.medianBlur(maska, 5)

	# Zapiranje
	kernel = np.ones((11, 11), np.uint8)
	maska = cv.dilate(maska, kernel)
	maska = cv.erode(maska, kernel)
	cv.imshow("vrhovi maska", maska)

	# Za iskanje točk najbližje sredini
	sredinaSlike = np.flip(np.floor(np.array(maska.shape) / 2))
	#cv.circle(slika, tuple(sredinaSlike.astype(np.int)), 5, (255, 255, 0), -1)

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
		if povrsina < 80 or povrsina > 1000:
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

	for v in vrhiRobotov:
		cv.circle(slika, tuple(v), 5, (255, 255, 255), -1)
	cv.imshow("vrhovi", slika)

	le = len(vrhiRobotov)
	# Če ni našel treh vrhov
	if le < 3:
		if izpisujOpozorila: print("Nisem nasel treh tock")
		return None

	# Če je preveč vrhov
	elif le > 3:
		vrhiRobotov = zdruziNajblizjeTocke(vrhiRobotov, sredinaSlike)	

	for v in vrhiRobotov:
		cv.circle(slika, tuple(v), 3, (255, 0, 255), -1)
	cv.imshow("vrhovi", slika)

	# Če so dokaj smiselno postavleni
	if not tvorijoTrikotnik(vrhiRobotov):
		if izpisujOpozorila: print("Ne tvorijo trikotnika")
		return None

	# Vrne vrhove
	return np.array(vrhiRobotov)
