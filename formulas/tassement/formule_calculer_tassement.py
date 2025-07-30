class CalculTassements:
    def __init__(self, ei_star: float, e0_star: float, e_final: float):
        self.ei_star = ei_star
        self.e0_star = e0_star
        self.e_final = e_final

    def calculer(self):
        if self.ei_star + 1 == 0:
            raise ValueError("Division by zero is not allowed in the settlement calculation.")

        s1 = (self.ei_star * 1.09 - self.ei_star) / (1 + self.ei_star * 1.09) * 100
        s2 = (self.ei_star - self.e0_star) / (1 + 1.09 * self.ei_star) * 100
        s3 = (self.e0_star - self.e_final) / (1 + 1.09 * self.ei_star) * 100
        s_total = s1 + s2 + s3

        return s1, s2, s3, s_total
