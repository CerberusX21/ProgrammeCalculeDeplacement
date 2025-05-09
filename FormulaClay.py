import math

class FormulaClay:
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

    def calculate(self, clay, water, compression, density, is_water):

        self.type_sol = clay
        self.pores_sol = water
        self.compress_sol = compression
        self.density_sol = density


        try:
            if is_water:
                self.formula13a()
            else:
                self.formula13b()
            self.formula12()
            self.formula14()
            self.formula15()
            self.formula16()
            self.formula17()
            self.formula11()
        except (ZeroDivisionError, OverflowError) as e:
            raise e

        return self.result

    def formula11(self):
            exponent = -(self.r16/self.r17)
            base = self.density_sol/self.r14
            self.result = self.r15*base**exponent

    def formula12(self):
        numerator = ((0.0018 * self.type_sol - 0.099) * math.log10(self.r13) + 0.0007 * self.type_sol - 0.053)
        denominator = 0.30
        exponent = numerator / denominator
        self.r12 = 10 ** exponent

    def formula13a(self):
        self.r13 = 0.01*self.pores_sol*self.density_sol

    def formula13b(self):
        numerator = self.density_sol - self.pores_sol
        denominator = self.pores_sol - 0.9174
        self.r13 = numerator / denominator

    def formula14(self):
        numerator = self.r12 - 0.0049 * self.type_sol -0.82
        denominator = -0.00063 * self.type_sol - 0.06
        exponent = numerator / denominator
        self.r14 = 2 * math.exp(exponent)

    def formula15(self):
        exponent = -0.077 * self.type_sol + (-0.05 * self.type_sol + 20.5) * self.r12
        self.r15 = 1.1 * (10 ** (-12)) * math.exp(exponent)

    def formula16(self):
        self.r16 = 0.74 * math.log(self.r12) + 0.22

    def formula17(self):
        self.r17 = 0.30 * math.log(self.r12) + 0.12

