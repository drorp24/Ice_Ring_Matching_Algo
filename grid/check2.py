import matplotlib.pyplot as plt
from shapely.geometry import box, Polygon, MultiPolygon, GeometryCollection
from descartes import PolygonPatch

MAX_COUNT = 250
def katana(geometry, threshold, count=0):
    """Split a Polygon into two parts across it's shortest dimension"""
    bounds = geometry.bounds
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]

    print("width",width, "height", height)
    if max(width, height) <= threshold or count == MAX_COUNT:
        # either the polygon is smaller than the threshold, or the maximum
        # number of recursions has been reached
        return [geometry]
    if height >= width:
        # split left to right
        a = box(bounds[0], bounds[1], bounds[2], bounds[1] + height / 2)
        b = box(bounds[0], bounds[1] + height / 2, bounds[2], bounds[3])

        #print("** height >= width **")
        #print(a,b)
    else:
        # split top to bottom
        a = box(bounds[0], bounds[1], bounds[0] + width / 2, bounds[3])
        b = box(bounds[0] + width / 2, bounds[1], bounds[2], bounds[3])
        #print("** height < width **")
        #print(a, b)

    result = []
    print(a, b)
    for d in (a, b,):
        print("d",d)
        c = geometry.intersection(d)
        print("c", c)
        if not isinstance(c, GeometryCollection):
            c = [c]
        for e in c:
            if isinstance(e, (Polygon, MultiPolygon)):
                result.extend(katana(e, threshold, count + 1))
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




fig = plt.figure()
ax = fig.add_subplot(111)

p = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
a = katana(p, 1)
for poly in list(a):
    ax.add_patch(PolygonPatch(poly, alpha=0.5, zorder=2))

xrange = [-2, 12]
yrange = [-2, 8]
ax.set_xlim(*xrange)
# ax.set_xticks(range(*xrange) + [xrange[-1]])
ax.set_ylim(*yrange)
# ax.set_yticks(range(*yrange) + [yrange[-1]])
ax.set_aspect(1)
plt.show()
