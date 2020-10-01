from __future__ import annotations

from enum import Enum


class Color(Enum):
    Black = (0, 0, 0)
    NavyBlue = (0, 0, 128)
    DarkBlue = (0, 0, 139)
    MediumBlue = (0, 0, 205)
    Blue = (0, 0, 255)
    DarkGreen = (0, 100, 0)
    Green = (0, 128, 0)
    DarkCyan = (0, 139, 139)
    DeepSkyBlue = (0, 191, 255)
    DarkTurquoise = (0, 206, 209)
    MediumSpringGreen = (0, 250, 154)
    Lime = (0, 255, 0)
    SpringGreen = (0, 255, 127)
    Cyan = (0, 255, 255)
    MidnightBlue = (25, 25, 112)
    DodgerBlue = (30, 144, 255)
    LightSeaGreen = (32, 178, 170)
    ForestGreen = (34, 139, 34)
    SeaGreen = (46, 139, 87)
    LimeGreen = (50, 205, 50)
    MediumSeaGreen = (60, 179, 113)
    Turquoise = (64, 224, 208)
    RoyalBlue = (65, 105, 225)
    SteelBlue = (70, 130, 180)
    DarkSlateBlue = (72, 61, 139)
    MediumTurquoise = (72, 209, 204)
    Indigo = (75, 0, 130)
    DarkOliveGreen = (85, 107, 47)
    CadetBlue = (95, 158, 160)
    CornflowerBlue = (100, 149, 237)
    MediumAquamarine = (102, 205, 170)
    SlateBlue = (106, 90, 205)
    OliveDrab = (107, 142, 35)
    MediumSlateBlue = (123, 104, 238)
    LawnGreen = (124, 252, 0)
    Chartreuse = (127, 255, 0)
    Aquamarine = (127, 255, 212)
    Maroon = (128, 0, 0)
    Purple = (128, 0, 128)
    Olive = (128, 128, 0)
    Grey = (128, 128, 128)
    LightSlateBlue = (132, 112, 255)
    SkyBlue = (135, 206, 235)
    LightSkyBlue = (135, 206, 250)
    BlueViolet = (138, 43, 226)
    DarkRed = (139, 0, 0)
    DarkMagenta = (139, 0, 139)
    SaddleBrown = (139, 69, 19)
    DarkSeaGreen = (143, 188, 143)
    LightGreen = (144, 238, 144)
    Brown = (165, 42, 42)
    Red = (255, 0, 0)
    Orange = (255, 165, 0)
    Pink = (255, 192, 203)
    Yellow = (255, 255, 0)
    White = (255, 255, 255)

    def __init__(self, r, g, b):
        self._r = r / 255
        self._g = g / 255
        self._b = b / 255

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
