
from manim import *

class EquationScene(Scene):
    def construct(self):
        equation_tex = MathTex("x2+y2=25x^2+y^2=25x2+y2=25")
        self.play(Write(equation_tex))
        self.wait(2)
