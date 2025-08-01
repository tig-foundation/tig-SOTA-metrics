###
# Download standard QKP instances
# Script adapted from https://github.com/phil85/benchmark-instances-for-qkp/blob/main/generate_instances_from_raw_data.py
### 

import requests
import os

print('Downloading Standard_QKP instances...')
os.makedirs('Standard_QKP', exist_ok=True)
# %% Download standard QKP instances

n_nodes_list = [100, 200, 300]
densities = {100: [25, 50, 75, 100],
             200: [25, 50, 75, 100],
             300: [25, 50]}
n_instances = 10

# Download txt file from url
for n_nodes in n_nodes_list:
    for density in densities[n_nodes]:
        for i in range(1, n_instances + 1):
            url = 'https://cedric.cnam.fr/~soutif/QKP/jeu_{:d}_{:d}_{:d}.txt'.format(n_nodes, density, i)
            print('Downloading ' + url)

            # Get file name
            file_name = url.split('/')[-1]

            # Download file
            lines = requests.get(url).text.split('\n')

            # Get number of nodes and edges
            n_nodes = int(lines[1])

            # Get linear utilities
            edges = []
            linear_utilities = [int(v) for v in lines[2].strip('\n').split(' ') if v != '']
            for i in range(n_nodes):
                edges += [(i, i, linear_utilities[i])]

            # Get quadratic utilities
            for i in range(n_nodes):
                quadratic_utilities = [int(v) for v in lines[3 + i].strip('\n').split(' ') if v != '']
                for j in range(i + 1, n_nodes):
                    edges += [(i, j, quadratic_utilities[j - (i + 1)])]

            # Remove edges with utility of zero
            edges = [edge for edge in edges if edge[2] != 0]

            # Write file
            f = open('Standard_QKP/' + file_name, 'w')
            f.write('{:d} {:d} {:s}\n'.format(n_nodes, len(edges), 'int'))
            for ind_i, ind_j, val in edges:
                f.write('{:d} {:d} {:.6f}\n'.format(ind_i, ind_j, val))

            # Get weights
            budget = int(lines[4 + n_nodes].strip('\n'))
            weights = [int(v) for v in lines[5 + n_nodes].strip('\n').split(' ') if v != '']

            # Write weights to file
            for weight in weights:
                f.write('{:d} '.format(weight))
            f.write('\n')

            # Write budget to file
            f.write('{:d}\n'.format(budget))
            f.close()

print("Done")