"""
A four point transmission line structure.

Used for measuring sheet resistance and maybe contact resistance.
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

    self.param("disp_C", self.TypeBoolean, "Display C?", default=True)
    self.param("disp_W", self.TypeBoolean, "Display W?", default=True)
    self.param("disp_dL", self.TypeBoolean, "Display dL?", default=True)
    self.param("text_h", self.TypeDouble, "Text Height", default = 20)


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
    right = pad_dx / 2 + pad_w
    metal_w = dl * .8
    
    # Add contacts
    if 5 * dl > pad_w + metal_w:
      xs = [right - metal_w / 2 - shift * dl - (3 - ii) * contact_size
            for ii, shift in enumerate([6, 5, 3, 0])]
    else:
      xs = [- pad_dx / 2 - metal_w / 2 + shift * dl - (1 - ii) * contact_size
            for ii, shift in enumerate([-1, 0, 2, 5])]

    self.cell.shapes(self.resistor_layer).insert(pya.Box(
        xs[0] - w / 2, - w / 2, xs[-1] + w / 2, w / 2))

    polarities = [1, -1, 1, -1]
    for x, polarity in zip(xs, polarities):
      self.cell.shapes(self.contact_layer).insert(pya.Box(
          *helpers.center_size_to_points(x, 0, contact_size, contact_size)))
      self.cell.shapes(self.metal_layer).insert(pya.Box(
          x - metal_w / 2, - polarity * w, x + metal_w / 2, polarity * pad_dy / 2))

    # Add metal
    pad_end = pad_w + pad_dx / 2
    b_pad_start = pad_end - max(pad_w, pad_end - (dl - metal_w) / 2)
    t_pad_start = pad_end - max(pad_w, pad_end - (3 * dl - metal_w) / 2)
    tl_pad_end = max(-pad_dx / 2, xs[0] + metal_w / 2)
    bl_pad_end = max(-pad_dx / 2, xs[1] + metal_w / 2)
    tr_pad_start = min(pad_dx / 2, xs[2] - metal_w / 2)
    br_pad_start = min(pad_dx / 2, xs[3] - metal_w / 2)
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        -pad_dx / 2 - pad_w, pad_dy / 2, tl_pad_end, pad_h + pad_dy / 2))
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        -pad_dx / 2 - pad_w, - pad_dy / 2, bl_pad_end, - pad_h - pad_dy / 2))
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        tr_pad_start, pad_dy / 2, pad_dx / 2 + pad_w, pad_h + pad_dy / 2))
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        br_pad_start, - pad_dy / 2, pad_dx / 2 + pad_w, - pad_h - pad_dy / 2))

    # Display text with relevant parameters
    # Show some subset of dL, W, and C
    disp_str = ''
    if self.disp_dL:
        disp_str += f'dL={self.dl:g} '
    if self.disp_W:
        disp_str += f'W={self.width:g} '
    if self.disp_C:
        disp_str += f'C={self.contact_size:g} '
    
    if disp_str:
        # Generate klayout region containing text
        # This can only generate with lower left at (0, 0)
        text_generator = pya.TextGenerator.default_generator()
        # default height is .7; third argument rescales to desired size
        text = text_generator.text(disp_str[:-1], self.layout.dbu, self.text_h / .7)

        # Adjust position of region
        bbox = text.bbox()
        text_len = (bbox.right - bbox.left)
        text_x = - text_len / 2
        text_y = pad_h + pad_dy / 2 + .05 * pad_h
        text.move(text_x, text_y)

        # Add region to metal layer
        self.cell.shapes(self.metal_layer).insert (text)
