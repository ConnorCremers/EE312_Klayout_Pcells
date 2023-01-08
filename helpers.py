import pya

def tuples_to_polygon(points: list, shift=(0, 0)):
    """Converts an iterable of tuples to polygon object.
    
    Contains an optional shift. 
    """
    pya_points = [pya.Point.from_dpoint(pya.DPoint(x - shift[0], y - shift[1]))
                  for (x, y) in points]
    return pya.Polygon(pya_points)

def center_size_to_points(center_x, center_y, width, length):
    """Convert center and size to lower left/upper right coords."""
    return (center_x - width / 2, center_y - length / 2,
            center_x + width / 2, center_y + length / 2)
