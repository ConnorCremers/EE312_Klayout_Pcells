"""
A Van der Pauw structure.

Used for measuring sheet resistance.

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

class vdp(pya.PCellDeclarationHelper):

  def __init__(self):
    # Important: initialize the super class
    super(vdp, self).__init__()
    # declare the parameters
    self.param("si", self.TypeLayer, "Semiconductor Layer", default = pya.LayerInfo(1, 0))
    self.param("contact", self.TypeLayer, "Contact Layer", default = pya.LayerInfo(3, 0))
    self.param("metal", self.TypeLayer, "Metal Layer", default = pya.LayerInfo(4, 0))

    self.param("pad_w", self.TypeDouble, "Pad Width", default = 150)
    self.param("pad_h", self.TypeDouble, "Pad Height", default = 100)
    self.param("pad_dx", self.TypeDouble, "X pad spacing", default=150)
    self.param("pad_dy", self.TypeDouble, "Y pad spacing", default=100)

    self.param("diag", self.TypeDouble, "Diagonal Length", default=30)

    self.param("alignment", self.TypeDouble, "Alignment Accuracy", default = 1)
    self.param("contact_size", self.TypeDouble, "Contact Size", default = 2)


  def display_text_impl(self):
    return f'Van Der Pauw diagonal length={self.diag}'
  
  def coerce_parameters_impl(self):
    pass

  def produce_impl(self):
    dbu = self.layout.dbu

    pad_w = self.pad_w / dbu
    pad_h = self.pad_h / dbu
    pad_dx = self.pad_dx / dbu
    pad_dy = self.pad_dy / dbu

    alignment = self.alignment / dbu
    contact_size = self.contact_size / dbu

    diag = self.diag / dbu

    contact_box = contact_size + 4 * alignment
    
    bar_height = diag + 4 * alignment
    self.cell.shapes(self.si_layer).insert(pya.Box(
        *helpers.center_size_to_points(0, 0, 2 * alignment, bar_height)))
    self.cell.shapes(self.si_layer).insert(pya.Box(
        *helpers.center_size_to_points(0, 0, bar_height, 2 * alignment)))
    
    rect = [(0, diag / 2), (diag / 2, 0), (0, - diag / 2), (- diag / 2, 0)]
    self.cell.shapes(self.si_layer).insert(helpers.tuples_to_polygon(rect))

    for mir in [-1, 1]:
        if self.metal_layer != self.si_layer:
            self.cell.shapes(self.si_layer).insert(pya.Box(
                *helpers.center_size_to_points(0, mir * (bar_height + contact_box) / 2, contact_box, contact_box)))
            self.cell.shapes(self.contact_layer).insert(pya.Box(
                *helpers.center_size_to_points(0, mir * (bar_height + contact_box) / 2, contact_size, contact_size)))

            self.cell.shapes(self.si_layer).insert(pya.Box(
                *helpers.center_size_to_points(mir * (bar_height + contact_box) / 2, 0, contact_box, contact_box)))
            self.cell.shapes(self.contact_layer).insert(pya.Box(
                *helpers.center_size_to_points(mir * (bar_height + contact_box) / 2, 0, contact_size, contact_size)))

        self.cell.shapes(self.metal_layer).insert(pya.Box(
            - contact_box / 2, mir * bar_height / 2, contact_box / 2, mir * pad_dy / 2))
        self.cell.shapes(self.metal_layer).insert(pya.Box(
            mir * bar_height / 2, - contact_box / 2, mir * pad_dx / 2, contact_box / 2))
    
    # Make pads
    pad_x = (pad_w + pad_dx) / 2
    pad_y = (pad_h + pad_dy) / 2
    for x_mir in [-1, 1]:
        for y_mir in [-1, 1]:
            self.cell.shapes(self.metal_layer).insert(pya.Box(
                *helpers.center_size_to_points(
                    x_mir * pad_x, y_mir * pad_y, pad_w, pad_h))) 
    
    # Connect Si contacts to pads
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        contact_box / 2, pad_dy / 2, - pad_dx / 2, pad_dy / 2 + contact_box))
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        - contact_box - pad_dx / 2, contact_box / 2, - pad_dx / 2, - pad_dy / 2))

    # Connect metal to pads
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        - contact_box / 2, - pad_dy / 2, pad_dx / 2, - pad_dy / 2 - contact_box))
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        pad_dx / 2, - contact_box / 2, pad_dx / 2 + contact_box, pad_dy / 2))
    
