"""
A snake-like pattern used to test minimum feature size.

Can test for continuity or isolation.

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

class min_feature_electrical(pya.PCellDeclarationHelper):

  def __init__(self):
    # Important: initialize the super class
    super(min_feature_electrical, self).__init__()
    # declare the parameters
    self.param("si", self.TypeLayer, "Feature Layer", default = pya.LayerInfo(1, 0))
    self.param("contact", self.TypeLayer, "Contact Layer", default = pya.LayerInfo(3, 0))
    self.param("metal", self.TypeLayer, "Metal Layer", default = pya.LayerInfo(4, 0))

    self.param("feature_width", self.TypeDouble, "Feature size", default=1)
    self.param("feature_spacing", self.TypeDouble, "Feature spacing", default=5)

    self.param("pad_dy", self.TypeDouble, "Pad Y Spacing", default=100)
    self.param("pad_w", self.TypeDouble, "Pad Width", default=150)
    self.param("pad_h", self.TypeDouble, "Pad Height", default=100)

    self.param("alignment", self.TypeDouble, "Alignment Accuracy", default = 1)
    self.param("contact_size", self.TypeDouble, "Contact Size", default = 2)

    self.param("cont", self.TypeBoolean, "Continuity expected?", default=True)

  def display_text_impl(self):
    return f'Min Feature Electrical width={self.feature_width}'
  
  def coerce_parameters_impl(self):
    pass

  def get_snake(self, h, w, fs, fw):
    """Creates a snake structure.

    Returns two paths which look like this:
    |‾‾‾‾‾| |‾‾‾‾‾| | |
    | |‾| |_| |‾| |_| |
    | | |_____| |_____|
    Args:
        h is the total height of the structure
        w is the total length of the structure
        fw is the space between the two lines
        fs is the closest each line gets to itself
    """
    dxs = [2 * fw + fs, fs]
    top_hs = [h, fs]
    bottom_hs = [h - fs, 0]

    top_snake = [(0, 0), (0, h)]
    bottom_snake = [(fw, 0), (fw, h - fs)]
    flip = False
    while True:
        top_snake.append( (top_snake[-1][0] + dxs[flip], top_hs[flip]) )
        bottom_snake.append( (bottom_snake[-1][0] + dxs[not flip], bottom_hs[flip]) )
        flip = not flip
        top_snake.append( (top_snake[-1][0], top_hs[flip]) )
        bottom_snake.append( (bottom_snake[-1][0], bottom_hs[flip]) )
        if bottom_snake[-1][0] > w and not flip:
            bottom_snake[-1] = (bottom_snake[-1][0], h)
            return top_snake, bottom_snake

  def produce_impl(self):
    dbu = self.layout.dbu
    fw = self.feature_width / dbu
    fs = self.feature_spacing / dbu
    pad_dy = self.pad_dy / dbu
    pad_w = self.pad_w / dbu
    pad_h = self.pad_h / dbu

    alignment = self.alignment / dbu
    contact_size = self.contact_size / dbu

    offset = contact_size + 4 * alignment

    height = pad_dy - (2 * fs if self.cont else 0)
    top_snake, bottom_snake = self.get_snake(height, pad_w, fs, fw)
    if self.cont:
        pad_end = fs + (pad_h if self.si_layer == self.metal_layer else offset)
        pad_1 = [
            (0, - pad_end),
            (bottom_snake[-1][0], - pad_end),
            (bottom_snake[-1][0], - fs),
            (bottom_snake[0][0], - fs)
        ]

        pad_2 = [
            (bottom_snake[-1][0], height + pad_end),
            (0, height + pad_end),
            (0, height + fs),
            (top_snake[-1][0], height + fs),
        ]

        point_list = pad_1 + bottom_snake + pad_2 + list(reversed(top_snake))
        self.cell.shapes(self.si_layer).insert(helpers.tuples_to_polygon(
            point_list, (bottom_snake[-1][0] / 2, height / 2)))
    else:
        pad_end = pad_h if self.si_layer == self.metal_layer else offset
        end = bottom_snake[-1][0]
        top_snake.pop(0)
        top_snake.extend([
            (top_snake[-1][0], height + pad_end),
            (0, height + pad_end)
        ])
        bottom_snake.pop(-1)
        bottom_snake.extend([
            (end, -pad_end),
            (fw, -pad_end)
        ])

        self.cell.shapes(self.si_layer).insert(helpers.tuples_to_polygon(
            bottom_snake, (end / 2, height / 2)))     
        self.cell.shapes(self.si_layer).insert(helpers.tuples_to_polygon(
            top_snake, (end / 2, height / 2)))

    if self.si_layer != self.metal_layer:
        contact_y = (pad_dy + offset) / 2
        for ii in range(int((pad_w - 2 * alignment) / (contact_size + 2 * alignment))):
            contact_x = - pad_w / 2 + offset / 2 + ii * (contact_size + 2 * alignment)
            self.cell.shapes(self.contact_layer).insert(pya.Box(
                *helpers.center_size_to_points(contact_x, contact_y, contact_size, contact_size))) 
            self.cell.shapes(self.contact_layer).insert(pya.Box(
                *helpers.center_size_to_points(contact_x, - contact_y, contact_size, contact_size)))
        pad_y = (pad_dy + pad_h) / 2
        self.cell.shapes(self.metal_layer).insert(pya.Box(
            *helpers.center_size_to_points(0, - pad_y, pad_w, pad_h)))
        self.cell.shapes(self.metal_layer).insert(pya.Box(
            *helpers.center_size_to_points(0, pad_y, pad_w, pad_h)))
