import sys
import numpy as np
import cv2 as cv

# Ali rise maske, tocke, itd.?
debug = True

# Hrani tocke trajektorije
trajektorija = []

# region stara funkcija
#def NajdiTrajektorijo(slika, elipsa):
#	"""
#	V sliki najde trajektorijo
#	slika - v kateri sliki isce trajektorijo
#	elipsa - elipsa plosce
#	"""

#	slika = slika.copy()

#	# Maskiram po plosci
#	slika *= cv.ellipse(np.zeros(slika.shape, dtype = np.uint8), elipsa[0], elipsa[1], elipsa[2], 0, 360, (1, 1, 1), -1)

#	# Pretvorim v hsv prostor
#	slika = cv.cvtColor(slika, cv.COLOR_BGR2HSV)

#	# Maskiram po barvi
#	slika = cv.inRange(slika, (29, 10, 150), (70, 50, 200))
#	if debug: cv.imshow("trajektorija maska1", slika)

#	# Poveze
#	kernel = np.ones((3, 3), np.uint8)
#	slika = cv.dilate(slika, kernel, iterations = 5)
#	slika = cv.erode(slika, kernel, iterations = 5)

#	# Odstrani majhne delce
#	slika = cv.medianBlur(slika, 3)

#	if debug: cv.imshow("trajektorija maska2", slika)

#	# Gauss
#	slika = cv.GaussianBlur(slika, (5, 5), 2)

#	if debug: cv.imshow("trajektorija maska3", slika)

#	#raise NotImplementedError
#	return None
# endregion

# region stara koda
#def NajdiTrajektorijo(slika, elipsa):
#	"""
#	V sliki najde trajektorijo
#	slika - v kateri sliki isce trajektorijo
#	elipsa - elipsa plosce
#	"""

#	slika = slika.copy()

#	# Obrezi sliko
#	d = np.max(elipsa[1])
#	x = elipsa[0][0] - d
#	y = elipsa[0][1] - d
#	slika = slika[y: elipsa[0][1] + d, x: elipsa[0][0] + d]

#	# Maskiram po plosci
#	slika *= cv.ellipse(np.zeros(slika.shape, dtype = np.uint8), tuple(elipsa[0] - np.array((x, y))), elipsa[1], elipsa[2], 0, 360, (1, 1, 1), -1)

#	# Gauss
#	slika = cv.GaussianBlur(slika, (3, 3), 1)

#	# Sharp
#	slika = cv.filter2D(slika, -1, np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]))

#	# Median
#	slika = cv.medianBlur(slika, 3)

#	# Gamma
#	#invGamma = 2
#	#table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
#	#slika = cv.LUT(slika, table)

	
#	slika = cv.cvtColor(slika, cv.COLOR_BGR2HLS)
#	l = slika[:, :, 1]
#	k, n = vrniPremico(np.array([140, 0]), np.array([200, 255]))
#	l = l * k + n
#	l = np.clip(l, 0, 230)
#	slika[:, :, 1] = l
#	slika[:, :, 0] = cv.GaussianBlur(slika[:, :, 0], (9, 9), 1)

#	slika1 = cv.cvtColor(slika, cv.COLOR_HLS2BGR)


#	if debug: cv.imshow("trajektorija maska1", slika1)
#	if debug: cv.setMouseCallback("trajektorija maska1", onMouse, slika)

#	slika = cv.inRange(slika, (30, 0, 0), (70, 180, 255))

#	if debug: cv.imshow("trajektorija maska2", slika)

#	# Poveze
#	kernel = np.ones((3, 3), np.uint8)
#	slika = cv.dilate(slika, kernel, iterations = 2)
#	slika = cv.erode(slika, kernel, iterations = 2)

#	# Kontra
#	slika = cv.medianBlur(slika, 3)

#	if debug: cv.imshow("trajektorija maska3", slika)
	
#	# Katastrofa....
#	# Katastrofa....
#	# Katastrofa....
#	# Katastrofa....
#	# Katastrofa....
#	# Katastrofa....



#	return None
# endregion


def obreziSliko(slika, elipsa):
	"""
	Obreze sliko tako, da dobis samo del kjer je elipsa
	slika - katero sliko obreze
	elipsa - okrog katere elipse
	Vrne obrezano sliko in relativno lokacijo kje se ta nahaja na prejsnjo
	"""

	# Obreze kar po najdajlji crti, da se ne mucim s kotom..
	d = np.max(elipsa[1])

	# Izracuna meje
	x1 = elipsa[0][0] - d
	y1 = elipsa[0][1] - d
	x2 = elipsa[0][0] + d
	y2 = elipsa[0][1] + d

	# Preveri in popravi ce so zunaj slike
	if x1 < 0:
		x1 = 0
	if y1 < 0:
		y1 = 0
	if x2 > slika.shape[1]:
		x2 = slika.shape[1]
	if y2 > slika.shape[0]:
		y2 = slika.shape[0]

	return slika[y1: y2, x1: x2], np.array([x1, y1])

def NajdiTrajektorijo(slika, elipsa):
	"""
	V sliki najde trajektorijo
	slika - v kateri sliki isce trajektorijo
	elipsa - elipsa plosce
	"""

	slika = slika.copy()

	# Obrezi sliko
	slika, lokacija = obreziSliko(slika, elipsa)

	# Maskiram izven plosce
	slika *= cv.ellipse(np.zeros(slika.shape, dtype = np.uint8), tuple(elipsa[0] - lokacija), elipsa[1], elipsa[2], 0, 360, (1, 1, 1), -1)

	# Gauss
	slika = cv.GaussianBlur(slika, (3, 3), 2)

	# Sharp
	slika = cv.filter2D(slika, -1, np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]]))

	# Canny
	""" Popravi parametre """
	slika = cv.Canny(slika, 30, 300)

	if debug: cv.imshow("trajektorija maska", slika)








	return None


# Brisi
def onMouse(event, x, y, flags, param):
	print("{1: %3d, 2: %3d, 3: %3d}" % tuple(param[y, x]))

def vrniPremico(tocka1, tocka2):
	k = (tocka1[1] - tocka2[1]) / (tocka1[0] - tocka2[0])
	n = tocka1[1] - k * tocka1[0]
	return k, n





def vrniNaslednjoTocko():
	"""
	Vrne naslednjo tocko v trajektoriji
	Ideja je da glavni program klice to vsakih x mili sekund in dobi novo ref tocko
	"""


	raise NotImplementedError
	return None

