import numpy as np
import matplotlib.pyplot as plt
import os

pathair = "/work/jovillalobos/CFDFinalProject/airfoils/modified_airfoils"
airfoil = np.loadtxt(pathair+"/"+"airfoil1.txt", delimiter=",")

for i, file in enumerate(os.listdir(pathair)): 
    airfoil = np.loadtxt(pathair+"/"+file, delimiter=",")
    xmax = airfoil[:,0].max()
    xmin = airfoil[:,0].min()
    ymax = airfoil[:,1].max()
    ymin = airfoil[:,1].min()
    x = (airfoil[:,0]-xmin)/(xmax-xmin)
    y = (-airfoil[:,1]+ymin)/(xmax-xmin)
    y = y - np.mean(y)
    plt.plot(x,y)
    plt.axis("equal")
    plt.scatter(np.mean(x), np.mean(y))
    plt.savefig("images/airfoil"+str(i)+".png")
    plt.close()
    newairfoil = np.array([x,y]).T
    np.savetxt(pathair+"/../"+"sg6043mod"+str(i)+".txt", newairfoil, delimiter=",")
    