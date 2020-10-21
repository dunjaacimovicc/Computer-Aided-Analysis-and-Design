import numpy as np

class Matrica:
    
    
#    - INCIJALIZACIJA -
    
    def __init__ (self, br_red, br_stup, identity = False, elementi = None):
        self.br_red = br_red
        self.br_stup = br_stup
        self.epsilon = 1e-7
        
        if elementi is None :
            self.elementi = np.zeros((br_red, br_stup))
        else:
            self.elementi = np.array(elementi)
        
        if identity == True:
            for i in range(br_red):
                self.elementi[i][i] = 1.0
    
    
#    - ADD, SUB, MUL AND DIV -

    def __add__(self, other):
        result = Matrica(self.br_red, self.br_stup, False)
        for i in range(self.br_red):
            z = list(zip(self.elementi[i], other.elementi[i]))
            m = list(map(sum, z))
            result.elementi[i] = m
        return result
    
    def __sub__(self, other):
        result = Matrica(self.br_red, self.br_stup, False)
        for i in range(self.br_red):
            z = list(zip(self.elementi[i], other.elementi[i]))
            m = [pair[0] - pair[1] for pair in z]
            result.elementi[i] = m
        return result
    
    def __mul__(self, other):
        t = type(other)
        if (t == int or t == float):
            result = Matrica(self.br_red, self.br_stup, False)
            for i in range(self.br_red):
                m = [x * other for x in self.elementi[i]]
                result.elementi[i] = m
            return result
        else:
            result = Matrica(self.br_red, other.br_stup, False)
            for i in range(self.br_red):
                resultRow = []
                for j in range(other.br_stup):
                    stupac = other.dohvati_stupac(j)
                    z = list(zip(self.elementi[i], stupac))
                    m = [pair[0]*pair[1] for pair in z]
                    resultRow.append(sum(m))
                result.elementi[i] = resultRow
        return result
    
    def __div__(self, other):
        result = Matrica(self.br_red, self.br_stup, False)
        for i in range(self.br_red):
            m = [x / other for x in self.elementi[i]]
            result.elementi[i] = m
        return result
    
    def __iadd__(self, other):
        return self + other
        
    def __isub__(self, other):
        return self - other
    
    def __imul__(self, other):
        return self * other
    
    def __idiv__(self, other):
        return self / other
        
#    - OSTALE OVERLOADANE METODE -

    def __eq__(self, other):
        if self.br_red != other.br_red or self.br_stup != other.br_stup: return False
        for i in range(self.br_red):
            for j in range(self.br_stup):
                if abs(self.elementi[i][j] - other.elementi[i][j]) > self.epsilon: return False
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __str__(self):
        return f'{self.elementi}'
        
    def __invert__(self):
        if abs(self.det()) < self.epsilon:
            raise Exception("Determinanta je nula, ova matrica nema inverz.")
            return
        
        jedinicna_matrica = Matrica(self.br_red, self.br_stup, True)
        inverz_matrice = Matrica(self.br_red, self.br_stup)
        
        for i in range(self.br_red):
            stupac = jedinicna_matrica.dohvati_stupac(i)
            konstante = [[x] for x in stupac]
                
            vektor_konstanti = Matrica(self.br_red, 1, False, konstante)
            stupac_inverza = self.rijesi_jednadzbu(vektor_konstanti)
            
            if stupac_inverza is None:
                raise Exception("Matrica nema inverz.")
                return
            else:
                inverz_matrice.postavi_stupac(i, stupac_inverza.elementi)
        
        return inverz_matrice
                    
       
#    - OSTALE METODE -
            
    def transponiraj(self):
        result = Matrica(self.br_red, self.br_stup, False)
        for i in range(self.br_red):
            for j in range(self.br_stup):
                result.elementi[i][j] = self.elementi[j][i]
        return result
        
    def det(self):
        permutacije, br_permutacija = self.lup_dekompozicija()
        det = self.elementi[0][0]
        for i in range(1, self.br_red):
            det *= self.elementi[i][i]
        
        if (br_permutacija - self.br_red) % 2 == 0:
            det *= 1
        else:
            det *= -1
        
        if abs(det) < self.epsilon: return 0
        else: return det
    
    
    def U(self):
        u = Matrica(br_red, br_stup, False)
        
        for i in range(self.br_red):
            for j in range(self.br_stup):
                if i <= j:
                    u.elementi[i][j] = self.elementi[i][j]
                else:
                    u.elementi[i][j] = 0.0
        
    def L(self):
        l = Matrica(br_red, br_stup, False)
        
        for i in range(self.br_red):
            for j in range(self.br_stup):
                if i > j:
                    u.elementi[i][j] = self.elementi[i][j]
                elif i == j:
                    u.elementi[i][j] = 1.0
                else:
                    u.elementi[i][j] = 0.0
    
    def prosirena_matrica(self, vektor):
        prosirena_matrica = Matrica(br_red, br_stup+1)
        for i in range(br_stup):
            prosirena_matrica.elementi[i] = self.elementi[i] + vektor.elementi[i]
        return prosirena_matrica
    
    def copy(self):
        return Matrica(self.br_red, self.br_stup, self.elementi.deepCopy())
        
    
