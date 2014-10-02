#!/usr/local/bin/python

import logging
import numpy
import sys
logging.basicConfig(filename='example.log',level=logging.DEBUG)


from functools import reduce

class GaloisField(object):

    # constants used in the multGF2 function
    
    def __init__(self, degree, irPoly):

        """Define parameters of binary finite field GF(2^m)/g(x)
           - degree: extension degree of binary field
           - irPoly: coefficients of irreducible polynomial g(x)
        """
        def i2P(sInt):
            """Convert an integer into a polynomial"""
            return [(sInt >> i) & 1
                    for i in reversed(range(sInt.bit_length()))]    
        
        self.mask1 = self.mask2 = 1 << degree
        self.mask2 -= 1
        self.polyred = reduce(lambda x, y: (x << 1) + y, i2P(irPoly)[1:])
            
    def multGF2(self, p1, p2):
        """Multiply two polynomials in GF(2^m)/g(x)"""
        p = 0
        while p2:
            if p2 & 1:
                p ^= p1
            p1 <<= 1
            if p1 & self.mask1:
                p1 ^= self.polyred
            p2 >>= 1
        return p & self.mask2
    def addGF2(self, p1, p2):
        """Add two polynomials in GF(2^m)/g(x)"""
        res = 0
        for i in range(8):
            b1 = (p1 >> i) & 1
            b2 = (p2 >> i) & 1

            res ^= ((b1 ^ b2) << i)
        return res
    def lgputGF2(self, a, b):
        #raise a ^ b mod g(x)
        res = 1
        while b > 0:
            if b & 1:
                res = self.multGF2(res, a)
            a = self.multGF2(a, a)
            b >>= 1
        return res
    def polymulGF2(self, a, b):
        #sorry, no FFT goes here
        if type(a) is int:
            a = [a]
        if type(b) is int:
            b = [b]
        # (x^2 + x + 1) (x^3 + x)
        mul_res = [0 for x in range(len(a) + len(b))]
        for idx_a in range(len(a)):
            for idx_b in range(len(b)):
                toAdd = self.multGF2(a[idx_a], b[idx_b])
                degree_sum = idx_a + idx_b
                mul_res[degree_sum] = self.addGF2(mul_res[degree_sum], toAdd)

        #erasing last coeff if 0
        while len(mul_res) > 1 and mul_res[-1] == 0:
            mul_res = mul_res[0:len(mul_res) - 1]
        return mul_res

    def polyaddGF2(self, a, b):
        if type(a) is int:
            a = [a]
        if type(b) is int:
            b = [b]

        copy1 = a
        copy2 = b
        if len(b) > len(a):
            copy1 = b
            copy2 = a

        while len(copy1) != len(copy2):
            copy2.append(0)
        res = [0 for x in range(len(copy1))]
        for idx in range(len(copy1)):
            res[idx] = self.addGF2(copy1[idx], copy2[idx])

        return res

