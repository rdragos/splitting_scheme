import cerealizer
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import sys
import os

""" computes some plots between generated shares """

def main():

    #ROL - Params:
    #   share1_path = 1 file to share;
    #   rng = max range for plot
    if len(sys.argv) != 3:
        print("Incorrect args")
        print("Usage python diff.py share1_path range")
        return 0
    
    pic1_path = sys.argv[1]
    l1 = cerealizer.load(open(pic1_path, "rb"))

    rng = int(sys.argv[2])

    lim = min(len(l1[0]),rng)
    x = np.arange(0, lim, 1)
    

    for ptp in range(1,5):
        fig = plt.figure()        
        fig.patch.set_facecolor('white')
        fig.subplots_adjust(hspace=0.5)
               
        #fig.suptitle("Database " + str(ptp + 1), fontsize=15)
        fig1 = fig.add_subplot(311)                
        fig1.axis([-50, rng+50, -50, 300])
        fig1.set_aspect(2)
        plt.scatter(x, l1[ptp][:lim], c="0", marker = 'o', s=1)
        print("finished with database" + str(ptp))
        plt.savefig('new_version\db'+str(ptp)+'.png', format='png', dpi=300)

    plt.show()
if __name__=="__main__":
    main()
