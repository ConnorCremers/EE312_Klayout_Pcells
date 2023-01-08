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

    self.param("width", self.TypeDouble, "Structure Width", default=3)
    self.param("dl", self.TypeDouble, "Contact Spacing", default=50)

    self.param("pad_w", self.TypeDouble, "Pad Width", default = 150)
    self.param("pad_h", self.TypeDouble, "Pad Length", default = 100)
    self.param("pad_dy", self.TypeDouble, "Y pad spacing", default=100)

    self.param("contact_size", self.TypeDouble, "Contact Size", default = 2)

    self.param("disp_C", self.TypeBoolean, "Display C?", default=True)
    self.param("disp_W", self.TypeBoolean, "Display W?", default=True)
    self.param("disp_dL", self.TypeBoolean, "Display dL?", default=True)
    self.param("text_h", self.TypeDouble, "Text Height", default = 20)


  def display_text_impl(self):
    return f'six p tlm dl={self.dl} contact={self.contact_size}'
  
  def coerce_parameters_impl(self):
    pass

  def produce_impl(self):
    dbu = self.layout.dbu
    w = self.width / dbu
    dl = self.dl / dbu
    pad_w = self.pad_w / dbu
    pad_h = self.pad_h / dbu
    pad_dy = self.pad_dy / dbu
    contact_size = self.contact_size / dbu
    
    xs = []
    contact_x = - contact_size
    metal_w = dl * .8
    min_gap = .05 * pad_h

    for ii in range(6):
      contact_x += ii * dl + contact_size
      self.cell.shapes(self.contact_layer).insert(pya.Box(
          *helpers.center_size_to_points(contact_x, 0, contact_size, contact_size)))
      y_dir = 1 if bool(ii % 2) else -1
      self.cell.shapes(self.metal_layer).insert(pya.Box(
          contact_x - metal_w / 2, - y_dir * w,
          contact_x + metal_w / 2, y_dir * pad_dy / 2))
      xs.append(contact_x)
    # Add in Si channel
    self.cell.shapes(self.resistor_layer).insert(pya.Box(
        - w / 2, - w / 2, xs[-1] + w / 2, w / 2))    
    
    # Add pads
    # First define the pads for the middle contacts, which we fix
    mid_bot_l = xs[2] - metal_w / 2
    mid_top_l = xs[3] - metal_w / 2
    mid_bot_r = mid_bot_l + pad_w # Right edge of middle bottom pad
    mid_top_r = mid_top_l + pad_w # Right edge of middle top pad
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        mid_bot_l, - pad_dy / 2, mid_bot_r, - pad_dy / 2 - pad_h))
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        mid_top_l, pad_dy / 2, mid_top_r, pad_dy / 2 + pad_h))
    # Set the left two pads as far right as possible without hitting middle pads
    left_bot_l = min(xs[0] - metal_w / 2, mid_bot_l - pad_w - min_gap)
    left_top_l = min(xs[1] - metal_w / 2, mid_top_l - pad_w - min_gap)
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        left_bot_l, - pad_dy / 2, left_bot_l + pad_w, - pad_dy / 2 - pad_h))
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        left_top_l, pad_dy / 2, left_top_l + pad_w, pad_dy / 2 + pad_h))
    # Set the right two pads as far left as possible without hitting middle pads
    right_bot_r = max(xs[4] + metal_w / 2, mid_bot_r + pad_w + min_gap)
    right_top_r = max(xs[5] + metal_w / 2, mid_top_r + pad_w + min_gap)
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        right_bot_r - pad_w, - pad_dy / 2, right_bot_r, - pad_dy / 2 - pad_h))
    self.cell.shapes(self.metal_layer).insert(pya.Box(
        right_top_r - pad_w, pad_dy / 2, right_top_r, pad_dy / 2 + pad_h))

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
        text_x = (xs[-1] - text_len) / 2
        text_y = pad_h + pad_dy / 2 + min_gap
        text.move(text_x, text_y)

        # Add region to metal layer
        self.cell.shapes(self.metal_layer).insert (text)

