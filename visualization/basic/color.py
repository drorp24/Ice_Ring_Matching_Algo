from __future__ import annotations

from enum import Enum


class Color(Enum):
    Black = (0.0, 0.0, 0.0)
    NavyBlue = (0.0, 0.0, 0.502)
    DarkBlue = (0.0, 0.0, 0.545)
    MediumBlue = (0.0, 0.0, 0.804)
    Blue = (0.0, 0.0, 1.0)
    DarkGreen = (0.0, 0.392, 0.0)
    Green = (0.0, 0.502, 0.0)
    DarkCyan = (0.0, 0.545, 0.545)
    DeepSkyBlue = (0.0, 0.749, 1.0)
    DarkTurquoise = (0.0, 0.808, 0.82)
    MediumSpringGreen = (0.0, 0.98, 0.604)
    Lime = (0.0, 1.0, 0.0)
    SpringGreen = (0.0, 1.0, 0.498)
    Cyan = (0.0, 1.0, 1.0)
    MidnightBlue = (0.098, 0.098, 0.439)
    DodgerBlue = (0.118, 0.565, 1.0)
    LightSeaGreen = (0.125, 0.698, 0.667)
    ForestGreen = (0.133, 0.545, 0.133)
    SeaGreen = (0.18, 0.545, 0.341)
    LimeGreen = (0.196, 0.804, 0.196)
    MediumSeaGreen = (0.235, 0.702, 0.443)
    Turquoise = (0.251, 0.878, 0.816)
    RoyalBlue = (0.255, 0.412, 0.882)
    SteelBlue = (0.275, 0.51, 0.706)
    DarkSlateBlue = (0.282, 0.239, 0.545)
    MediumTurquoise = (0.282, 0.82, 0.8)
    Indigo = (0.294, 0.0, 0.51)
    DarkOliveGreen = (0.333, 0.42, 0.184)
    CadetBlue = (0.373, 0.62, 0.627)
    CornflowerBlue = (0.392, 0.584, 0.929)
    MediumAquamarine = (0.4, 0.804, 0.667)
    SlateBlue = (0.416, 0.353, 0.804)
    OliveDrab = (0.42, 0.557, 0.137)
    MediumSlateBlue = (0.482, 0.408, 0.933)
    LawnGreen = (0.486, 0.988, 0.0)
    Chartreuse = (0.498, 1.0, 0.0)
    Aquamarine = (0.498, 1.0, 0.831)
    Maroon = (0.502, 0.0, 0.0)
    Purple = (0.502, 0.0, 0.502)
    Olive = (0.502, 0.502, 0.0)
    Grey = (0.502, 0.502, 0.502)
    LightSlateBlue = (0.518, 0.439, 1.0)
    SkyBlue = (0.529, 0.808, 0.922)
    LightSkyBlue = (0.529, 0.808, 0.98)
    BlueViolet = (0.541, 0.169, 0.886)
    DarkRed = (0.545, 0.0, 0.0)
    DarkMagenta = (0.545, 0.0, 0.545)
    SaddleBrown = (0.545, 0.271, 0.075)
    DarkSeaGreen = (0.561, 0.737, 0.561)
    LightGreen = (0.565, 0.933, 0.565)
    Brown = (0.647, 0.165, 0.165)
    Red = (1.0, 0.0, 0.0)
    Orange = (1.0, 0.647, 0.0)
    Pink = (1.0, 0.753, 0.796)
    Yellow = (1.0, 1.0, 0.0)
    White = (1.0, 1.0, 1.0)

    def __init__(self, r: float, g: float, b: float):
        if (r < 0 or r > 1 or
                g < 0 or g > 1 or
                b < 0 or b > 1):
            raise ValueError("Color RGB values should be within 0-1 range")
        self._r = r
        self._g = g
        self._b = b

    @property
    def r(self) -> float:
        return self._r

    @property
    def g(self) -> float:
        return self._g

    @property
    def b(self) -> float:
        return self._b

    def get_rgb(self) -> (float, float, float):
        return self.r, self.g, self.b

    def get_rgb_with_alpha(self, alpha: float) -> (float, float, float, float):
        return self.r, self.g, self.b, alpha
