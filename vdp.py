"""
A Van der Pauw structure.

Used for measuring sheet resistance.
"""

import pya
import math

import helpers

class vdp(pya.PCellDeclarationHelper):

  def __init__(self):
    # Important: initialize the super class
    super(vdp, self).__init__()
    # declare the parameters
    self.param("si", self.TypeLayer, "Semiconductor Layer", default = pya.LayerInfo(1, 0))
    self.param("contact", self.TypeLayer, "Contact Layer", default = pya.LayerInfo(3, 0))
    self.param("metal", self.TypeLayer, "Metal Layer", default = pya.LayerInfo(4, 0))

    self.param("pad_w", self.TypeDouble, "Pad Width", default = 150)
    self.param("pad_h", self.TypeDouble, "Pad Height", default = 100)
    self.param("pad_dx", self.TypeDouble, "X pad spacing", default=150)
    self.param("pad_dy", self.TypeDouble, "Y pad spacing", default=100)

    self.param("square", self.TypeDouble, "Square Side Length", default=40)
    self.param("slit", self.TypeDouble, "Slit Width", default=10)
    self.param("dia", self.TypeDouble, "Diameter", default=80)

    self.param("alignment", self.TypeDouble, "Alignment Accuracy", default = 1)
    self.param("contact_size", self.TypeDouble, "Contact Size", default = 2)

    self.param("disp_square", self.TypeBoolean, "Display square?", default=True)
    self.param("disp_slit", self.TypeBoolean, "Display slit?", default=True)
    self.param("disp_dia", self.TypeBoolean, "Display dia?", default=True)
    self.param("text_h", self.TypeDouble, "Text Height", default = 20)


  def display_text_impl(self):
    return f'Van Der Pauw Square Size={self.square}'
  
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

    rad = self.dia / (2 * dbu)
    slit = self.slit / dbu
    square = self.square / dbu

    # Produce cloverleaf shape on test layer
    points = []
    start_angle = math.asin(slit / (2 * rad))
    angle_offsets = [ii * math.pi / 2 for ii in range(4)]
    total_delta = math.pi / 2 - 2 * start_angle
    for base_angle in angle_offsets:
        points.append([square / 2 * math.cos(base_angle) - slit / 2 * math.sin(base_angle),
                       square / 2 * math.sin(base_angle) + slit / 2 * math.cos(base_angle)])
        for angle in [base_angle + start_angle + ii * total_delta / 15 for ii in range(16)]:
            p_x = rad * math.cos(angle)
            p_y = rad * math.sin(angle)
            points.append([p_x, p_y])
        points.append([slit / 2 * math.cos(base_angle) - square / 2 * math.sin(base_angle),
                       slit / 2 * math.sin(base_angle) + square / 2 * math.cos(base_angle)])
    self.cell.shapes(self.si_layer).insert(helpers.tuples_to_polygon(points))

    # Make pads, contacts, etc
    pad_x = (pad_w + pad_dx) / 2
    pad_y = (pad_h + pad_dy) / 2
    metal_w = 4 * alignment + contact_size
    contact_rad = rad - alignment - contact_size / math.sqrt(2)
    for x_mir in [-1, 1]:
        for y_mir in [-1, 1]:
            contact_pos = contact_rad / math.sqrt(2)
            # Define pads
            self.cell.shapes(self.metal_layer).insert(pya.Box(
                *helpers.center_size_to_points(
                    x_mir * pad_x, y_mir * pad_y, pad_w, pad_h))) 
            # Define connection between pads and contacts
            self.cell.shapes(self.metal_layer).insert(pya.Box(
                x_mir * (contact_pos - metal_w / 2), y_mir * (contact_pos - metal_w / 2),
                x_mir * (contact_pos + metal_w / 2), y_mir * pad_dy / 2))
            self.cell.shapes(self.metal_layer).insert(pya.Box(
                x_mir * (contact_pos - metal_w / 2), y_mir * pad_dy / 2,
                x_mir * pad_dx / 2, y_mir * (metal_w + pad_dy / 2)))
            # Define contacts
            self.cell.shapes(self.contact_layer).insert(pya.Box(
                *helpers.center_size_to_points(
                    x_mir * contact_pos, y_mir * contact_pos,
                    contact_size, contact_size)))

    # Display text with relevant parameters
    # Show some subset of square, slit, and dia
    disp_str = ''
    if self.disp_square:
        disp_str += f'S={self.square:g} '
    if self.disp_slit:
        disp_str += f'L={self.slit:g} '
    if self.disp_dia:
        disp_str += f'D={self.dia:g} '
    
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
