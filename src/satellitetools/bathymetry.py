import matplotlib.pyplot as plt

class Bathymetry:

    def __init__(self, bathygrid, coords, model, timestamp):
        self.bathygrid = bathygrid
        self.coords = coords
        self.model = model
        self.timestamp = timestamp

    def plotBathymetry(self):
        (fig, ax) = plt.subplots()
        bathy = ax.imshow(self.bathygrid, cmap='coolwarm')
        fig.suptitle(self.timestamp)

        bar = fig.colorbar(bathy)
        bar.set_label('Depth (m)')

        return fig