class SplittingScheme(object):

    def __init__(self, ptp_number, threshold, block_size, file_path):
        """ 
            block_size should be a multiple of the threshold
            TODO: get a larger prime number
        """

        if block_size % threshold:
            raise Exception("block_not divisible by threshold")

        self.ptp_number = ptp_number
        self.threshold = threshold
        self.block_size = block_size
        self.file_path = file_path

        self.person = list()
        self.poly = list()
        for k in range(self.ptp_number):
            self.person.append(list())
            self.poly.append(list())

        self.big_prime = 169743212279
        self.field = GaloisField(8, 0b100011011)

    def loadInv(self):
        """keeping the inverses for each polynome"""
        
        self.invTable = [0 for i in range(256)]

        with open("invtable.out", "r") as f:
            line = f.readline().split(" ")
            print(line)
            for i in range(255):
                self.invTable[i + 1] = int(line[i], 16)

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
        print("last block: " + str(len(last_block)) + " standard block: " + str(self.block_size))
        if len(last_block) != self.block_size:
            remaining = self.block_size - len(last_block) - 1
            self.allblocks[-1].append(128)
            while remaining > 0:
                self.allblocks[-1].append(0)
                remaining -= 1;
        """
        for idx_block in range(len(self.allblocks)):
            print("block with index: " + str(idx_block) + " has value: " + str(self.allblocks[idx_block]))
        """

    def evalC(self, coefs, point):
        """
        Evaluate poly formed by 'coefs' with point
        """
        F = self.field
        summation = 0 
        for idx_coef in range(len(coefs)):
            cur_eval = F.lgputGF2(point, idx_coef)
            cur_eval = F.multGF2(coefs[idx_coef], cur_eval)
            summation = F.addGF2(summation, cur_eval)
        return summation

    def give_shares(self):
        """
            self.poly[i] is the list of polynomials for person i
            self.person[k][i] contains the evaluated polynomial self.poly[i][k] at point i
        """
        F = self.field
        for blockl in self.allblocks:
            #take |threshold| blocks and make a polynome
            for i in range(0, len(blockl), self.threshold):
                raw_coefs = blockl[i: i + self.threshold]
                for ptp in range(self.ptp_number):
                    summation = self.evalC(raw_coefs, ptp)
                    self.person[ptp].append(summation)
                    self.poly[ptp].append(raw_coefs)

    def interpolate_shares(self, pts):
        #init the poly_sum with bunch of zeros
        sum_poly = [0 for i in range(self.threshold)]
        """
            Lagrange interpolation: yi * (x - xj) / (xi - xj), i != j
            Intuition: check what happens when you replace x with xi
        """
        F = self.field

        for i in range(len(pts)):
            p = 1
            xi = pts[i][0]
            yi = pts[i][1]
            rolling = [1]
            for j in range(len(pts)):
                if i == j:
                    continue
                xj = pts[j][0]
                curInv = self.invTable[F.addGF2(xi, xj)]
                p = F.multGF2(p, curInv)
                up = [xj, 1]
                rolling = F.polymulGF2(up, rolling)

            rolling = F.polymulGF2(rolling, F.multGF2(yi, p))
            sum_poly = F.polyaddGF2(sum_poly, rolling)

        return sum_poly

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
        print(";".join(str(item) for item in self.person[0]))
        pResults = self.compute_secret([4,5,6])
        for pIdx in range(len(pResults)):
            print(str(pResults[pIdx]) + "<->" + str(self.poly[0][pIdx]))

    def dump_shares_to_file(self, output_file):
        import cerealizer
        lperson = []
        for idx_p in range(len(self.person)):
            lperson.append([int(x) for x in self.person[idx_p]])

        cerealizer.dump(lperson, open(output_file, "wb"))
    def fun(self):
        import pdb; pdb.set_trace()

def main():
    print(len(sys.argv), sys.argv[0])
    if len(sys.argv) != 6:
        """
        This tells us that the DB will split to nr_parties such that if no of parties < threshold_size
        then the secret cannot be recovered (this is the ideal case)

        Split the DB located in file_path into blocks of block_size.
        Dump the shares for each person to shares_dump_file into an array.

        Element at index 0 has the shares for the first person.
        Element at index 1 has the shares for the second person and so on
        """

        print("Usage: python main.py nr_parties threshold_size block_size file_path shares_dump_file")
        print("Example: python main.py 10 3 6 test.in shares_dump.out")
        raise Exception("Incorrect args")

    nr_party = int(sys.argv[1])
    sz_threshold = int(sys.argv[2])
    block_size = int(sys.argv[3])
    file_path = sys.argv[4]
    to_dump = sys.argv[5]


    s = SplittingScheme(nr_party, sz_threshold, block_size, file_path)
    s.loadInv()
    s.process_threshold_scheme()
    s.dump_shares_to_file(to_dump)
    #s.debug()

if __name__ == "__main__":
    main()
