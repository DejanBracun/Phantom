from time import time as Cas
from time import sleep as Cakaj

class FPS:
	def __init__(self):
		self.Zacetek = None
		self.Stevec = 0
		self.IntervalPosodobitve = 1
		self.ZadnjiFps = 0	
		self.ZeljeniSPF = None	
		self.CasPrej = None

	def NastaviIntervalPosodobitve(self, IntervalPosodobitve = 1):
		""" Nastavi na koliko sekund naj izpisuje FPS """
		self.IntervalPosodobitve = IntervalPosodobitve

	def Klici(self, Izpisi = True, KliciFunkcijo = None):
		""" Klices vedno v glavni zanki """
		if self.Zacetek is None: self.Zacetek = Cas()
		self.Stevec += 1
		Razlika = Cas() - self.Zacetek
		if Razlika > self.IntervalPosodobitve:
			self.ZadnjiFps = self.Stevec / Razlika
			self.Stevec = 0
			self.Zacetek = Cas()
			if Izpisi:
				print("FPS: %.2f" % self.ZadnjiFps)
				if callable(KliciFunkcijo):
					KliciFunkcijo(self.ZadnjiFps)
		if self.CasPrej is None:
			self.CasPrej = Cas()
		else:
			Razlika = Cas() - self.CasPrej
			if self.ZeljeniSPF is not None and Razlika < self.ZeljeniSPF :
				Cakaj(self.ZeljeniSPF - Razlika)
			self.CasPrej = Cas()

	def VrniFps(self):
		""" Vrne zadnji izracunani fps """
		return self.ZadnjiFps

	def NastaviZeljeniFPS(self, FPS):
		""" Nastaviš kako hitro zeliš, da se zanka izvaja """
		if FPS is None:
			self.ZeljeniSPF = None
		elif FPS > 0:
			self.ZeljeniSPF = 1 / FPS
		else:
			self.ZeljeniSPF = None



#from time import time as Cas

#__Zacetek = Cas()
#__Stevec = 0
#__IntervalPosodobitve = 1
#__ZadnjiFps = 0

#def NastaviIntervalPosodobitve(IntervalPosodobitve = 1):
#    """ Nastavi na koliko sekund naj izpisuje FPS """
#    __IntervalPosodobitve = IntervalPosodobitve

#def Klici(Izpisi = True, KliciFunkcijo = None):
#    """ Klices vedno v glavni zanki """
#    global __Zacetek, __Stevec, __ZadnjiFps
#    __Stevec += 1
#    Razlika = Cas() - __Zacetek
#    if Razlika > __IntervalPosodobitve:
#        __ZadnjiFps = __Stevec / Razlika
#        __Stevec = 0
#        __Zacetek = Cas()
#        if Izpisi:
#            print("FPS: %.2f" % __ZadnjiFps)
#        if callable(KliciFunkcijo):
#            KliciFunkcijo(__ZadnjiFps)
    
#def VrniFps():
#    """ Vrne zadnji izracunani fps """
#    return __ZadnjiFps