#    - STUPCI -
    
    def dohvati_stupac(self, i):
        return [self.elementi[j][i] for j in range(self.br_red)]
    
    def postavi_stupac(self, stupac, novi_elementi):
        for i in range(self.br_red):
            self.elementi[i][stupac] = novi_elementi[i]
    
    def zamjeni_stupce(self, i, j):
        temp = self.dohvati_stupac(i)
        self.postavi_stupac(i, self.dohvati_stupac(j))
        self.postavi_stupac(j, temp)
    
        
#    - SUPSTITUCIJA -
    
    def supst_unaprijed(self, b):
        y = b.elementi.copy()
        for i in range(self.br_red-1):
            for j in range(i+1, self.br_red):
                y[j][0] -= self.elementi[j][i] * y[i][0]
        return Matrica(b.br_red, 1, False, y)
    
    def supst_unazad(self, y):
        x = y.elementi.copy()
        for i in reversed(range(self.br_red)):
            if abs(self.elementi[i][i]) <= self.epsilon:
                raise Exception("Dijeljenje s nulom.")
            x[i] = x[i] / self.elementi[i][i]
            if(i <= 0): break
            for j in range(i):
                x[j][0] -= self.elementi[j][i] * x[i][0]
        return Matrica(y.br_red, 1, False, x)
    
    
#    - DEKOMPOZICIJA -
    
    def lu_dekompozicija(self):
        matrica = self
        for i in range(matrica.br_red-1):
            for j in range(i+1, self.br_red):
                if abs(matrica.elementi[i][i]) <= self.epsilon:
                    raise Exception("Pivot je nula.")
                    
                matrica.elementi[j][i] = matrica.elementi[j][i] / matrica.elementi[i][i]
                
                for k in range (i+1, matrica.br_stup):
                    matrica.elementi[j][k] -= matrica.elementi[j][i] * matrica.elementi[i][k]
        
    def lup_dekompozicija(self):
        matrica = self
        p = np.array(range(matrica.br_red))
        br_permutacija = matrica.br_red

        for i in range(matrica.br_red-1):
            pivot = i
            for j in range(i+1, matrica.br_red):
                if(abs(matrica.elementi[j][i]) > abs(matrica.elementi[pivot][i])):
                    pivot = j

            if pivot != i:
                p[i], p[pivot] = p[pivot], p[i]
#                print(matrica)
                temp = matrica.elementi[i].copy()
                matrica.elementi[i] = matrica.elementi[pivot].copy()
                matrica.elementi[pivot] = temp
#                print(matrica)
                br_permutacija += 1
        
            for j in range(i+1, self.br_red):
                if abs(matrica.elementi[i][i]) <= self.epsilon:
                    raise Exception("Pivot je nula.")
                
#                print(matrica.elementi[j][i], matrica.elementi[i][i])
                matrica.elementi[j][i] /= matrica.elementi[i][i]
                for k in range(i+1, self.br_stup):
#                    print(matrica.elementi[j][i], matrica.elementi[i][k])
                    matrica.elementi[j][k] -= matrica.elementi[j][i] * matrica.elementi[i][k]
#                    print(matrica.elementi[j][k])
#                    print(matrica)
                
            self.elementi = np.around(self.elementi, 2)
                    
        permutacijska_matrica = self.stvoriPermutacijskuMatricu(p)
#        print(p, permutacijska_matrica)
        return permutacijska_matrica, br_permutacija
    
    def stvoriPermutacijskuMatricu(self, pivoti):
        elem = []
        br_pivota = len(pivoti)
        
        for i in pivoti:
            redak = np.zeros(br_pivota)
            redak[i] = 1.0
            elem.append(redak)
        
        return Matrica(br_pivota, br_pivota, False, elem)

    def rijesi_jednadzbu(self, vektor_konstanti, lup = True, rounded = True):
        
        if lup:
            try:
                permutacijska_matrica, br_permutacija = self.lup_dekompozicija()
                vektor = permutacijska_matrica * vektor_konstanti
            except Exception as e:
                print("Dekompozicija matrice nije bila moguca. " + str(e))
                return
        
        else:
            try:
                self.lu_dekompozicija()
                vektor = vektor_konstanti
            except Exception as e:
                print("Dekompozicija matrice nije bila moguca: " + str(e))
                return
                
        z = self.supst_unaprijed(vektor)
        y = self.supst_unazad(z)
        
        if rounded:  y.elementi = np.around(y.elementi,2)
        return y

#    - CITANJE I PISANJE U DATOTEKE -

    @staticmethod
    def citaj_iz(datoteka):
        ulaz = open("zadatci/" + datoteka, "r")
        redovi = ulaz.readlines()
        ulaz.close()
        
        if redovi == []:
            print("Datoteka " + datoteka + " je prazna.")
            return

        br_red = len(redovi)
        br_stup = len(redovi[0].strip().split())
        elem = []

        for red in redovi:
            e = [float(x) for x in red.strip().split()]
            elem.append(e)

        return Matrica(br_red, br_stup, False, elem)
    
    def pisi_u(self, datoteka):
        izlaz = open("zadatci/" + datoteka, "w")
        redovi = ""
        for i in range(self.br_red):
            for j in range(self.br_red):
                redovi += str(self.elementi[i][j]) + " "
            redovi += "\n"
        izlaz.write(redovi)
        izlaz.close()
