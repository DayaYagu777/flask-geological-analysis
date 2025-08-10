from matplotlib import pyplot as plt
import numpy as np

def plot_stereonet(data, title='Stereonet Plot'):
    """
    Create a stereonet plot from the given data.

    Parameters:
    - data: A list of tuples containing the plunge and azimuth of the geological features.
    - title: Title of the plot.
    """
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, polar=True)

    # Convert plunge and azimuth to radians
    plunge = np.radians([d[0] for d in data])
    azimuth = np.radians([d[1] for d in data])

    # Plot the data on the stereonet
    for p, a in zip(plunge, azimuth):
        ax.plot([a, a], [0, np.pi/2 - p], marker='o', linestyle='-', markersize=5)

    ax.set_title(title, va='bottom')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_ylim(0, np.pi/2)

    plt.grid(True)
    plt.show()

def generate_stereonet_data(features):
    """
    Generate stereonet data from geological features.

    Parameters:
    - features: A list of geological features with their plunge and azimuth.

    Returns:
    - data: A list of tuples containing plunge and azimuth.
    """
    data = []
    for feature in features:
        plunge = feature['plunge']
        azimuth = feature['azimuth']
        data.append((plunge, azimuth))
    return data