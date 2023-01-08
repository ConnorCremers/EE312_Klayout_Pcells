"""
A diode or capacitor structure.

Used for testing any number of electrical characteristics.
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
    self.param("diode", self.TypeBoolean, "Diode?", default=True)

    self.param("disp_L", self.TypeBoolean, "Display Size?", default=True)
    self.param("text_h", self.TypeDouble, "Text Height", default = 20)


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

    # Display text with relevant parameters    
    if self.disp_L:
        # Generate klayout region containing text
        # This can only generate with lower left at (0, 0)
        text_generator = pya.TextGenerator.default_generator()
        # default height is .7; third argument rescales to desired size
        text = text_generator.text(f'L={self.L:g}', self.layout.dbu, self.text_h / .7)

        # Adjust position of region
        bbox = text.bbox()
        text_len = (bbox.right - bbox.left)
        text_x = - text_len / 2
        text_y = max(p_contact_pos + offset / 2, pad_h / 2) + offset
        text.move(text_x, text_y)

        # Add region to metal layer
        self.cell.shapes(self.metal_layer).insert (text)