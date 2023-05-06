import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import json


def get_aoasweep_data(sweepdir):

    cwd = os.getcwd()
    files = os.listdir(sweepdir)
    files = np.array(files)
    coefficients = np.zeros((len(files),3))
    angles = np.arange(-10, 22, 2)

    sfiles = [ifile.replace("GRTsteady", "") for ifile in files]
    sfiles = np.array([ifile.replace("Mesh8", "") for ifile in sfiles]).astype(int)
    #print(sfiles)

    files = files[sfiles.argsort()]
    #print(files)

    for i, file in enumerate(files):
        os.chdir(os.path.join(sweepdir,file))
        coefs = np.loadtxt("postProcessing/forceCoeffs/0/forceCoeffs.dat", skiprows=9 , delimiter="\t")
        coefsmean = np.mean(coefs[-200:], axis=0)
        #print(coefs)
        coefficients[i, 1] = coefsmean[2]
        coefficients[i, 2] = coefsmean[3]
        os.chdir(cwd)

    return sorted(files), coefficients, angles


def experimental_data_validation(coefs, liftdata, dragdata, angles, Re):
    
    metrics = {}
    
    ind = np.where(np.isin(liftdata["aoa"], angles))


    cl = np.array(liftdata[Re])[ind]
    cd = np.array(dragdata[Re])[ind]

    # R_squared calculation

    ssres_cl = np.sum((cl - coefs[:,2])**2)
    ssres_cd = np.sum((cd - coefs[:,1])**2)

    sstot_cl = np.sum((cl - cl.mean())**2)
    sstot_cd = np.sum((cd - cd.mean())**2)

    R_clsq = 1 - ssres_cl/sstot_cl
    R_cdsq = 1 - ssres_cd/sstot_cd

    metrics["Rsq"] = [R_clsq, R_cdsq]

    # relative error calculation

    rerr_cl = 100*np.abs((cl - coefs[:,2]))/cl.mean()
    rerr_cd = 100*np.abs((cd - coefs[:,1]))/cd.mean()

    metrics["rerr_cl"] = rerr_cl.tolist()
    metrics["rerr_cd"] = rerr_cd.tolist()

    # relative area error

    auc_clexp = np.trapz(cl)
    auc_cdexp = np.trapz(cd)

    auc_cl = np.trapz(coefs[:,2])
    auc_cd = np.trapz(coefs[:,1])

    arerrcl = np.abs(auc_cl - auc_clexp)/auc_clexp
    arerrcd = np.abs(auc_cd - auc_cdexp)/auc_cdexp

    metrics["area_error_cl"] = arerrcl
    metrics["area_error_cd"] = arerrcd
    
    fig, ax = plt.subplots(figsize=(7,6), dpi=130)
    ax.grid()
    ax.set_axisbelow(True)
    ax.bar(angles, rerr_cd)
    #ax.set_title("Lift coefficient vs angle of attack")
    ax.set_xlabel("Angle of attack $[^\circ]$", fontsize=16)
    ax.set_ylabel(r"$\epsilon_{r, C_d}$ [\%]", fontsize=16)
    fig.savefig("validationgraphs/errcd"+Re+".svg")
    
    fig, ax = plt.subplots(figsize=(7,6), dpi=130)
    ax.grid()
    ax.set_axisbelow(True)
    ax.bar(angles, rerr_cl)
    #ax.set_title("Lift coefficient vs angle of attack")
    ax.set_xlabel("Angle of attack $[^\circ]$", fontsize=16)
    ax.set_ylabel(r"$\epsilon_{r, C_l}$ [\%]", fontsize=16)
    fig.savefig("validationgraphs/errcl"+Re+".svg")
    

    with open("metrics"+Re+".json", "w") as outfile:
        json.dump(metrics, outfile, indent=4)

