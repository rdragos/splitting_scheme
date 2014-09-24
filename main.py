import logging
import numpy

logging.basicConfig(filename='example.log',level=logging.DEBUG)

class splittingScheme(object):

    def __init__(self, ptp_number, threshold, block_size, file_path):
        """block_size should be a multiple of the threshold"""

        if block_size % threshold:
            print("Please give a block_size divisible by threshold")
            return ;
        self.ptp_number = ptp_number
        self.threshold = threshold
        self.block_size = block_size
        self.file_path = file_path

        self.person = list()
        self.poly = list()
        for k in range(self.threshold):
            self.person.append(list())
            self.poly.append(list())


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
        for blockl in self.allblocks:
            for i in range(0, len(blockl), self.threshold):
                lb = [blockl[k] for k in range(i, i + self.threshold)]

                #debugging purposes
                logging.debug(lb)
                lb = numpy.polynomial.Polynomial(lb)

                for k in range(0, self.threshold):
                    self.person[k].append(lb(k))
                    self.poly[k].append(lb)
        """
        import pdb; pdb.set_trace()
        """

    def process_threshold_scheme(self):
        self.split_into_blocks()
        self.pad_allblocks()
        self.give_shares()


    def debug(self):
        print(self.allblocks)

def main():

    nr_party = 10
    sz_threshold = 2
    block_size = 4
    file_path = "/home/dragos/open-source/splitting_scheme/test.in"
    s = splittingScheme(nr_party, sz_threshold, block_size, file_path)
    s.process_threshold_scheme()
    s.debug()

if __name__ == "__main__":
    main()
