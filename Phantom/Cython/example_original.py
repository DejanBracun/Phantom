import numpy as np

def vrniElipso(canny, E1, E2, E3):
	# Prileganje
	najboljsi = {"st": 0, "E1": E1, "E2": E2, "E3": E3}
	for kot_ in range(0, 90, 10):
		for MA_ in range(int(E2[0]), int(E2[0] * 1.1), 2):
			for ma_ in range(int(E2[1]), int(E2[1] * 1.1), 2):
				for x_ in range(E1[0] - 10, E1[0] + 10, 2):
					for y_ in range(E1[1] - 10, E1[1] + 10, 2):
						st = np.sum(cv.ellipse(np.full(canny.shape[0: 2], -1, dtype = np.float), (x_, y_), (MA_, ma_), kot_, 0, 360, 255.) == canny)
						if st > najboljsi["st"]:
							najboljsi = {"st": st, "E1": (x_, y_), "E2": (MA_, ma_), "E3": kot_}
	return najboljsi