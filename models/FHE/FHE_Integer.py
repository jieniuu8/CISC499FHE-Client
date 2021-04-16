class FHE_Integer:
    def __init__(self, x0, m0, p0):
        self.x = x0
        self.m = m0
        self.p = p0

    def encrypt(self):
        x_prime = (self.x + self.p) % self.m
        q = (self.x + self.p) // self.m
        return FHE_Integer_Enc(x_prime, q, self.m, self.p)


class FHE_Integer_Enc:
    def __init__(self, xp_0, q0, m0, p0):
        self.x_prime = xp_0
        self.q = q0
        self.m = m0
        self.p = p0

    def getContext(self):
        return self.x_prime, self.q, self.p

    def __add__(self, enc_obj):
        xp1, q1, p1 = self.getContext()
        xp2, q2, p2 = enc_obj.getContext()
        return FHE_Integer_Enc(xp1+xp2, q1+q2, self.m, p1+p2)

    def __mul__(self, enc_obj):
        xp1, q1, p1 = self.getContext()
        xp2, q2, p2 = enc_obj.getContext()
        x1 = xp1 + q1*self.m - p1
        x2 = xp2 + q2*self.m - p2
        q0 = xp1*q2 + xp2*q1 + q1*q2*self.m
        p0 = x1*p2 + x2*p1 + p1*p2
        return FHE_Integer_Enc(xp1*xp2, q0, self.m, p0)
