
class Geocode(object):
    LON_BOUND = (-180, 180)
    LAT_BOUND = (-90, 90)
    SIZE = (LON_BOUND[1]-LON_BOUND[0], LAT_BOUND[1]-LAT_BOUND[0])

    def __init__(self, lon, lat, depth=32):
        self.depth = depth
        self.loc = (lon, lat)
        self._gbox = None
        self.gcode, self._gbox_coord = self._calcGeocode(self.loc, self.depth)

    def _boundRatio(self, position, bound):
        '''
        Return a floating number from 0 to 1 representing the position in the bound.
        * position(float): position in the bound
        * bound(tuple): lower, upper bound
        '''
        return (position - bound[0])/float(bound[1]-bound[0])

    def _calcGeocode(self, loc, depth):

        minx = miny = 0.0
        maxx = maxy = 1.0

        maskDepth = (1 << depth)
        x, y = loc

        # Compute the percentage of x and y in perspective of the bound
        x_part = long(self._boundRatio(x, self.LON_BOUND) * maskDepth)
        y_part = long(self._boundRatio(y, self.LAT_BOUND) * maskDepth)

        # Interleave x and y at the bit level.
        # For x=1100 and y=1010, result would be: 11100100
        # The result would be a number twice the size of depth
        result = 0
        for i in xrange(depth):
            x_bit = (x_part >> i) & 1
            y_bit = (y_part >> i) & 1

            # Calculate the interleave value
            result_index = i * 2
            x_val = x_bit * 2 ** (result_index+1)
            y_val = y_bit * 2 ** result_index
            result += y_val + x_val

            # Calc box
            box_index = (2 << i)
            minx += float(y_bit)/box_index
            miny += float(x_bit)/box_index

        return result, (minx, miny, maxx, maxy)

    @property
    def gbox(self):
        depth = self.depth
        if self._gbox is None:
            minx, miny, maxx, maxy = self._gbox_coord
            print "# %s, %s, %s, %s" % (minx, miny, maxx, maxy)

            maxx = minx + 1.0/(2L << (depth-1))
            maxy = miny + 1.0/(2L << (depth-1))

            minx, maxx = [self.LON_BOUND[0] + x * self.SIZE[0] for x in(minx, maxx)]
            miny, maxy = [self.LON_BOUND[1] + y * self.SIZE[1] for y in(miny, maxy)]

            self._gbox = tuple([round(x, 6) for x in minx, miny, maxx, maxy])

        return self._gbox
