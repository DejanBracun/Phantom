import cv2 as cv
import numpy as np

debug = True

# region stara koda
#def vrniNajblizjoTocko(tocka, obroba):
#	"""
#	Vrne tocko, ki je na obrobi in je najblizja parametru tocka 
#	tocka - okrog katere tocke me zanima
#	obroba - na kateri obrobi iscem
#	"""
#	obroba = obroba[0]
#	index = 0
#	najboljsa = 1e+9
#	for i in range(obroba.shape[0]):
#		razdalja = np.linalg.norm(tocka - obroba[i][0])
#		if razdalja < najboljsa:
#			najboljsa = razdalja
#			index = i
#	return obroba[index][0]

#def relativnaPozicijaKrogle(krogla, elipsa):
#	"""
#	Izracuna relativno pozicijo krogle na elipsi
#	krogla - tocka pozicija krogle
#	elipsa - elipsa plosce
#	"""
#	ploscaCenter, (MA, ma), kot = elipsa
#	if referenca is None:
#		referenca = ploscaCenter

#	# Pozicija glede na plosco
#	vk = np.array(krogla) - np.array(ploscaCenter) + np.array((ma, MA))
#	# Maskiram ven samo plosco
#	maska = np.zeros((MA * 2, ma * 2), dtype = np.uint8)
#	maska = cv.ellipse(maska, (ma, MA), (MA, ma), kot, 0, 360, 255, -1)
#	obroba = cv.findContours(maska, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
#	robnaTocka = vrniNajblizjoTocko(vk, obroba[0])

#	if debug:
#		cv.circle(maska, tuple(vk), 2, 100, -1)
#		cv.circle(maska, tuple(robnaTocka), 3, 100)
#		cv.imshow("Relativna poz", maska)

#	relativno = (vk - np.array((ma, MA))) / np.linalg.norm(robnaTocka - np.array((ma, MA)))

#	return relativno
# endregion



def relativnaPozicijaKrogle(krogla, elipsa, referencaP = None):
	"""
	Izracuna relativno pozicijo krogle na elipsi
	krogla - tocka pozicija krogle
	elipsa - elipsa plosce
	referenca - v katero tocko se zelim premaknit
	"""
	krogla = np.array(krogla)

	ploscaCenter, (MA, ma), kot = elipsa
	referenca = np.array(ploscaCenter)
	referencaLokalna = referenca if referencaP is None else np.array(referencaP)

	# Za koliko poveca sliko
	obroba = 100

	# Maskiram ven samo plosco
	d = np.max([MA, ma])
	maska = np.zeros([(d + obroba) * 2, (d + obroba) * 2], dtype = np.uint8)
	maska = cv.ellipse(maska, tuple(np.floor(np.flip(np.array(maska.shape) / 2)).astype(np.int32)), (MA, ma), kot, 0, 360, 255, -1)

	# Pozicija glede na plosco
	vk = krogla - referenca + (np.array(maska.shape) / 2).astype(np.int32)
	vrl = referencaLokalna - referenca + (np.array(maska.shape) / 2).astype(np.int32)

	# vektor krogla referenca
	vkr = krogla - referencaLokalna
	normVkr = np.linalg.norm(vkr)
	if normVkr:
		vkrNorm = vkr / normVkr
	else:
		vkrNorm = vkr

	# Najde robno tocko v smeri vkrNorm
	i = 0
	robnaTocka = vk
	while maska[robnaTocka[1], robnaTocka[0]]:
		i += 1
		robnaTocka = np.round(vk + vkrNorm * i).astype(np.int32)
	robnaTocka = np.round(vk + vkrNorm * i - 1).astype(np.int32)

	if debug:
		cv.circle(maska, tuple(vk), 2, 100, -1)
		cv.circle(maska, tuple(robnaTocka), 5, 100)
		#cv.line(maska, tuple(vk), tuple(referenca), 50)
		cv.line(maska, tuple(vk), tuple(vrl), 50)
		cv.imshow("Relativna poz", maska)

	# Izracuna relativno med vk in robno
	relativno = (vk - vrl) / np.linalg.norm(robnaTocka - vrl)
	return relativno * np.array([-1, 1])