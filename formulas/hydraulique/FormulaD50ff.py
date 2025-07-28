import math

class FormulaD50ff:
    def __init__(self):
        self.type_sol = None
        self.pores_sol = None
        self.compress_sol = None
        self.density_sol = None
        self.sigma_v = None
        self.e0 = None
        self.ei = None
        self.sigma_0 = None
        self.kv0 = None
        self.cc = None
        self.ck = None
        self.result = None

    def calculate(self, clay, water, compression, density, pore_style, ei=None, cc=None, ck=None):
        self.type_sol = clay
        self.pores_sol = water
        self.compress_sol = self.sigma_v = compression
        self.density_sol = density
        self.ei = ei
        self.cc = cc
        self.ck = ck

        try:
            if self.ei is None:
                if pore_style == "Initial water content":
                    self.formula13a()
                elif pore_style == "Frozen bulk density":
                    self.formula13b()
                elif pore_style == "Frozen void ratio":
                    self.formula13c()
            self.formula12()
            self.formula14()
            self.formula15()
            if self.cc is None:
                self.formula16()
            if self.ck is None:
                self.formula17()
            self.formula11()
        except (ZeroDivisionError, OverflowError) as e:
            raise e

        return self.result, self.ei, self.cc, self.ck, self.e0, self.sigma_0, self.kv0, self.sigma_v

    def formula11(self):
        exponent = -(self.cc / self.ck)
        base = self.sigma_v / self.sigma_0
        self.result = self.kv0 * base ** exponent
    def formula12(self):
        numerator = (
                (-0.074 * math.log10(self.type_sol) + 0.014) * math.log10(self.ei)
                - 0.028 * math.log10(self.type_sol)
                - 0.096
        )
        denominator = 0.30
        exponent = numerator / denominator
        self.e0 = 10 ** exponent

    def formula13a(self):
        self.ei = 0.01 * self.pores_sol * self.density_sol

    def formula13b(self):
        numerator = self.density_sol - self.pores_sol
        denominator = self.pores_sol - 0.9174
        self.ei = numerator / denominator

    def formula13c(self):
        self.ei = self.pores_sol / 1.09

    def formula14(self):
        numerator = self.e0 + 0.25 * math.log10(self.type_sol) - 0.45
        denominator = 0.02 * math.log10(self.type_sol) - 0.06
        exponent = numerator / denominator
        sigma_0 = 0.9 * math.exp(exponent)
        if sigma_0 > 50:
            self.sigma_0 = 50
        else:
            self.sigma_0 = sigma_0

    def formula15(self):
        exponent = 3.1 * math.log10(self.type_sol) + (2.02 * math.log10(self.type_sol) + 23.6) * self.e0
        self.kv0 = 1.3 * 2.2 * (10 ** (-10)) * math.exp(exponent)

    def formula16(self):
        self.cc = 0.74 * math.log10(self.e0) + 0.22

    def formula17(self):
        self.ck = 0.30 * math.log10(self.e0) + 0.12