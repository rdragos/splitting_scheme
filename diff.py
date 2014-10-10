import cerealizer
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import sys
import os

""" computes some plots between generated shares """

def main():

    if len(sys.argv) != 3:
        print("Incorrect args")
        print("Usage python diff.py share1_path share2_path")
        return 0
    pic1_path = sys.argv[1]
    pic2_path = sys.argv[2]
    l1 = cerealizer.load(open(pic1_path, "rb"))
    l2 = cerealizer.load(open(pic2_path, "rb"))

    lim = len(l1[0])
    x = np.arange(0, lim, 1)

    print(len(l1))
    print(len(l2))

    for ptp in range(len(l1)):
        fig = plt.figure()
        fig.suptitle("Person " + str(ptp), fontsize=20)
        plt.subplot(211)
        plt.scatter(x, l1[ptp][:lim], s=20, c='b')
        plt.subplot(212)
        plt.scatter(x, l2[ptp][:lim], s=20, c='r')

        print("finished with " + str(ptp))

    plt.show()
if __name__=="__main__":
    main()
