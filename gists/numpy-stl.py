from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot
from matplotlib import cm
from matplotlib.colors import LightSource

# Create a new plot
figure = pyplot.figure()
axes = figure.add_subplot(111, projection='3d')

# Load the STL files and add the vectors to the plot
your_mesh = mesh.Mesh.from_file('test.stl')

ls = LightSource(270, 45)
rgb = ls.shade(your_mesh.z, cmap=cm.gist_earth, vert_exag=0.1, blend_mode='soft')

mesh_new1 = mplot3d.art3d.Poly3DCollection(your_mesh.vectors)
mesh_new1.set_facecolor(rgb[:, 0])
axes.add_collection3d(mesh_new1)
mesh_new2 = mesh_new1.rotate([0.5, 0.0, 0.0], math.radians(90))
axes.add_collection3d(mesh_new2)

# Auto scale to the mesh size
scale = your_mesh.points.flatten(-1)
axes.auto_scale_xyz(scale, scale, scale)

# Show the plot to the screen
pyplot.show()
