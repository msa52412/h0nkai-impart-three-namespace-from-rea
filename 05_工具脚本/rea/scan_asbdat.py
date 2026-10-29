# -*- coding: utf-8 -*-
import os
p = r"C:/Users/Administrator/AppData/LocalLow/miHoYo/Honkai Impact 3/StreamingAsb/pc/asb.dat"
data = open(p, "rb").read()
print("asb.dat %d 字节" % len(data))
print("前64B:", data[:64].hex())
print("含 'CAB-' :", data.count(b"CAB-"))
print("含 'settingicon':", b"settingicon" in data)
print("含 'f65865df' :", b"f65865df" in data)
print("含 'UnityFS' :", data.count(b"UnityFS"))
