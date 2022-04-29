"""
A four point probe.

Used for measuring sheet resistance.
"""

import pya
import math

import helpers

class four_point_probe(pya.PCellDeclarationHelper):

  def __init__(self):
    # Important: initialize the super class
    super(four_point_probe, self).__init__()
    # declare the parameters
    self.param("resistor", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
    self.param("contact", self.TypeLayer, "Layer", default = pya.LayerInfo(3, 0))
    self.param("metal", self.TypeLayer, "Layer", default = pya.LayerInfo(4, 0))

    self.param("width", self.TypeDouble, "Structure Width", default=3)
    self.param("length", self.TypeDouble, "Meas Length", default=200)

    self.param("pad_w", self.TypeDouble, "Pad Width", default = 150)
    self.param("pad_h", self.TypeDouble, "Pad Length", default = 100)
    self.param("pad_dx", self.TypeDouble, "X pad spacing", default=150)
    self.param("pad_dy", self.TypeDouble, "Y pad spacing", default=100)

    self.param("alignment", self.TypeDouble, "Alignment Accuracy", default = 1)
    self.param("contact_size", self.TypeDouble, "Contact Size", default = 2)
    self.param("min_feature", self.TypeDouble, "Min Feature in Resistor Layer", default=1)


  def display_text_impl(self):
    return f'FPP W={self.width} L={self.length}'
  
  def coerce_parameters_impl(self):
    pass

  def produce_impl(self):
    dbu = self.layout.dbu
    w = self.width / dbu
    l = self.length / dbu
    pad_w = self.pad_w / dbu
    pad_h = self.pad_h / dbu
    pad_dx = self.pad_dx / dbu
    pad_dy = self.pad_dy / dbu
    alignment = self.alignment / dbu
    contact_size = self.contact_size / dbu
    min_feature = self.min_feature / dbu
    
    contact_box = contact_size + 4 * alignment

    # Make pads
    pad_x = (pad_w + pad_dx) / 2
    pad_y = (pad_h + pad_dy) / 2
    for x_mir in [-1, 1]:
        for y_mir in [-1, 1]:
            self.cell.shapes(self.metal_layer).insert(pya.Box(
                *helpers.center_size_to_points(
                    x_mir * pad_x, y_mir * pad_y, pad_w, pad_h))) 
    
    # Add in Si channel
    total_l = pad_dx + 2 * pad_w
    contact_y = - min_feature * 4 - (w + contact_box) / 2
    if contact_box < w:
      self.cell.shapes(self.resistor_layer).insert(pya.Box(
          *helpers.center_size_to_points(0, 0, total_l, w)))
    else:
      self.cell.shapes(self.resistor_layer).insert(pya.Box(
          *helpers.center_size_to_points(0, 0, total_l - 2 * contact_box, w)))
      self.cell.shapes(self.resistor_layer).insert(pya.Box(
          *helpers.center_size_to_points((total_l - contact_box) / 2, 0, contact_box, contact_box)))
      self.cell.shapes(self.resistor_layer).insert(pya.Box(
          *helpers.center_size_to_points((contact_box - total_l) / 2, 0, contact_box, contact_box)))
    for mir in [-1, 1]:
      self.cell.shapes(self.resistor_layer).insert(pya.Box(
          *helpers.center_size_to_points(mir * l / 2, - min_feature * 2 - w / 2,
                                      min_feature, min_feature * 4))) 
      self.cell.shapes(self.resistor_layer).insert(pya.Box(
          *helpers.center_size_to_points(mir * l / 2, contact_y, contact_box, contact_box)))
    
    # Add contacts
    if self.resistor_layer != self.metal_layer:
      for mir in [-1, 1]:
        self.cell.shapes(self.contact_layer).insert(pya.Box(
            *helpers.center_size_to_points(mir * l / 2, contact_y, contact_size, contact_size)))
        self.cell.shapes(self.contact_layer).insert(pya.Box(
            *helpers.center_size_to_points(mir * (total_l - contact_box) / 2, 0, contact_size, contact_size)))


    # Finish metal
    for mir in [-1, 1]:
      self.cell.shapes(self.metal_layer).insert(pya.Box(
          mir * total_l / 2, -contact_box / 2, mir * (total_l / 2 - contact_box), pad_dy / 2))
      self.cell.shapes(self.metal_layer).insert(pya.Box(
          mir * (l - contact_box) / 2, contact_y + contact_box / 2, mir * (l + contact_box) / 2, - pad_dy / 2))
