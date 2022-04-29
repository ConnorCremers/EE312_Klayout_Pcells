"""
A good ol fashioned transistor.
"""

import pya
import math

import helpers

class transistor(pya.PCellDeclarationHelper):

  def __init__(self):
    # Important: initialize the super class
    super(transistor, self).__init__()
    # declare the parameters
    self.param("active", self.TypeLayer, "Active Region Layer", default = pya.LayerInfo(1, 0))
    self.param("gate", self.TypeLayer, "Gate Poly Layer", default = pya.LayerInfo(2, 0))
    self.param("contact", self.TypeLayer, "Contact Etch Layer", default = pya.LayerInfo(3, 0))
    self.param("metal", self.TypeLayer, "Metal Layer", default = pya.LayerInfo(4, 0))
    self.param("p_metal", self.TypeLayer, "P Metal Layer", default = pya.LayerInfo(5, 0))
    self.param("W", self.TypeDouble, "Width", default = 100)
    self.param("L", self.TypeDouble, "Length", default = 100)
    self.param("alignment", self.TypeDouble, "Alignment Accuracy", default = 1)
    self.param("contact_size", self.TypeDouble, "Contact Size", default = 2)
    self.param("pad_w", self.TypeDouble, "Pad Width", default = 150)
    self.param("pad_h", self.TypeDouble, "Pad Length", default = 100)

    self.param("pad_dx", self.TypeDouble, "Pad X Spacing", default = 150)
    self.param("pad_dy", self.TypeDouble, "Pad Y Spacing", default = 100)


  def display_text_impl(self):
    return f'Trans L={self.L} W={self.W}'
  
  def coerce_parameters_impl(self):
    pass

  def produce_impl(self):
    dbu = self.layout.dbu
    W = self.W / dbu
    L = self.L / dbu
    alignment = self.alignment / dbu
    contact_size = self.contact_size / dbu
    pad_w = self.pad_w / dbu
    pad_h = self.pad_h / dbu
    pad_dx = self.pad_dx / dbu
    pad_dy = self.pad_dy / dbu
    offset = 4 * alignment + contact_size
    
    active_L = max(L, offset) + 2 * offset
    contact_w = max(offset, W)
    gate_contact_h = max(offset, L)

    self.cell.shapes(self.active_layer).insert(pya.Box(
        *helpers.center_size_to_points(0, 0, W, active_L - 2 * offset)))
    self.cell.shapes(self.active_layer).insert(pya.Box(
        *helpers.center_size_to_points(0, (active_L - offset) / 2, contact_w, offset)))
    self.cell.shapes(self.active_layer).insert(pya.Box(
        *helpers.center_size_to_points(0, (offset - active_L) / 2, contact_w, offset)))

    self.cell.shapes(self.gate_layer).insert(pya.Box(
        *helpers.center_size_to_points(0, 0, W + 2 * offset, L)))
    self.cell.shapes(self.gate_layer).insert(pya.Box(
        *helpers.center_size_to_points(- (W + 3 * offset) / 2, 0, offset, gate_contact_h)))

    gate_contact_x = - W / 2 - 3 * offset / 2
    for ii in range(int((gate_contact_h - 2 * alignment) / (contact_size + 2 * alignment))):
        #contact_y = gate_contact_h / 2 - (ii + 1) * (contact_size + alignment) + contact_size / 2 - alignment
        contact_y = gate_contact_h / 2 - offset / 2 - ii * (contact_size + 2 * alignment)
        self.cell.shapes(self.contact_layer).insert(pya.Box(
            *helpers.center_size_to_points(gate_contact_x, contact_y, contact_size, contact_size)))

    pad_x = (pad_w + pad_dx) / 2
    pad_y = (pad_h + pad_dy) / 2
    for x_mir in [-1, 1]:
        self.cell.shapes(self.metal_layer).insert(pya.Box(*helpers.center_size_to_points(
            x_mir * pad_x, pad_y, pad_w, pad_h))) 
    self.cell.shapes(self.metal_layer).insert(pya.Box(*helpers.center_size_to_points(
        pad_x, - pad_y, pad_w, pad_h))) 
    self.cell.shapes(self.p_metal_layer).insert(pya.Box(*helpers.center_size_to_points(
        - pad_x, - pad_y, pad_w, pad_h))) 

    # Add in S/D contacts, also P well contacts
    sd_contact_y = (active_L - offset) / 2
    p_well_y = - sd_contact_y - 2 * offset
    for ii in range(int((contact_w - 2 * alignment) / (contact_size + 2 * alignment))):
        contact_x = - contact_w / 2 + offset / 2 + ii * (contact_size + 2 * alignment)
        self.cell.shapes(self.contact_layer).insert(pya.Box(
            *helpers.center_size_to_points(contact_x, sd_contact_y, contact_size, contact_size))) 
        self.cell.shapes(self.contact_layer).insert(pya.Box(
            *helpers.center_size_to_points(contact_x, -sd_contact_y, contact_size, contact_size))) 
        self.cell.shapes(self.contact_layer).insert(pya.Box(
            *helpers.center_size_to_points(contact_x, p_well_y, contact_size, contact_size))) 

    # Connect S/D contacts to pads
    for y_mir in [-1, 1]:
        self.cell.shapes(self.metal_layer).insert(pya.Box(
            -contact_w / 2, y_mir * (sd_contact_y - offset / 2), pad_dx / 2 + offset, y_mir * (sd_contact_y + offset / 2)))
        self.cell.shapes(self.metal_layer).insert(pya.Box(
            pad_dx / 2, y_mir * (sd_contact_y + offset / 2), pad_dx / 2 + offset, y_mir * pad_dy / 2))

    # Connect gate contacts to pad
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        gate_contact_x - offset / 2, - gate_contact_h / 2, gate_contact_x + offset / 2, pad_dy / 2 + offset))
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        gate_contact_x + offset / 2, pad_dy / 2, - pad_dx / 2, pad_dy / 2 + offset))

    # Connect P well contacts to pad
    self.cell.shapes(self.p_metal_layer).insert(pya.Box(
        contact_w / 2, y_mir * p_well_y - offset / 2, - pad_dx / 2 - offset, p_well_y + offset / 2))
    self.cell.shapes(self.p_metal_layer).insert(pya.Box(
        - pad_dx / 2, p_well_y + offset / 2, - pad_dx / 2 - offset, - pad_dy / 2))