if __name__ == "__main__":

    try: 
        sweepdir = str(sys.argv[1])
        Re = str(sys.argv[2])
    
    except (IndexError, ValueError):
        raise SystemExit
    
    
    plt.rcParams.update({
        'text.usetex': True,
        'figure.dpi': 150
    })
    
    plt.tight_layout()
    
    # Get experimental data from table
    
    cl_data = pd.read_csv("./data/Cl_data.csv")
    cd_data = pd.read_csv("./data/Cd_data.csv")

    files, coefs, angles = get_aoasweep_data(sweepdir)
    
    experimental_data_validation(coefs, cl_data, cd_data, angles, Re)


    fig, ax = plt.subplots(figsize=(7,6), dpi=130)
    ax.grid()
    ax.set_axisbelow(True)
    
    ax.plot(cl_data["aoa"], cl_data[Re], marker=".", label="Experiment (Bartl, Sagmo, Bracchi, Sætran)")
    ax.plot(angles, coefs[:,2], marker=".", label=r"$\gamma-Re_\theta$  SST simulation")
    
    # plot extra data for Re = 1e5
    if Re == "100k":
        NTNU1_cl = np.loadtxt("data/NTNU1_cl.txt", delimiter=",")
        NTNU2_cl = np.loadtxt("data/NTNU2_cl.txt", delimiter=",")
        ax.plot(np.rint(NTNU1_cl[:,0]), NTNU1_cl[:,1], marker=".", label="Experiment NTNU force gauge")
        ax.plot(np.rint(NTNU2_cl[:,0]), NTNU2_cl[:,1], marker=".", label="Experiment NTNU int. surf. press.")

    ax.set_xlabel("Angle of attack $[^\circ]$", fontsize=16)
    ax.set_ylabel(r"$C_l\quad[-]$", fontsize=16)
    ax.legend()
    
    fig.savefig("validationgraphs/AoA_Cl"+Re+".svg")

    fig, ax = plt.subplots(figsize=(7,6), dpi=130)
    ax.grid()
    ax.set_axisbelow(True)

    ax.plot(cd_data["aoa"], cd_data[Re], marker=".", label="Experiment (Bartl, Sagmo, Bracchi, Sætran)")
    ax.plot(angles, coefs[:,1], marker=".", label=r"$\gamma-Re_\theta$ SST simulation")
 
    # extra data for Re = 1e5
    if Re == "100k":
        DTU_intwakecd = np.loadtxt("data/DTU_intwakecd.txt", delimiter=",")
        METU_forcecd = np.loadtxt("data/METU_forcecd.txt", delimiter=",")
        NTNU_intwakecd = np.loadtxt("data/NTNU_intwakecd.txt", delimiter=",")
        
        ax.plot(np.rint(DTU_intwakecd[:,0]), DTU_intwakecd[:,1], marker=".", label="DTU int. wake. mom. loss")
        ax.plot(np.rint(METU_forcecd[:,0]), METU_forcecd[:,1], marker=".", label="METU force gauge")
        ax.plot(np.rint(NTNU_intwakecd[:,0]), NTNU_intwakecd[:,1], marker=".", label="DTU direct force meas.")

    ax.set_xlabel("Angle of attack $[^\circ]$", fontsize=16)
    ax.set_ylabel(r"$C_d\quad[-]$", fontsize=16)
    ax.legend()
    
    fig.savefig("validationgraphs/AoA_Cd"+Re+".svg")

    fig, ax = plt.subplots(figsize=(7,6), dpi=130)
    ax.grid()
    ax.set_axisbelow(True)
    #ax.set_title("Lift coefficient vs angle of attack")
    ax.plot(cd_data["aoa"], cl_data[Re]/cd_data[Re], marker=".", label="Experiment (Bartl, Sagmo, Bracchi, Sætran)")
    ax.plot(angles, coefs[:,2]/coefs[:,1], marker=".", label=r"$\gamma-Re_\theta$ SST simulation")
    ax.set_xlabel("Angle of attack $[^\circ]$", fontsize=16)
    ax.set_ylabel(r"$C_d\quad[-]$", fontsize=16)
    ax.legend()
    
    fig.savefig("validationgraphs/AoA_CdCl"+Re+".svg")



