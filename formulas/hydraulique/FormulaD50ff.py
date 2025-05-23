import math

class FormulaD50ff:
    def __init__(self):
        self.type_sol = None
        self.pores_sol = None
        self.compress_sol = None
        self.density_sol = None
        self.σv = None
        self.E0 = None
        self.Ei = None
        self.σ0 = None
        self.kv0 = None
        self.Cc = None
        self.Ck = None
        self.result = None

    def calculate(self, clay, water, compression, density, pore_style, Ei=None, Cc=None, Ck=None):
        self.type_sol = clay
        self.pores_sol = water
        self.compress_sol = self.σv = compression
        self.density_sol = density
        self.Ei = Ei
        self.Cc = Cc
        self.Ck = Ck

        try:
            if self.Ei == None:
                if pore_style == "W":
                    self.formula13a()
                elif pore_style == "ρf":
                    self.formula13b()
                elif pore_style == "ef*":
                    self.formula13c()
            self.formula12()
            self.formula14()
            self.formula15()
            if self.Cc == None:
                self.formula16()
            if self.Ck == None:
                self.formula17()
            self.formula11()
        except (ZeroDivisionError, OverflowError) as e:
            raise e

        return (self.result, self.Ei, self.Cc, self.Ck, self.E0, self.σ0, self.kv0, self.σv)

    def formula11(self):
        exponent = -(self.Cc / self.Ck)
        base = self.σv/self.σ0
        self.result = self.kv0 * base ** exponent
    def formula12(self):
        numerator = ((-0.074 * self.type_sol + 0.014) * math.log10(self.Ei) - 0.028 * self.type_sol - 0.096)
        denominator = 0.30
        exponent = numerator / denominator
        self.E0 = 10 ** exponent

    def formula13a(self):
        self.Ei = 0.01 * self.pores_sol * self.density_sol

    def formula13b(self):
        numerator = self.density_sol - self.pores_sol
        denominator = self.pores_sol - 0.9174
        self.Ei = numerator / denominator

    def formula13c(self):
        self.Ei = self.pores_sol / 1.09

    def formula14(self):
        numerator = self.E0 + 0.25 * math.log10(self.type_sol) - 0.45
        denominator = 0.02 * math.log10(self.type_sol) - 0.06
        exponent = numerator / denominator
        self.σ0 = 2.2 * math.exp(exponent)  #modifier de 2 à 2.2

    def formula15(self):
        exponent = 3.1 * math.log10(self.type_sol) + (2.02 * math.log10(self.type_sol) + 23.6) * self.E0
        self.kv0 = 2.1 * 2.2 * (10 ** (-10)) * math.exp(exponent) #ajout du 2.1 

    def formula16(self):
        self.Cc = 0.74 * math.log10(self.E0) + 0.22

    def formula17(self):
        self.Ck = 0.30 * math.log10(self.E0) + 0.12