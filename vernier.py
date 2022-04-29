"""
A Vernier structure.

Used for optical inspection of alignment.
"""

import pya
import math

import helpers

class vernier(pya.PCellDeclarationHelper):

  def __init__(self):
    # Important: initialize the super class
    super(vernier, self).__init__()
    # declare the parameters
    self.param("l1", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
    self.param("l2", self.TypeLayer, "Layer", default = pya.LayerInfo(2, 0))
    self.param("num_ticks", self.TypeInt, "Number of ticks", default=3)
    self.param("tick_width", self.TypeDouble, "Tick Width", default=1)
    self.param("tick_height", self.TypeDouble, "Tick Height", default=5)
    self.param("tick_spacing", self.TypeDouble, "Tick Spacing", default=1)
    self.param("shift", self.TypeDouble, "Shift per tick", default=.2)

  def display_text_impl(self):
    return f'Venier shift={self.shift}'
  
  def coerce_parameters_impl(self):
    pass

  def produce_impl(self):
    dbu = self.layout.dbu
    tw = self.tick_width / dbu
    th = self.tick_height / dbu
    ts = self.tick_spacing / dbu
    shift = self.shift / dbu
    
    long_L = ts + th
    
    self.cell.shapes(self.l1_layer).insert(pya.Box(
        *helpers.center_size_to_points(0, long_L + tw / 2, tw + 2 * ts, tw)))

    for ii in range(- self.num_ticks, self.num_ticks + 1):
        top_x = ii * (tw + ts)
        bottom_x = top_x + ii * shift
        line_h = th if ii % 5 else long_L
        self.cell.shapes(self.l1_layer).insert(pya.Box(
            *helpers.center_size_to_points(top_x, line_h / 2, tw, line_h)))

        self.cell.shapes(self.l2_layer).insert(pya.Box(
            *helpers.center_size_to_points(bottom_x, - line_h / 2, tw, line_h)))
