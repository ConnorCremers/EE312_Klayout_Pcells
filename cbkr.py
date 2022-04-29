"""
A cross bridge kelvin resistor.

Used to measure contact resistivity.
"""

import pya
import math

import helpers

class cbkr(pya.PCellDeclarationHelper):

  def __init__(self):
    # Initialize the super class
    super(cbkr, self).__init__()
    # declare the parameters
    self.param("si", self.TypeLayer, "Semiconductor Layer", default = pya.LayerInfo(1, 0))
    self.param("contact", self.TypeLayer, "Contact Layer", default = pya.LayerInfo(3, 0))
    self.param("metal", self.TypeLayer, "Metal Layer", default = pya.LayerInfo(4, 0))

    self.param("pad_w", self.TypeDouble, "Pad Width", default = 150)
    self.param("pad_h", self.TypeDouble, "Pad Height", default = 100)
    self.param("pad_dx", self.TypeDouble, "X pad spacing", default=150)
    self.param("pad_dy", self.TypeDouble, "Y pad spacing", default=100)

    self.param("alignment", self.TypeDouble, "Alignment Accuracy", default = 1)
    self.param("contact_size", self.TypeDouble, "Contact Size", default = 2)


  def display_text_impl(self):
    return f'CKBR size={self.contact_size}'
  
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

    arm_w = contact_size + 4 * alignment

    x_arm_l = pad_dx / 2 + arm_w / 2
    y_arm_l = pad_dy / 2 + arm_w / 2
    
    contact_centers = [(0, 0), (- x_arm_l, 0), (0, y_arm_l)]
    for x, y in contact_centers:
        self.cell.shapes(self.contact_layer).insert(pya.Box(
            *helpers.center_size_to_points(x, y, contact_size, contact_size)))
    
    # Make + shape
    for mir, layer in zip([1, -1], [self.si_layer, self.metal_layer]):
        self.cell.shapes(layer).insert(pya.Box(
            *helpers.center_size_to_points(0, 0, arm_w, arm_w)))
        self.cell.shapes(layer).insert(pya.Box(
            *helpers.center_size_to_points(mir * (- arm_w / 2 - x_arm_l / 2), 0, x_arm_l, arm_w)))
        self.cell.shapes(layer).insert(pya.Box(
            *helpers.center_size_to_points(0, mir * (arm_w / 2 + y_arm_l / 2), arm_w, y_arm_l)))
    
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
        arm_w / 2, pad_dy / 2, - pad_dx / 2, pad_dy / 2 + arm_w))
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        - arm_w - pad_dx / 2, arm_w / 2, - pad_dx / 2, - pad_dy / 2))

    # Connect metal to pads
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        arm_w / 2, - pad_dy / 2, pad_dx / 2, - pad_dy / 2 - arm_w))
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        pad_dx / 2, arm_w / 2, pad_dx / 2 + arm_w, pad_dy / 2))
    
