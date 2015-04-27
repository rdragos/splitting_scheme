import cerealizer
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import sys
import os

""" computes some plots between generated shares """

def main():

    #ROL - Params:
    #   share1_path, share2_path, share3_path = 3 files to share;
    #   rng = max range for plot
    if len(sys.argv) != 5:
        print("Incorrect args")
        print("Usage python diff.py share1_path share2_path share3_path range")
        return 0
    
    pic1_path = sys.argv[1]
    l1 = cerealizer.load(open(pic1_path, "rb"))

    pic2_path = sys.argv[2]
    l2 = cerealizer.load(open(pic2_path, "rb"))

    pic3_path = sys.argv[3]
    l3 = cerealizer.load(open(pic3_path, "rb"))

    rng = int(sys.argv[4])

    lim = min(len(l1[0]),len(l2[0]),len(l3[0]),rng)
    x = np.arange(0, lim, 1)

    for ptp in range(1,5):
        fig = plt.figure()
        fig.patch.set_facecolor('white')
        fig.subplots_adjust(hspace=.5)        
        #fig.suptitle("Database " + str(ptp + 1), fontsize=15)
        fig1 = fig.add_subplot(311)
        fig1.set_title("Europass Curriculum Vitae - BG", fontsize=11)
        plt.scatter(x, l1[ptp][:lim], c="0", marker = 'o', s=1)
        #plt.plot(x,l1[ptp][:lim])
        fig2 = fig.add_subplot(312)
        fig2.set_title("Europass Curriculum Vitae - DK", fontsize=11)
        plt.scatter(x, l2[ptp][:lim], c="0", marker = 'o', s=1)
        #plt.plot(x,l2[ptp][:lim])
        fig3 = fig.add_subplot(313)
        fig3.set_title("Europass Mobility - RO", fontsize=11)
        plt.scatter(x, l3[ptp][:lim], c="0", marker = 'o', s=1)
        #plt.plot(x,l2[ptp][:lim])
        print("finished with database" + str(ptp))    

    plt.show()
if __name__=="__main__":
    main()
