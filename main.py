#!/usr/local/bin/python

import logging
import numpy

logging.basicConfig(filename='example.log',level=logging.DEBUG)

class splittingScheme(object):

    def __init__(self, ptp_number, threshold, block_size, file_path):
        """block_size should be a multiple of the threshold
            TODO: get a larger prime number
        """

        if block_size % threshold:
            print("Please give a block_size divisible by threshold")
            return ;
        self.ptp_number = ptp_number
        self.threshold = threshold
        self.block_size = block_size
        self.file_path = file_path

        self.person = list()
        self.poly = list()
        for k in range(self.ptp_number):
            self.person.append(list())
            self.poly.append(list())

        self.big_prime = 10000019

    def split_into_blocks(self):
        """ read one byte at a time """

        self.allblocks = []

        with open(self.file_path, "rb") as f:
            byte = f.read(1)
            ibyte = int.from_bytes(byte, byteorder='big')
            nr_bytes = 1
            temp_block = [ibyte]

            while byte:
                if nr_bytes == self.block_size:
                    self.allblocks.append(temp_block)
                    nr_bytes = 0
                    temp_block = []

                byte = f.read(1)
                if not byte:
                    break;
                ibyte = int.from_bytes(byte, byteorder='big')

                temp_block.append(ibyte)
                nr_bytes += 1

            if len(temp_block) > 0:
                self.allblocks.append(temp_block)

    def pad_allblocks(self):
        """Using this method: 0x80 0x00 0x00 ... 0x00 """
        last_block = self.allblocks[-1]
        if len(last_block) != self.block_size:
            remaining = self.block_size - len(last_block) - 1
            self.allblocks[-1].append(128)
            while remaining > 0:
                self.allblocks[-1].append(0)
                remaining -= 1

    def give_shares(self):
        """
        self.poly[i] is the list of polynomials for person i
        self.person[k][i] contains the evaluated polynomial self.poly[i][k] at point i
        """
        for blockl in self.allblocks:
            #take |threshold| blocks and makea polynome
            for i in range(0, len(blockl), self.threshold):
                lb = [blockl[k] for k in range(i, i + self.threshold)]
                lb = numpy.polynomial.Polynomial(lb)
                for k in range(0, self.ptp_number):
                    self.person[k].append(lb(k) % self.big_prime)
                    self.poly[k].append(lb)

    def lgput(self, a, b):
        """Raise a^b in log(b) time"""
        r = 1
        while b > 0:
            if (b & 1):
                r = (r * a) % self.big_prime
            a = (a * a) % self.big_prime

            b >>= 1
        return r

    def modular_inverse(self, x):
        """compute inverse of x in GF(big_prime)"""
        return self.lgput(x, self.big_prime - 2)

    def interpolate_shares(self, pts):
        import numpy.polynomial as P
        #init the poly_sum with bunch of zeros
        sum_poly = numpy.array([0 for i in range(self.threshold)])
        """
            lagrange interpolation: yi * (x - xj) / (xi - xj)
            intuition: check what happens when you replace x with xi
        """
        for i in range(len(pts)):
            p = 1
            xi = pts[i][0]
            yi = pts[i][1]

            poly1 = numpy.polynomial.Polynomial([1])
            for j in range(len(pts)):
                if i == j:
                    continue

                xj = pts[j][0]
                p = (p * self.modular_inverse((xi - xj) % self.big_prime)) % self.big_prime
                #poly2 is down, poly1 is up
                poly2 = P.Polynomial([-xj, 1])
                poly1 = P.polynomial.polymul(poly1, poly2)[0]

            poly1 = P.polynomial.polymul(poly1, (yi * p) % self.big_prime)
            sum_poly = P.polynomial.polyadd(sum_poly, poly1)

        """
            apply the field reduction for every coefficient, I think this would be better
            if put on upper lines, but python is great on big numbers ^_^
        """
        res = numpy.array([coef % self.big_prime for coef in sum_poly[0]])
        return res

    def compute_secret(self, common_shares):
        """
            compute the polynomial by interpolating the shares holded
            by participants located at [common_shares]
        """
        secret = []
        for idx_piece in range(len(self.person[0])):
            shares = [(idx, self.person[idx][idx_piece]) for idx in common_shares]
            cur_poly = self.interpolate_shares(shares)
            secret.append(cur_poly)
        return secret

    def process_threshold_scheme(self):
        self.split_into_blocks()
        self.pad_allblocks()
        self.give_shares()

    def debug(self):
        print(self.allblocks)

def main():

    nr_party = 10
    sz_threshold = 4
    block_size = 8
    file_path = "test.in"
    s = splittingScheme(nr_party, sz_threshold, block_size, file_path)
    s.process_threshold_scheme()

    pResults = s.compute_secret([0, 1, 2, 3])

    print("computed polynomial: " + str(pResults[2]))
    print("original polynomial: " + str(s.poly[0][2]))
    print("values at: " + str(s.person[0][2]) + " " + str(s.person[1][2]))

    #just checking if computed polynomials match with the originals
    for pIdx in range(len(pResults)):
        cItem = pResults[pIdx]
        oItem = s.poly[0][pIdx].coef
        for k in range(len(cItem)):
            if cItem[k] != oItem[k]:
                print("Lol a mistake at " + str(pIdx))

    #s.debug()

if __name__ == "__main__":
    main()
