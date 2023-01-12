"""
A good ol fashioned transistor.
"""

import pya
import math

import helpers

class grid_labels(pya.PCellDeclarationHelper):

  def __init__(self):
    # Important: initialize the super class
    super(grid_labels, self).__init__()
    # declare the parameters
    self.param("l", self.TypeLayer, "Layer", default = pya.LayerInfo(1, 0))

    self.param("text_h", self.TypeDouble, "Text Height", default=20)

    self.param("dx", self.TypeDouble, "X Spacing", default = 100)
    self.param("dy", self.TypeDouble, "Y Spacing", default = 100)

    self.param("x_num", self.TypeInt, "Column Count", default = 5)
    self.param("y_num", self.TypeInt, "Row Count", default = 5)

  def display_text_impl(self):
    return f'Grid Labels'
  
  def coerce_parameters_impl(self):
    pass

  def produce_impl(self):
    dbu = self.layout.dbu

    # Generate klayout region containing text
    # This can only generate with lower left at (0, 0)
    text_generator = pya.TextGenerator.default_generator()
    # default height is .7; rescale to um
    text_h = self.text_h / .7

    texts = []
    for ii in range(self.x_num):
        texts.append([])
        for jj in range(self.y_num):
            texts[-1].append(text_generator.text(f'{ chr(65 + ii) }{jj + 1}', dbu, text_h))
            texts[-1][-1].move(ii * self.dx / dbu, - jj * self.dy / dbu)

    x_shift = - (texts[0][0].bbox().left + texts[-1][0].bbox().right) / 2
    y_shift = - (texts[0][0].bbox().top + texts[0][-1].bbox().bottom) / 2

    for ii in range(self.x_num):
        for jj in range(self.y_num):
            texts[ii][jj].move(x_shift, y_shift)
            self.cell.shapes(self.l_layer).insert(texts[ii][jj])
