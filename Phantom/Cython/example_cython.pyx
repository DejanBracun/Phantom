
import numpy as np
import cv2 as cv

cpdef vrniElipso(canny, int E11z, int E11k, int E10z, int E10k, int E21z, int E21k, int E20z, int E20k):
	print("Prileganje")
	# Prileganje
	cdef int najboljsi = 0
	
	cdef int kot_
	cdef int MA_
	cdef int ma_
	cdef int x_
	cdef int y_
	cdef int st
	
	for kot_ in range(0, 90, 10):
		for MA_ in range(E20z, E20k, 2):
			for ma_ in range(E21z, E21k, 2):
				for x_ in range(E10z, E10k, 2):
					for y_ in range(E11z, E11k, 2):
						prazna = np.full(canny.shape[0: 2], -1, dtype = np.float)
						porisana = cv.ellipse(prazna, (x_, y_), (MA_, ma_), kot_, 0, 360, 255.)
						st = np.sum(porisana == canny)
						if st > najboljsi:
							najboljsi = st
							R = np.array([x_, y_, MA_, ma_, kot_])
							print(R)
	return R