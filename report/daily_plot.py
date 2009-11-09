import numpy as np
import matplotlib.pyplot as plt
import pickle
import sys
import datetime

if __name__ == "__main__":
    filename = sys.argv[1]

    pkl_file = open(filename, 'rb')
    time_slots = pickle.load(pkl_file)
    data = pickle.load(pkl_file)
    pkl_file.close()


    times = []
    cpt = 0
    for time_slot in time_slots:
        if(cpt % 4 == 0):
            times.append(time_slot.strftime("%H%M"))
        cpt = cpt + 1

    plt.bar(np.arange(len(data)),data,alpha = 0.75)

    plt.xlabel('Time')
    plt.ylabel('Missing files')
    plt.title(filename)
    plt.grid(True)
    plt.xlim(0,len(data))
    plt.xticks(np.arange(len(data)/4)*4,times,rotation = 45)
    plt.show()
