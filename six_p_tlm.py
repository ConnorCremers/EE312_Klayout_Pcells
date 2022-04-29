"""
A six point transmission line structure.

Used for measuring sheet resistance and maybe contact resistance.
"""

import pya
import math

import helpers

class six_p_tlm(pya.PCellDeclarationHelper):

  def __init__(self):
    # Important: initialize the super class
    super(six_p_tlm, self).__init__()
    # declare the parameters
    self.param("resistor", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))
    self.param("contact", self.TypeLayer, "Layer", default = pya.LayerInfo(3, 0))
    self.param("metal", self.TypeLayer, "Layer", default = pya.LayerInfo(4, 0))

    self.param("width", self.TypeDouble, "Structure Width", default=10)
    self.param("dl", self.TypeDouble, "Contact Spacing", default=100)

    self.param("pad_w", self.TypeDouble, "Pad Width", default = 150)
    self.param("pad_h", self.TypeDouble, "Pad Length", default = 100)
    self.param("metal_size", self.TypeDouble, "Pad gap and extension width", default=20)
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
    ms = self.metal_size / dbu
    pad_dy = self.pad_dy / dbu
    contact_size = self.contact_size / dbu
    
    top_contacts = [(2 * ii - 2.5) * dl for ii in range(3)]
    bot_contacts = [(2 * ii - 1.5) * dl for ii in range(3)]
    for cl in top_contacts:
      self.cell.shapes(self.contact_layer).insert(pya.Box(
          *helpers.center_size_to_points(cl, 0, contact_size, contact_size)))
      self.cell.shapes(self.metal_layer).insert(pya.Box(
          cl - ms / 2, - w / 2, cl + ms / 2, pad_dy / 2))
      self.cell.shapes(self.metal_layer).insert(pya.Box(
          cl - pad_w / 2, pad_dy / 2, cl + pad_w / 2, pad_h + pad_dy / 2))

    for cl in bot_contacts:
      self.cell.shapes(self.contact_layer).insert(pya.Box(
          *helpers.center_size_to_points(cl, 0, contact_size, contact_size)))
      self.cell.shapes(self.metal_layer).insert(pya.Box(
          cl - ms / 2, w / 2, cl + ms / 2, - pad_dy / 2))
      self.cell.shapes(self.metal_layer).insert(pya.Box(
          cl - pad_w / 2, - pad_dy / 2, cl + pad_w / 2, - pad_h - pad_dy / 2))

    # Add in Si channel
    total_l = 5 * dl + w
    self.cell.shapes(self.resistor_layer).insert(pya.Box(
        *helpers.center_size_to_points(0, 0, total_l, w)))
