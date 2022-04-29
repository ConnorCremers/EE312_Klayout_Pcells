"""
A contact chain.

Used to verify contacts perform consistently.

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

class contact_chain(pya.PCellDeclarationHelper):

  def __init__(self):
    # Important: initialize the super class
    super(contact_chain, self).__init__()
    # declare the parameters
    self.param("si", self.TypeLayer, "Semiconductor Layer", default = pya.LayerInfo(1, 0))
    self.param("contact", self.TypeLayer, "Contact Layer", default = pya.LayerInfo(3, 0))
    self.param("metal", self.TypeLayer, "Metal Layer", default = pya.LayerInfo(4, 0))

    self.param("pad_w", self.TypeDouble, "Pad Width", default = 150)
    self.param("pad_h", self.TypeDouble, "Pad Height", default = 100)
    self.param("pad_dx", self.TypeDouble, "X pad spacing", default=150)

    self.param("alignment", self.TypeDouble, "Alignment Accuracy", default = 1)
    self.param("contact_size", self.TypeDouble, "Contact Size", default = 2)
    
    self.param("bar_len", self.TypeDouble, "Conductor Length", default = 10)
    self.num = 0


  def display_text_impl(self):
    return f'contact chain size={self.contact_size} num={self.num}'
  
  def coerce_parameters_impl(self):
    pass

  def produce_impl(self):
    self.num=0
    dbu = self.layout.dbu

    pad_w = self.pad_w / dbu
    pad_h = self.pad_h / dbu
    pad_dx = self.pad_dx / dbu

    alignment = self.alignment / dbu
    cs = self.contact_size / dbu

    bl = self.bar_len / dbu

    bw = cs + 4 * alignment

    for x_mir in [-1, 1]:
        self.cell.shapes(self.metal_layer).insert(pya.Box(
            *helpers.center_size_to_points(
                x_mir * (pad_dx + pad_w) / 2, 0, pad_w, pad_h)))
    x = -pad_dx / 2 - bw / 2
    y = -pad_h / 2 + bw / 2
    c_dir = -1
    layers = [self.si_layer, self.metal_layer]
    layer = True
    next_br = False
    while True:
        if abs(y + c_dir * (2 * bl + bw / 2)) > pad_h / 2 and layer:
            if next_br:
                break
            if x + 3 * bl - bw / 2 > pad_dx / 2:
                next_br = True
            self.cell.shapes(layers[layer]).insert(pya.Box(
                *helpers.center_size_to_points(
                   x + bl / 2, y, bl + bw, bw)))
            x += bl
            c_dir *= -1
            self.cell.shapes(self.contact_layer).insert(pya.Box(
                *helpers.center_size_to_points(
                   x, y, cs, cs)))
            layer = not layer
        self.cell.shapes(layers[layer]).insert(pya.Box(
            *helpers.center_size_to_points(
                x, y + c_dir * bl / 2, bw, bl + bw)))
        y += c_dir * bl
        self.cell.shapes(self.contact_layer).insert(pya.Box(
            *helpers.center_size_to_points(
                x, y, cs, cs)))
        if not layer:
            self.num += 2
        layer = not layer
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        x - bw / 2, y - bw / 2, pad_dx / 2, y + bw / 2))
