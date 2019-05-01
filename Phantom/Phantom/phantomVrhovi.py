import cv2 as cv
import numpy as np
import operator
from itertools import combinations

def zdruziNajblizjeTocke(tocke, sredina):
	""" Tocke, ki so skupaj zdruzi v tisto, ki je najblizje sredini """
	
	# Če ni vsaj treh tock
	if len(tocke) <= 3:
		return tocke

	# Izracuna vse razdalje med vsemi tockami
	razdalje = []
	for i in range(len(tocke) - 1):
		v1 = tocke[i]
		for j in range(i + 1, len(tocke)):
			v2 = tocke[j]
			razdalje.append({"t1": v1, "t2": v2, "razdalja": np.linalg.norm(v1 - v2)})

	# Razvrsti po razdaljah
	razdalje = sorted(razdalje, key = lambda r: r["razdalja"])

	# Brise tocke dokler jih je vec kot 3
	while len(tocke) > 3:

		# Ce so prevec narazen vrni tri tocke, ki se najbolje prilegajo trikotniku
		if razdalje[0]["razdalja"] > 60:
			kombinacije = list(combinations(tocke, 3))
			
			# Izracunam napake za vsako kombinacijo
			napake = []
			for k in kombinacije:
				""" Dodaj se napako zaradi prevelikega ali premajhnega trikotnika """
				n = napakaTrikotnika(list(k))
				napake.append({"n": n, "k": k})

			# Razvrsti po napakah
			napake = sorted(napake, key = lambda n: n["n"])

			# Vrnem najboljso kombinacijo
			return napake[0]["k"]

		# Dolocim najblizji tocki
		najblizja = razdalje.pop(0)

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

def napakaTrikotnika(tocke):
	""" Izracuna kako dobro se tocke prilegajo trkotniku """
	v1 = np.sum((tocke[0] - tocke[1]) ** 2)
	v2 = np.sum((tocke[1] - tocke[2]) ** 2)
	v3 = np.sum((tocke[2] - tocke[0]) ** 2)

	v = np.array((v1, v2, v3))
	std = np.std(v)
	avg = np.average(v)

	""" DELJENJE Z 0 ?? """
	return std / avg

def tvorijoTrikotnik(tocke):
	""" Vrne True ce tocke tvorijo trikotnik (s toleranco) """
	return napakaTrikotnika(tocke) < 0.25

def najdiVrhe(slika, izpisujOpozorila = False):
	"""
	Slika je slika na kateri isce
	Ce je izpisuj obvestila True bo v konzolo printal zakaj ni nasel vrhov
	Vrne tocke vrhovov robotov ali None"""

	slika = slika.copy()
	
	# Filtrira barvo
	hsv = cv.cvtColor(slika, cv.COLOR_BGR2HSV)
	maska = cv.inRange(hsv, (7, 165, 90), (17, 255, 155))
	#cv.imshow("vrhovi maska1", maska)
	
	# Odstranim sum
	maska = cv.medianBlur(maska, 5)	

	# Zapiranje
	kernel = np.ones((7, 7), np.uint8)
	maska = cv.dilate(maska, kernel, iterations = 4)
	maska = cv.erode(maska, kernel, iterations = 4)
	#cv.imshow("vrhovi maska2", maska)

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
		if povrsina < 70 or povrsina > 1100:
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
	#	cv.circle(slika, tuple(v), 5, (255, 255, 255), -1)
	#cv.imshow("vrhovi", slika)

	le = len(vrhiRobotov)
	# Če ni našel treh vrhov
	if le < 3:
		if izpisujOpozorila: print("Nisem nasel treh tock")
		return None

	# Če je preveč vrhov
	elif le > 3:
		vrhiRobotov = zdruziNajblizjeTocke(vrhiRobotov, sredinaSlike)	

	#for v in vrhiRobotov:
	#	cv.circle(slika, tuple(v), 3, (255, 0, 255), -1)
	#cv.imshow("vrhovi", slika)

	# Če so dokaj smiselno postavleni
	if not tvorijoTrikotnik(vrhiRobotov):
		if izpisujOpozorila: print("Ne tvorijo trikotnika")
		return None

	# Vrne vrhove
	return np.array(vrhiRobotov)
