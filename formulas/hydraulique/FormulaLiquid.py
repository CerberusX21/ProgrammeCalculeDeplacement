import math

class FormulaLiquid:
    def __init__(self):
        self.type_sol = None
        self.pores_sol = None
        self.compress_sol = None
        self.density_sol = None
        self.r12 = None
        self.r13 = None
        self.r14 = None
        self.r15 = None
        self.r16 = None
        self.r17 = None
        self.result = None

    def calculate(self, clay, water, compression, density, pore_style, Ei=None, Cc=None, Ck=None):
        self.type_sol = clay
        self.pores_sol = water
        self.compress_sol = compression
        self.density_sol = density
        self.r13 = Ei
        self.r16 = Cc
        self.r17 = Ck

        try:
            if self.r13 == None:
                if pore_style == "W":
                    self.formula13a()
                elif pore_style == "ρf":
                    self.formula13b()
                elif pore_style == "ef*":
                    self.formula13c()
            self.formula12()
            self.formula14()
            self.formula15()
            if self.r16 == None:
                self.formula16()
            if self.r17 == None:
                self.formula17()
            self.formula11()
        except (ZeroDivisionError, OverflowError) as e:
            raise e

        return self.result, self.r13, self.r16, self.r17

    def formula11(self):
        exponent = -(self.r16 / self.r17)
        base = self.compress_sol / self.r14
        self.result = self.r15 * base ** exponent

    def formula12(self):
        numerator = ((0.0035 * self.type_sol - 0.018) * math.log10(self.r13) + 0.0019 * self.type_sol - 0.099)
        denominator = 0.30
        exponent = numerator / denominator
        self.r12 = 10 ** exponent

    def formula13a(self):
        self.r13 = 0.01*self.pores_sol*self.density_sol

    def formula13b(self):
        numerator = self.density_sol - self.pores_sol
        denominator = self.pores_sol - 0.9174
        self.r13 = numerator / denominator

    def formula13c(self):
        self.r13 = self.pores_sol/1.09

    def formula14(self):
        numerator = self.r12 - 0.014 * self.type_sol - 0.42
        denominator = -0.0014 * self.type_sol - 0.012
        exponent = numerator / denominator
        self.r14 = 2 * math.exp(exponent)

    def formula15(self):
        exponent = -0.25 * self.type_sol + (0.08 * self.type_sol + 12.85) * self.r12
        self.r15 = 1.3 * (10 ** (-8)) * math.exp(exponent)

    def formula16(self):
        self.r16 = 0.74 * math.log(self.r12) + 0.22

    def formula17(self):
        self.r17 = 0.30 * math.log(self.r12) + 0.12