import cv2 as cv
import numpy as np

def vrniKroglo(slika, center, polmer):
	""" slika - rabi sliko na kateri isce
	center - kje naj isce
	polmer - okrog centra kje naj isce
	Vrne tocko kje se nahaja krogla """

	slika = slika.copy()
	slikaHsv = cv.cvtColor(slika, cv.COLOR_BGR2HSV)

	gray = cv.cvtColor(slika, cv.COLOR_BGR2GRAY)
	gray = cv.GaussianBlur(gray, (3, 3), 2)
	#kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
	#gray = cv.filter2D(gray, -1, kernel)

	_, gray = cv.threshold(gray, 70, 255, cv.THRESH_BINARY_INV)
	#kernel = np.ones((5, 5), np.uint8) 
	#gray = cv.dilate(gray, kernel)
	#gray = cv.erode(gray, kernel)
	
	#for y in range(gray.shape[0]):
	#	for x in range(gray.shape[1]):
	#		gray[y, x] = (np.sqrt(np.sum((np.array([x, y]) - center) ** 2)) < polmer) * gray[y, x]
	
	#gray = cv.GaussianBlur(gray, (7, 7), 100)
	#cv.imshow("gray", gray)

	# min 5, max 25
	#krogi = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 4, 20, minRadius = 15, maxRadius = 20)
	#krogi = cv.HoughCircles(th1, cv.HOUGH_GRADIENT, 8, 50, maxRadius = 40)

	#if krogi is not None:
	#	for krog in krogi[0]:
	#		if np.sqrt(np.sum((krog[0:2] - center) ** 2)) < polmer * 1.1:
	#			cv.circle(slika, (krog[0], krog[1]), krog[2], (0, 255, 0), thickness = 2)



	# maskiram da isce samo okrog centra z radije
	gray = cv.bitwise_and(gray, gray, mask = cv.circle(np.zeros(gray.shape, dtype = np.uint8), tuple(center), polmer, 255, -1))
	
	# maskiram da isce samo tam ko je dost temno
	gray = cv.bitwise_and(gray, gray, mask = np.where((slikaHsv[:, :, 1] <= 230) & (slikaHsv[:, :, 2] <= 50), 255, 0).astype(np.uint8))

	#odstranitev sledi (zapiranje)
	kernel = np.ones((3, 3), np.uint8) 
	gray = cv.dilate(gray, kernel)
	gray = cv.erode(gray, kernel)

	#cv.imshow("gray", gray)




	#ret,thresh = cv.threshold(gray,75, 255,cv.THRESH_BINARY_INV)	
	contours, hierarchy = cv.findContours(gray, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)		
	
	if contours is not None:
		krog = {"napaka": np.inf}
		for cnt in contours:		
			(x, y), radius = cv.minEnclosingCircle(cnt)
			#cv.drawContours(slika, cnt, -1, (0, 0, 255))
			centerKroga = np.array((int(x),int(y)))
			if np.sqrt(np.sum((centerKroga - center) ** 2)) < polmer and radius >= 7 and radius <= 25:
				#cv.circle(slika, tuple(centerKroga), int(radius), (255, 0, 0), 2)
				area = cv.contourArea(cnt)
				napaka = np.abs(area - np.pi * 16 ** 2)
				if napaka < krog["napaka"]:
					krog = {"center": tuple(centerKroga), "radij": int(radius), "napaka": napaka}
		if krog["napaka"] != np.inf:
			#cv.circle(slika, krog["center"], krog["radij"], (0, 255, 0), 1)
			return krog["center"], krog["radij"]

	return None, None

