import sys
import socket
import struct
import cv2 as cv
import numpy as np
from FPS import FPS
import phantomVrhovi
#import keyboard
from ShraniVideo import ShraniVideo
import krogla

#static double distanceBtwPoints(const cv::Point a, const cv::Point b)
#{
#    double xDiff = a.x - b.x;
#    double yDiff = a.y - b.y;

#    return std::sqrt((xDiff * xDiff) + (yDiff * yDiff));
#}

#static int findNearestPointIndex(const cv::Point pt, const vector<Point> points)
#{
#    int nearestpointindex = 0;
#    double distance;
#    double mindistance = 1e+9;

#    for ( size_t i = 0; i < points.size(); i++)
#    {
#        distance = distanceBtwPoints(pt,points[i]);

#        if( distance < mindistance )
#        {
#            mindistance =  distance;
#            nearestpointindex = i;
#        }
#    }
#    return nearestpointindex;
#}


def vrniNajblizjoTocko(tocka, obroba):
	""" Vrne tocko, ki je na obrobi in je najblizja parametru tocka 
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
	""" Izracuna relativno pozicijo krogle na elipsi
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

def elipsa(tocke):
	""" tocke je vektor iz treh tock za elipso """
	c = np.average(tocke, axis = 0)
	nove = list(tocke).copy()
	for t in tocke:
		nove.append(list(c - np.array(t) + c))
	(x, y), (MA, ma), kot = cv.fitEllipse(np.array(nove).astype(np.int32))
	return (int(x), int(y)), (int(MA / 2), int(ma / 2)), int(kot)
	
# Ce je True konca glavno zanko
koncajProgram = False
def onMouse(event, x, y, flags, param):
	""" Se kliče ob dogodkih miske nad oknom slike """
	global koncajProgram
	koncajProgram = event == cv.EVENT_LBUTTONDBLCLK
	print(slika[y, x])

# Poslje preko omrezja do simulinka
def send_vals(x, y, z):
	""" Poslje koordinate zogice na simulink """
	vals = (x, y, z)
	packer = struct.Struct('f f f')
	bin_data = packer.pack(*vals)
	sock.sendto(bin_data, (client_ip, port))
	return

# Za posiljanje na simulink
client_ip = "192.168.65.97"
port = 26001
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initializacija kamere
cap = cv.VideoCapture(0)

# Za posnet video
video = ShraniVideo("Test video")

# Za FPS
FPS = FPS()
FPS.NastaviZeljeniFPS(30)

while(cap.isOpened() and not koncajProgram):

	#region Za Keyboard
	#try:  # used try so that if user pressed other than the given key error will not be shown
	#	if keyboard.is_pressed('q'):  # if key 'q' is pressed 
	#		print('You Pressed A Key!')
	#		break  # finishing the loop
	#	else:
	#		pass
	#except:
	#	break  # if user pressed a key other than the given key the loop will break
	#endregion

	ret, slikaOrg = cap.read() # Vrne sliko iz kamere
	slika = np.copy(slikaOrg)
	
	global testnaSlika
	testnaSlika = slika.copy()


	vrhovi = phantomVrhovi.najdiVrhe(slikaOrg)
	if vrhovi is not None:

		# Za elipso
		ploscaCenter, (MA, ma), kot = elipsa(vrhovi)
		cv.ellipse(slika, ploscaCenter, (MA, ma), kot, 0, 360, (255, 255, 255))

		# Za center plosce
		cv.drawMarker(slika, ploscaCenter, (0, 255, 255), cv.MARKER_TILTED_CROSS, 15)

		# Za vrhove robotov
		for v in vrhovi.astype(np.uint):
			cv.drawMarker(slika, tuple(v), (255, 255, 0), cv.MARKER_TILTED_CROSS, 15)
			


		## Dolocitev polmera		
		#r = np.zeros((3))
		#for i in range(3):
		#	r[i] = np.sum((vrhovi[i] - ploscaCenter) ** 2)
		#ploscaPolmer = np.round(np.sqrt(np.average(r))).astype(np.uint)
		
		## Izris kroga plosce
		#cv.circle(slika, tuple(ploscaCenter), ploscaPolmer,(0, 255, 255), 2)

		# Za kroglo
		kroglaTocka, kroglaPolmer = krogla.vrniKroglo(slikaOrg, [ploscaCenter, (MA, ma), kot])
		if kroglaTocka is not None:
			cv.circle(slika, kroglaTocka, kroglaPolmer, (255, 0, 255), 2)
			# Izracun relativne pozicje krogle
			#pozicijaProcent = (kroglaTocka - ploscaCenter) / ploscaPolmer
			pozicijaProcent = relativnaPozicijaKrogle(kroglaTocka, (ploscaCenter, (MA, ma), kot))
			send_vals(pozicijaProcent[0], -pozicijaProcent[1], 0)

		
			
	cv.putText(slika, "Dvojni klik, da zapres", (5, 20), 4, 0.5, (255, 255, 255))
	cv.putText(slika, f"FPS: %.2f" % FPS.VrniFps(), (5, slika.shape[0] - 15), 4, 0.5, (255, 255, 255))	
	cv.setMouseCallback("Slika", onMouse)
	cv.imshow("Slika", slika)

	# Za posnet video
	video.DodajFrame(slikaOrg)

	# Za cv.imshow() da vidis kaj dela
	cv.waitKey(1)

	# Za FPS
	FPS.Klici(Izpisi = False)




# Za posnet video
video.Koncal()

cv.destroyAllWindows()