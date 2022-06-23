"""
A ono contact structure.

Good when contacts are electrically long and alignment is poor.
See Mizuki Ono, Akira Nishiyama, Akira Toriumi,
A simple approach to understanding measurement errors in the 
cross-bridge Kelvin resistor and a new pattern for measurements 
of specific contact resistivity, Solid-State Electronics, Volume 46,
Issue 9, 2002, Pages 1325-1331.
"""

import pya
import math

import helpers

class ono_contact(pya.PCellDeclarationHelper):

  def __init__(self):
    # Important: initialize the super class
    super(ono_contact, self).__init__()
    # declare the parameters
    self.param("si", self.TypeLayer, "Semiconductor Layer", default = pya.LayerInfo(1, 0))
    self.param("contact", self.TypeLayer, "Contact Layer", default = pya.LayerInfo(3, 0))
    self.param("metal", self.TypeLayer, "Metal Layer", default = pya.LayerInfo(4, 0))

    self.param("pad_w", self.TypeDouble, "Pad Width", default = 150)
    self.param("pad_h", self.TypeDouble, "Pad Height", default = 100)
    self.param("pad_dx", self.TypeDouble, "X pad spacing", default=150)
    self.param("pad_dy", self.TypeDouble, "Y pad spacing", default=100)

    self.param("alignment", self.TypeDouble, "Alignment Accuracy", default = 1)
    self.param("meas_contact_w", self.TypeDouble, "Measurement Contact Width", default = 4)
    self.param("meas_contact_l", self.TypeDouble, "Measurement Contact Length", default = 10)

    self.param("tlm_dl", self.TypeDouble, "TLM Distance", default = 10)
    self.param("meas_w", self.TypeDouble, "Measurement Tap Width", default = 2)

  def display_text_impl(self):
    return f'Ono Contact size={self.meas_contact_w}'
  
  def coerce_parameters_impl(self):
    pass

  def produce_impl(self):
    dbu = self.layout.dbu

    pad_w = self.pad_w / dbu
    pad_h = self.pad_h / dbu
    pad_dx = self.pad_dx / dbu
    pad_dy = self.pad_dy / dbu

    alignment = self.alignment / dbu

    mcw = self.meas_contact_w / dbu
    mcl = self.meas_contact_l / dbu

    dl = self.tlm_dl / dbu
    meas_w = self.meas_w / dbu
    metal_w = mcw + 4 * alignment

    # Define pads
    pad_x = pad_w + pad_dx
    pad_y = (pad_h + pad_dy) / 2
    for y_mir in [-1, 1]:
        self.cell.shapes(self.metal_layer).insert(pya.Box(
            *helpers.center_size_to_points(
                0, y_mir * pad_y, pad_w, pad_h))) 
        for x_mir in [-1, 1]:
                self.cell.shapes(self.metal_layer).insert(pya.Box(
                    *helpers.center_size_to_points(
                        x_mir * pad_x, y_mir * pad_y, pad_w, pad_h))) 

    # Define big contacts
    big_contact_x = 2 * dl + mcl / 2
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        - big_contact_x + mcl / 2 + 2 * alignment, - metal_w / 2,
        metal_w / 2, metal_w / 2))
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        - metal_w / 2, metal_w / 2,
        metal_w / 2, pad_dy / 2))
    for x_mir in [-1, 1]:
        self.cell.shapes(self.contact_layer).insert(pya.Box(
            *helpers.center_size_to_points(
                x_mir * big_contact_x, 0, mcl, mcw)))
        self.cell.shapes(self.metal_layer).insert(pya.Box(
            x_mir * (pad_dx + pad_w / 2 + metal_w), - metal_w / 2,
            x_mir * (big_contact_x - mcl / 2 - 2 * alignment), metal_w / 2))
        self.cell.shapes(self.metal_layer).insert(pya.Box(
            x_mir * (pad_dx + pad_w / 2), metal_w / 2,
            x_mir * (pad_dx + pad_w / 2 + metal_w), pad_dy / 2))

    # Define Si area + meas contacts
    si_l = 4 * dl + 2 * mcl + 4 * alignment
    self.cell.shapes(self.si_layer).insert(pya.Box(
        *helpers.center_size_to_points(
            0, 0, si_l, metal_w)))
    for x in [-dl, 0, dl]:
        self.cell.shapes(self.si_layer).insert(pya.Box(
            x - meas_w / 2, - metal_w / 2, x + meas_w / 2, - 1.5 * metal_w))
        self.cell.shapes(self.si_layer).insert(pya.Box(
            *helpers.center_size_to_points(
                x, - 2 * metal_w, metal_w, metal_w)))
        self.cell.shapes(self.contact_layer).insert(pya.Box(
            *helpers.center_size_to_points(
                x, - 2 * metal_w, mcw, mcw)))
    
    # Connect Si to metal
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        - metal_w / 2, - 1.5 * metal_w, metal_w / 2, - pad_dy))
    for x_mir in [-1, 1]:
        self.cell.shapes(self.metal_layer).insert(pya.Box(
            x_mir * (dl - metal_w / 2), - 1.5 * metal_w,
            x_mir * (pad_dx + pad_w / 2 + metal_w), - 2.5 * metal_w))
        self.cell.shapes(self.metal_layer).insert(pya.Box(
            x_mir * (pad_dx + pad_w / 2), - 2.5 * metal_w,
            x_mir * (pad_dx + pad_w / 2 + metal_w), - pad_dy / 2))

