import cv2 as cv
import numpy as np
from skimage.morphology import skeletonize   #scikit-image module
from math import sqrt

#prikazovanje mask,...
debug = False

""" 
Iskanje najblizje razdalje 
Funkcija rabi kot vhod seznam tock in zacetno tocko
"""
def get_ordered_list(points, x, y):
   points= sorted(points, key = lambda p: sqrt((p[0] - x)**2 + (p[1] - y)**2) )
   return points


def narisanaTrajektorija(slika, elipsa, mode):
    """
    Na plosci je narisana trajektrorija po kateri zelimo voditi zogico
    mode = 1 ----> Fitanje elipse glede na zaznano trajektorijo
    mode = 2 ----> Poljubna trajektorija
    """

    # Maskiram da iscemo le znotraj elipse
    slika = slika.copy()
    output = slika.copy()


	# Maskiram izven plosce
    slika *= cv.ellipse(np.zeros(slika.shape, dtype = np.uint8), elipsa[0], elipsa[1], elipsa[2], 0, 360, (1, 1, 1), -1)

    blurred = cv.GaussianBlur(slika, (7, 7), 0)
    hsv = cv.cvtColor(blurred, cv.COLOR_BGR2HSV)
    Gray = cv.cvtColor(blurred, cv.COLOR_BGR2GRAY)
    Lower = (90, 10, 100)
    Upper = (190, 250, 175)

    if hsv.dtype == 'uint8' :
        Lower = (90/2, 10, 100)
        Upper = (190/2, 250, 175)

    mask = cv.inRange(hsv, Lower, Upper)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv.dilate(mask, kernel)
    mask = cv.erode(mask, kernel)

    if debug == True: cv.imshow('trajektorija_zapiranje', mask)

    maskBlurred = cv.GaussianBlur(mask, (7, 7), 0)

    if mode==2:
        """HougCircles je zelo obcutljiv na velikost radija, bo treba kaj drugega"""
        circles = cv.HoughCircles(maskBlurred, cv.HOUGH_GRADIENT, 7, 5,param1=25,param2=75, minRadius=15, maxRadius=20)
        if circles is not None:
	        # pretvorimo v int
            circles = np.round(circles[0, :]).astype("int")
 
	        # narisemo kroge
            for (x, y, r) in circles:
                cv.circle(output, (x, y), r, (0, 255, 0), 4)
    
        _, binarnaMaska = cv.threshold(mask, 127, 1, cv.THRESH_BINARY ) 

        skelet = skeletonize(binarnaMaska).astype(np.uint8)
        output[np.where(skelet==1)] = (0,0,255)
        
        #dobimo seznam tock s pomocjo skeleta in uredimo tocke tako da tvorijo trajektorijo
        seznam =  np.array( np.where(skelet==1) ).T  #seznam tock
        urejenSeznam = []
        #zacetni piksel!!
        element = [1,1]                     
        for i in range(seznam.shape[0] ):
    
            trenutniSeznam = get_ordered_list(seznam, element[0], element[1])
            element = trenutniSeznam[0]
            urejenSeznam.append( (element[0], element[1]) )
            seznam = np.delete(trenutniSeznam, 0, axis=0) #pravilno brisanje

        urejenSeznam = np.array( urejenSeznam ) 

        urejenSeznam =urejenSeznam[::5]         #decimacija

        if debug==True:
            platno = np.zeros( (output.shape[0],output.shape[1]) )
            for i in urejenSeznam:
                platno[i[0],i[1]] = 255
            cv.imshow("platno", platno)
        

    """
    ISKANJE DALJIC
    """
    #lines = cv.HoughLinesP(edges, 3, np.pi/180, 30, minLineLength=2)
    #tocke = []
    #if lines is not None:
    #    for points in lines[:,0]:
    #        theta = np.arctan((points[2]-points[0])/(points[3]-points[1] + 1e-7) )
    #        cv.line(output,(points[0],points[1]), (points[2],points[3]), (0,0,255), 2)
    #        points = np.append(points, theta)
    #        tocke = np.append(tocke, points)
        

      

    """
    ISKANJE PREMIC
    """
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


    """
    SAMOSTOJNO ISKANJE TRAJEKTORIJE
    potrebni moduli:
    import matplotlib.pyplot as plt
    from sklearn.neighbors import NearestNeighbors
    import networkx as nx
    """
    ##x=seznam[:,0]
    ##y=seznam[:,1]

    #points = np.c_[x, y]

    #clf = NearestNeighbors(2).fit(points)
    #G = clf.kneighbors_graph()

    #T = nx.from_scipy_sparse_matrix(G)

    #order = list(nx.dfs_preorder_nodes(T, 0))

    #xx = x[order]
    #yy = y[order]

    ### Ce zgoraj ne podamo zacetne tocke potreben se spodnji del kode
    #paths = [list(nx.dfs_preorder_nodes(T, i)) for i in range(len(points))]

    #mindist = np.inf
    #minidx = 0

    #for i in range(len(points)):
    #    p = paths[i]           # order of nodes
    #    ordered = points[p]    # ordered nodes
    #    # find cost of that order by the sum of euclidean distances between points (i) and (i+1)
    #    cost = (((ordered[:-1] - ordered[1:])**2).sum(1)).sum()
    #    if cost < mindist:
    #        mindist = cost
    #        minidx = i

    #opt_order = paths[minidx]

    #xx = x[opt_order]
    #yy = y[opt_order]

    #print(xx)
    #print(yy)

    #plt.plot(xx, yy)
    #plt.show()


    if debug == True: cv.imshow('output', output)    

    return urejenSeznam