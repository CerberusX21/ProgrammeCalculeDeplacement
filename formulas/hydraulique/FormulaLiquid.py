import math

class FormulaLiquid:
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
                if pore_style == "W":
                    self.formula13a()
                elif pore_style == "ρf":
                    self.formula13b()
                elif pore_style == "ef*":
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
        numerator = ((0.0035 * self.type_sol - 0.018) * math.log10(self.ei) + 0.0019 * self.type_sol - 0.099)
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
        numerator = self.e0 - 0.014 * self.type_sol - 0.42
        denominator = -0.0014 * self.type_sol - 0.012
        exponent = numerator / denominator
        self.sigma_0 = 2 * math.exp(exponent)

    def formula15(self):
        exponent = -0.25 * self.type_sol + (0.08 * self.type_sol + 12.85) * self.e0
        self.kv0 = 1.3 * (10 ** (-8)) * math.exp(exponent)

    def formula16(self):
        self.cc = 0.74 * math.log10(self.e0) + 0.22

    def formula17(self):
        self.ck = 0.30 * math.log10(self.e0) + 0.12