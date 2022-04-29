"""
A diode or capacitor structure.

Used for testing any number of electrical characteristics.

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

class diode(pya.PCellDeclarationHelper):

  def __init__(self):
    # Initialize the super class
    super(diode, self).__init__()
    # declare the parameters
    self.param("active", self.TypeLayer, "Active Region Layer", default = pya.LayerInfo(1, 0))
    self.param("contact", self.TypeLayer, "Contact Etch Layer", default = pya.LayerInfo(3, 0))
    self.param("metal", self.TypeLayer, "Metal Layer", default = pya.LayerInfo(4, 0))
    self.param("p_metal", self.TypeLayer, "P Metal Layer", default = pya.LayerInfo(5, 0))
    self.param("L", self.TypeDouble, "Length", default = 50)
    self.param("alignment", self.TypeDouble, "Alignment Accuracy", default = 1)
    self.param("contact_size", self.TypeDouble, "Contact Size", default = 2)
    self.param("pad_w", self.TypeDouble, "Pad Width", default = 150)
    self.param("pad_h", self.TypeDouble, "Pad Length", default = 100)
    self.param("pad_dx", self.TypeDouble, "Pad X Spacing", default = 150)
    self.param("diode", self.TypeBoolean, "Diode or cap?", default=True)


  def display_text_impl(self):
    part_str = 'Diode' if self.diode else 'Cap'
    return f'{part_str} L={self.L}'
  
  def coerce_parameters_impl(self):
    pass

  def produce_impl(self):
    dbu = self.layout.dbu
    L = self.L / dbu
    alignment = self.alignment / dbu
    contact_size = self.contact_size / dbu
    pad_w = self.pad_w / dbu
    pad_h = self.pad_h / dbu
    pad_dx = self.pad_dx / dbu
    offset = 4 * alignment + contact_size

    self.cell.shapes(self.active_layer).insert(pya.Box(
        *helpers.center_size_to_points(0, 0, L, L)))

    num_contacts = int((L - 3 * alignment) / (contact_size + 2 * alignment))
    p_contact_pos = L / 2 + 3 * offset / 2
    for ii in range(num_contacts):
        contact_x = - L / 2 + offset / 2 + ii * (contact_size + 2 * alignment)
        self.cell.shapes(self.contact_layer).insert(pya.Box(
            *helpers.center_size_to_points(contact_x, p_contact_pos, contact_size, contact_size)))
        self.cell.shapes(self.contact_layer).insert(pya.Box(
            *helpers.center_size_to_points(contact_x, -p_contact_pos, contact_size, contact_size)))
        self.cell.shapes(self.contact_layer).insert(pya.Box(
            *helpers.center_size_to_points(-p_contact_pos, contact_x, contact_size, contact_size)))
        if self.diode or self.metal_layer != self.active_layer:
            for jj in range(num_contacts):
                contact_y = L / 2 - offset / 2 - jj * (contact_size + 2 * alignment)
                self.cell.shapes(self.contact_layer).insert(pya.Box(
                    *helpers.center_size_to_points(contact_x, contact_y, contact_size, contact_size)))

    pad_x = (pad_w + pad_dx) / 2
    self.cell.shapes(self.metal_layer).insert(pya.Box(*helpers.center_size_to_points(
        pad_x, 0, pad_w, pad_h))) 
    self.cell.shapes(self.p_metal_layer).insert(pya.Box(*helpers.center_size_to_points(
        - pad_x, 0, pad_w, pad_h))) 

    self.cell.shapes(self.metal_layer).insert(pya.Box(
        - L / 2, - L / 2, pad_dx / 2, L / 2))

    self.cell.shapes(self.p_metal_layer).insert(pya.Box(
        - p_contact_pos - offset / 2, p_contact_pos + offset / 2,
        - p_contact_pos + offset / 2, - p_contact_pos - offset / 2))
    self.cell.shapes(self.p_metal_layer).insert(pya.Box(
        - p_contact_pos + offset / 2, p_contact_pos - offset / 2,
        L / 2, p_contact_pos + offset / 2))
    self.cell.shapes(self.p_metal_layer).insert(pya.Box(
        - p_contact_pos + offset / 2, - p_contact_pos - offset / 2,
        L / 2, - p_contact_pos + offset / 2))

    self.cell.shapes(self.p_metal_layer).insert(pya.Box(
        - pad_dx / 2, - L / 2, - p_contact_pos - offset / 2, L / 2))