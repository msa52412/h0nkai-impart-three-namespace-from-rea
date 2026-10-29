# -*- coding: utf-8 -*-
"""_shot.py <hwnd> <out.png> —— 直接抓某个窗口的内容（PrintWindow，被遮挡也能抓）"""
import ctypes
import ctypes.wintypes as wt
import sys

from PIL import Image

u32 = ctypes.WinDLL("user32", use_last_error=True)
g32 = ctypes.WinDLL("gdi32", use_last_error=True)

PW_RENDERFULLCONTENT = 0x00000002


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wt.DWORD), ("biWidth", ctypes.c_long), ("biHeight", ctypes.c_long),
                ("biPlanes", wt.WORD), ("biBitCount", wt.WORD), ("biCompression", wt.DWORD),
                ("biSizeImage", wt.DWORD), ("biXPelsPerMeter", ctypes.c_long),
                ("biYPelsPerMeter", ctypes.c_long), ("biClrUsed", wt.DWORD),
                ("biClrImportant", wt.DWORD)]


def shot(hwnd, out):
    r = wt.RECT()
    u32.GetClientRect(hwnd, ctypes.byref(r))
    w, h = r.right - r.left, r.bottom - r.top
    if w <= 0 or h <= 0:
        print("bad client rect %dx%d" % (w, h))
        return 1

    hdc = u32.GetDC(hwnd)
    mem = g32.CreateCompatibleDC(hdc)
    bmp = g32.CreateCompatibleBitmap(hdc, w, h)
    g32.SelectObject(mem, bmp)
    ok = u32.PrintWindow(hwnd, mem, PW_RENDERFULLCONTENT)

    bi = BITMAPINFOHEADER()
    bi.biSize = ctypes.sizeof(bi)
    bi.biWidth = w
    bi.biHeight = -h          # top-down
    bi.biPlanes = 1
    bi.biBitCount = 32
    bi.biCompression = 0
    buf = ctypes.create_string_buffer(w * h * 4)
    got = g32.GetDIBits(mem, bmp, 0, h, buf, ctypes.byref(bi), 0)

    g32.DeleteObject(bmp)
    g32.DeleteDC(mem)
    u32.ReleaseDC(hwnd, hdc)

    if not ok or got != h:
        print("PrintWindow ok=%d lines=%d" % (ok, got))
        return 1
    img = Image.frombuffer("RGBA", (w, h), buf.raw, "raw", "BGRA", 0, 1).convert("RGB")
    img.save(out)
    # 全黑检测
    small = img.resize((16, 16))
    px = list(small.getdata())
    print("%s  %dx%d  max=%s" % (out, w, h, max(max(p) for p in px)))
    return 0


if __name__ == "__main__":
    sys.exit(shot(int(sys.argv[1], 0), sys.argv[2]))
