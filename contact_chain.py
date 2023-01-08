"""
A contact chain.

Used to verify contacts perform consistently.
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

    self.param("disp_c", self.TypeBoolean, "Display Size?", default=True)
    self.param("text_h", self.TypeDouble, "Text Height", default = 20)


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

    # Display text with relevant parameters    
    if self.disp_c:
        # Generate klayout region containing text
        # This can only generate with lower left at (0, 0)
        text_generator = pya.TextGenerator.default_generator()
        # default height is .7; third argument rescales to desired size
        text = text_generator.text(f'C={self.contact_size:g}', self.layout.dbu, self.text_h / .7)

        # Adjust position of region
        bbox = text.bbox()
        text_len = (bbox.right - bbox.left)
        text_x = - text_len / 2
        text_y = pad_h / 2 + bw
        text.move(text_x, text_y)

        # Add region to metal layer
        self.cell.shapes(self.metal_layer).insert (text)
