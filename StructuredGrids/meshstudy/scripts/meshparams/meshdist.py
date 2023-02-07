import numpy as np
import json
import sys

def make_mesh_distribution(N):
    R_ratio = np.linspace(1.06, 1.025, N)
    H_ratio = np.linspace(1.04, 1.02, N)
    Zone_1 = np.linspace(100, 300, N)
    Zone_2 = Zone_1/1.5
    Zone_3 = Zone_1/1.5
    Rdivs = np.linspace(100, 200, N)
    Hdivs = np.linspace(100, 150, N)
    with open("baseparamfile.json") as f:
        meshdict = json.load(f)
        name = meshdict["name"]
        for i in range(N):
            meshdict["name"] = name+str(i)
            meshdict["R_ratio"] = R_ratio[i]
            meshdict["H_ratio"] = H_ratio[i]
            meshdict["Zone_1"] = int(Zone_1[i])
            meshdict["Zone_2"] = int(Zone_2[i])
            meshdict["Zone_3"] = int(Zone_3[i])
            meshdict["Rdivs"] = int(Rdivs[i])
            meshdict["Hdivs"] = int(Hdivs[i])
            with open('./meshes/mesh'+str(i)+'.json', 'w') as file:
                json.dump(meshdict, file)

if __name__ == '__main__':
    make_mesh_distribution(int(sys.argv[1]))


