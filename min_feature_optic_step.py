"""
A pattern of increasing rectangles overlaid on a step.

Used for optical inspection of minimum feature size.

MIT License

Copyright (c) 2022 Connor Cremers.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import pya
import math

import helpers

class min_feature_optic_step(pya.PCellDeclarationHelper):

  def __init__(self):
    # Initialize the super class
    super(min_feature_optic_step, self).__init__()
    # declare the parameters
    self.param("l1", self.TypeLayer, "Feature Layer", default = pya.LayerInfo(1, 0))
    self.param("l2", self.TypeLayer, "Step Layer", default = pya.LayerInfo(2, 0))
    self.param("num_features", self.TypeInt, "Number of sizes", default=10)
    self.param("min_width", self.TypeDouble, "Smallest test size", default=1)
    self.param("feature_spacing", self.TypeDouble, "Test feature spacing", default=5)
    self.param("delta", self.TypeDouble, "Change per feature", default=.5)
    self.param("height", self.TypeDouble, "Structure Height", default=10)
    self.param("pos", self.TypeBoolean, "Positive or negative?", default=True)

  def display_text_impl(self):
    return f'Min Feature Optic Step delta={self.delta}'
  
  def coerce_parameters_impl(self):
    pass

  def produce_impl(self):
    dbu = self.layout.dbu
    min_w = self.min_width / dbu
    fs = self.feature_spacing / dbu
    delta = self.delta / dbu
    num = self.num_features
    height = self.height / dbu
    centers = [0]
    if self.pos:
      centers = [0]
      for ii in range(num - 1):
          centers.append(centers[-1] + fs + min_w + (ii + 1 / 2) * delta)
      shift = centers[-1] / 2 + (num - 1) * delta / 4
      
      for ii in range(num):
        loc = (shift - centers[ii], 0)
        dims = (min_w + ii * delta, height)
        self.cell.shapes(self.l1_layer).insert(pya.Box(
            *helpers.center_size_to_points(*loc, *dims)))  
    else:
      centers = [0]
      for ii in range(num):
          centers.append(centers[-1] + fs + min_w + ii * delta)
      shift = centers[-1] / 2
      
      for ii in range(num + 1):
        self.cell.shapes(self.l1_layer).insert(pya.Box(
            *helpers.center_size_to_points(shift - centers[ii], 0, fs, height)))    
    self.cell.shapes(self.l2_layer).insert(pya.Box(
        *helpers.center_size_to_points(0, 0, centers[-1] + 2 * fs, height / 2)))    
