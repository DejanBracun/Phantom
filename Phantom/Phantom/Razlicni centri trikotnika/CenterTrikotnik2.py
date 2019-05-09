import numpy as np

# Stranico na pol in nato crto do ogljisca

def VrniCenter(tocke):
	
	#tocke = np.array([[1, 2], [2, 6], [3, -4]])

	a = tocke[0][0]
	b = tocke[0][1]
	c = tocke[1][0]
	d = tocke[1][1]
	e = tocke[2][0]
	f = tocke[2][1]

	g = +a + +c
	h = g / 2
	i = +b + +d
	j = i / 2
	k = d - b
	l = c - a
	if (0 != k and 0 != l):
		m = k / l
		n = -1 / m
		o = j - n * h

	q = +e + +c
	r = q / 2
	s = +f + +d
	t = s / 2
	u = f - d
	v = e - c
	if (0 != u and 0 != v):
		w = u / v
		x = -1 / w
		y = t - x * r

	z = +e + +a
	A = z / 2
	B = +f + +b
	C = B / 2
	D = f - b
	E = e - a
	if (0 != D and 0 != E):
		F = D / E
		G = -1 / F
		H = C - G * A

	if (0 != k and 0 != l and 0 != u and 0 != v and 0 != D and 0 != E):
		I = -x
		J = -y
		K = I + n
		L = o + J
		M = L / K
		N = -M
		O = x * N + y
	elif (0 != k and 0 != l and 0 != u and 0 != v):
		I = -x
		J = -y
		K = I + n
		L = o + J
		M = L / K
		N = -M
		O = x * N + y
	elif (0 != u and 0 != v and 0 != D and 0 != E):
		P = -G
		Q = -H
		R = P + x
		S = y + Q
		M = S / R
		N = -M
		O = G * N + H
	elif (0 != k and 0 != l and 0 != D and 0 != E):
		P = -n
		Q = -o
		R = P + G
		S = H + Q
		M = S / R
		N = -M
		O = n * N + o

	return np.array([N, O])