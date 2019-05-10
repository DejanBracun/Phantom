import cv2 as cv
import numpy as np
from skimage.morphology import skeletonize   #scikit-image module


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

def narisanaTrajektorija(slika, elipsa):
    """Na plosci je narisana trajektrorija po kateri zelimo voditi zogico"""

    # Maskiram da iscemo le znotraj elipse
    slika = slika.copy()
    output = slika.copy()
	# Obrezi sliko
    #slika, lokacija = obreziSliko(slika, elipsa)

	# Maskiram izven plosce
    #slika *= cv.ellipse(np.zeros(slika.shape, dtype = np.uint8), tuple(elipsa[0] - lokacija), elipsa[1], elipsa[2], 0, 360, (1, 1, 1), -1)
    slika *= cv.ellipse(np.zeros(slika.shape, dtype = np.uint8), elipsa[0], elipsa[1], elipsa[2], 0, 360, (1, 1, 1), -1)
    cv.imshow(f'{slika.dtype}', slika)

    blurred = cv.GaussianBlur(slika, (7, 7), 0)
    hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)
    Gray = cv.cvtColor(blurred, cv.COLOR_BGR2GRAY)
    Lower = (90, 10, 100)
    Upper = (190, 250, 175)

    if hsv.dtype == 'uint8' :
        Lower = (90/2, 10, 100)
        Upper = (190/2, 250, 175)

    mask = cv.inRange(hsv, Lower, Upper)
    #cv.imshow('trajektorija', mask)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv.dilate(mask, kernel)
    mask = cv.erode(mask, kernel)
    cv.imshow('trajektorija_zapiranje', mask)

    maskBlurred = cv.GaussianBlur(mask, (7, 7), 0)
    cv.imshow('trajektorija_zapiranje_zamegleno',maskBlurred)

    """Ne bo slo s houghcircles"""
    circles = cv.HoughCircles(maskBlurred, cv.HOUGH_GRADIENT, 7, 10, minRadius=5, maxRadius=25)
    if circles is not None:
	    # pretvorimo v int
        circles = np.round(circles[0, :]).astype("int")
 
	    # narisemo kroge
        for (x, y, r) in circles:
            cv.circle(output, (x, y), r, (0, 255, 0), 4)
    
    _, binarnaMaska = cv.threshold(mask, 127, 1, cv.THRESH_BINARY ) 

    skelet = skeletonize(binarnaMaska).astype(np.uint8)
    output[np.where(skelet==1)] = (0,0,255)
    
    """najdi drugo metodo"""

    # Apply edge detection method on the image 
    #edges = cv.Canny(maskBlurred, 10, 100) 
    #cv.imshow('edges', edges)

    ####Iskanje daljic 
    #lines = cv.HoughLinesP(edges, 3, np.pi/180, 30, minLineLength=2)
    #tocke = []
    #if lines is not None:
    #    for points in lines[:,0]:
    #        theta = np.arctan((points[2]-points[0])/(points[3]-points[1] + 1e-7) )
    #        cv.line(output,(points[0],points[1]), (points[2],points[3]), (0,0,255), 2)
    #        points = np.append(points, theta)
    #        tocke = np.append(tocke, points)
        

      

    ### Iskanje premic
    #lines = cv.HoughLines(edges, 3, np.pi/180, 60)   
    #if lines is not None:
    #    for line in lines:                              
    #        for rho, theta in line:                    
    #            a = np.cos(theta)                     
    #            b = np.sin(theta)
    #            x0 = a*rho                           
    #            y0 = b*rho
    #            x1 = int(x0 + 1000*(-b))           
    #            y1 = int(y0 + 1000*a)
    #            x2 = int(x0 - 1000*(-b))          
    #            y2 = int(y0 - 1000*a)
    #            cv.line(output, (x1, y1), (x2, y2), (0, 0, 255), 1)  #narisemo premico z rdeco barvo , debelina crte



    cv.imshow('output', output)
	# Maskiram po zeleni barvi trajektorije glede na HSV
    #dolocitev zacetne in koncne tocke (mogoce kar z HoughCircles)
    #plotanje vmesnih tock po krivulji 
    

    return