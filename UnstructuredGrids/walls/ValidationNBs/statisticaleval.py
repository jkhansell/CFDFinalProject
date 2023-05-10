import pandas as pd
import numpy as np
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
import matplotlib.pyplot as plt
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def analysis_SD_airfoils(CoefCSV):
    
    airfoils = ['A' + str(i) for i in range(1, n_airfoils+1)]
    angles = ['B' + str(i) for i in range(1, n_angles+1)]

    # Create a full factorial design matrix
    design = pd.DataFrame(np.array(np.meshgrid(airfoils, angles)).T.reshape(-1, 2), columns=['Airfoil', 'Angle_of_attack'])
    print(design)

    # Generate random responses for the full factorial design
    np.random.seed(123)
    design['Y'] = np.exp(-np.linspace(0,1,n_airfoils*n_angles))+np.random.rand(n_airfoils*n_angles)

    # Fit an ANOVA model to the full factorial design
    model = ols('Y ~ Airfoil + Angle_of_attack', data=design).fit()
    anova_table = anova_lm(model)

    # Print the ANOVA table
    print(anova_table)

    # Identify the best airfoil based on the mean response
    airfoil_means = design.groupby('Airfoil')['Y'].mean()
    best_airfoil = airfoil_means.idxmax()
    # print(f"The best airfoil is {best_airfoil} with a mean response of {airfoil_means.loc[best_airfoil]}")

    # Perform Tukey HSD test
    tukey_results = pairwise_tukeyhsd(design['Y'], design['Airfoil'])

    # Print the results
    print(tukey_results)

    fig, ax = plt.subplots(figsize=(8, 6))

    # Compute the y-tick positions for the bar chart
    ax.set_yticklabels(np.unique(design['Airfoil']))

    # Plot the bar chart
    tukey_results.plot_simultaneous(ax=ax)

    # Add labels and title
    ax.set_xlabel('Response')
    ax.axvline(x=0.0)
    ax.set_ylabel('Airfoil')
    ax.set_title('Tukey HSD Test Results')
    plt.show()
