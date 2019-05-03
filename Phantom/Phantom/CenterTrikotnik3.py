import numpy as np

# Tisto s pravimi koti cez ogljisca

def VrniCenter(tocke):
	return f(tocke[0, 0], tocke[0, 1], tocke[1, 0], tocke[1, 1], tocke[2, 0], tocke[2, 1])

def h(a,A,b,B,c,C):
 if A==B:b,B,c,C=c,C,b,B
 m=(a-b)/(B-A)
 return m,C-m*c
def f(a,A,b,B,c,C):
 m,q=h(a,A,b,B,c,C)
 k,z=h(c,C,b,B,a,A)
 x=(q-z)/(k-m)
 return (x,k*x+z)

