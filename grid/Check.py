from shapely.geometry import Polygon, box, GeometryCollection, MultiPolygon
from shapely.strtree import STRtree
import matplotlib.pyplot as plt

grid_size = 1000

grid_resolution = 2


def plot(polygons):
    plt.clf()
    for poly in polygons:
        poly_points = poly.boundary
        x = [point[0] for point in poly_points]
        y = [point[1] for point in poly_points]

        plt.plot(x, y)


def katana(geometry, threshold, count=0):
    """Split a Polygon into two parts across it's shortest dimension"""
    bounds = geometry.bounds
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    if max(width, height) <= threshold or count == 250:
        # either the polygon is smaller than the threshold, or the maximum
        # number of recursions has been reached
        return [geometry]
    if height >= width:
        # split left to right
        a = box(bounds[0], bounds[1], bounds[2], bounds[1]+height/2)
        b = box(bounds[0], bounds[1]+height/2, bounds[2], bounds[3])
    else:
        # split top to bottom
        a = box(bounds[0], bounds[1], bounds[0]+width/2, bounds[3])
        b = box(bounds[0]+width/2, bounds[1], bounds[2], bounds[3])
    result = []
    for d in (a, b,):
        c = geometry.intersection(d)
        if not isinstance(c, GeometryCollection):
            c = [c]
        for e in c:
            if isinstance(e, (Polygon, MultiPolygon)):
                result.extend(katana(e, threshold, count+1))
    if count > 0:
        return result
    # convert multipart into singlepart
    final_result = []
    for g in result:
        if isinstance(g, MultiPolygon):
            final_result.extend(g)
        else:
            final_result.append(g)
    return final_result


polys = []
# my_polygon = Polygon([(0, 0), (0, 2), (2, 2),  (2,0)])
# my_polygon1 = Polygon([(-1,-1), (-1, 1), (1, 1),  (1,-1)])

my_polygon = Polygon([(0, 0), (0, 2), (2, 2),  (2,0)])
my_polygon1 = Polygon([(0,0), (0,2), (1,0.1),  (2, 2), (2,0)])
a = my_polygon.intersection(my_polygon1)
a =  katana(my_polygon,grid_resolution)
plot(a)
minx, miny, maxx, maxy = my_polygon.bounds
bounding_box_grid_cells = my_polygon.bounds


polys = [Polygon(((0, 0), (3, 0), (1, 1))), Polygon(((0, 1), (0, 0), (1, 0))), Polygon(((100, 100), (101, 100), (101, 101)))]
s = STRtree(polys)

query_geom = Polygon([(-1, -1), (2, 0), (2, 2), (-1, 2)])
result = s.query(query_geom)
print (polys[0] in result)