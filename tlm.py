"""
A four point transmission line structure.

Used for measuring sheet resistance and maybe contact resistance.

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

class tlm(pya.PCellDeclarationHelper):

  def __init__(self):
    # Important: initialize the super class
    super(tlm, self).__init__()
    # declare the parameters
    self.param("resistor", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
    self.param("contact", self.TypeLayer, "Layer", default = pya.LayerInfo(3, 0))
    self.param("metal", self.TypeLayer, "Layer", default = pya.LayerInfo(4, 0))

    self.param("width", self.TypeDouble, "Structure Width", default=3)
    self.param("dl", self.TypeDouble, "Contact Spacing", default=50)

    self.param("pad_w", self.TypeDouble, "Pad Width", default = 150)
    self.param("pad_h", self.TypeDouble, "Pad Length", default = 100)
    self.param("pad_dx", self.TypeDouble, "X pad spacing", default=150)
    self.param("pad_dy", self.TypeDouble, "Y pad spacing", default=100)

    self.param("contact_size", self.TypeDouble, "Contact Size", default = 2)


  def display_text_impl(self):
    return f'tlm dl={self.dl} contact={self.contact_size}'
  
  def coerce_parameters_impl(self):
    pass

  def produce_impl(self):
    dbu = self.layout.dbu
    w = self.width / dbu
    dl = self.dl / dbu
    pad_w = self.pad_w / dbu
    pad_h = self.pad_h / dbu
    pad_dx = self.pad_dx / dbu
    pad_dy = self.pad_dy / dbu
    contact_size = self.contact_size / dbu
    
    # Add in Si channel
    total_l = 3 * dl + w
    self.cell.shapes(self.resistor_layer).insert(pya.Box(
        *helpers.center_size_to_points(0, 0, total_l, w)))
    
    # Add contacts
    for mir in [-1, 1]:
      self.cell.shapes(self.contact_layer).insert(pya.Box(
          *helpers.center_size_to_points(mir * dl / 2, 0, contact_size, contact_size)))
      self.cell.shapes(self.contact_layer).insert(pya.Box(
          *helpers.center_size_to_points(mir * 3 * dl / 2, 0, contact_size, contact_size)))

    # Add metal
    metal_w = dl / 2
    pad_end = pad_w + pad_dx / 2
    b_pad_start = pad_end - max(pad_w, pad_end - (dl - metal_w) / 2)
    t_pad_start = pad_end - max(pad_w, pad_end - (3 * dl - metal_w) / 2)
    for mir in [-1, 1]:
      self.cell.shapes(self.metal_layer).insert(pya.Box(
          mir * (3 * dl - metal_w) / 2, - w / 2, mir * (3 * dl + metal_w) / 2, pad_dy / 2))
      self.cell.shapes(self.metal_layer).insert(pya.Box(
          mir * (dl - metal_w) / 2, w / 2, mir * (dl + metal_w) / 2, - pad_dy / 2))

      self.cell.shapes(self.metal_layer).insert(pya.Box(
          mir * b_pad_start, - pad_dy / 2, mir * pad_end, - pad_h - pad_dy / 2))
      self.cell.shapes(self.metal_layer).insert(pya.Box(
          mir * t_pad_start, pad_dy / 2, mir * pad_end, pad_h + pad_dy / 2))
