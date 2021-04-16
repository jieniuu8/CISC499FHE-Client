class FHE_Polynomial:

    def __init__(self,*coeffs):
        self.coefficients = list(coeffs)

    def __repr__(self):
        return "Polynomial" + str(tuple(self.coefficients))

    def getCoefficients(self):
        return self.coefficients # return as list

    def __str__(self):
        def x_expr(deg):
            if deg == 0:
                res = ""
            if deg ==1:
                res = "x"
            else:
                res = "x^"+str(deg)
            return res

        deg = len(self.coefficients) - 1
        res = ""

        for i in range(0,deg+1):
            coeff = self.coefficients[i]

            if deg-i != 0:
                if abs(coeff) == 1:
                    if coeff < 0:
                        res += "-x^"+str(deg-i)
                    else:
                        res += "+x^"+str(deg-i)
                elif coeff != 0:
                    if coeff < 0:
                        res += "-" + str(abs(coeff)) + "x^" + str(deg-i)
                    else:
                        res += "+" + str(abs(coeff)) + "x^" + str(deg-i)
            else:
                if coeff != 0:
                    if coeff > 0:
                        res += "+" + str(coeff)
                    else:
                        res += "-" + str(abs(coeff))
        return res.lstrip('+')

    def __call__(self,x):
        res = 0
        for index, coeff in enumerate(self.coefficients[::-1]):
            res += coeff * x**index
        return res
