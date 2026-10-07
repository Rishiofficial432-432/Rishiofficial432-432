#!/usr/bin/env python3
"""
Prepare portrait photo for clean ASCII conversion:
1. Isolate the subject from dark/background border
2. Smooth texture while preserving facial edges
3. Enhance contrast & stretch tones so face and features are crisp
"""
import os
import sys
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "avatar.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

def prep(inp_path, out_path):
    im = Image.open(inp_path).convert("L")
    w, h = im.size
    
    # In avatar.png, the avatar is a circular photo on black background
    # We mask out the dark outside of the circle to pure white (255)
    cx, cy = w / 2.0, h / 2.0
    r = min(w, h) / 2.0 - 2.0
    
    px = im.load()
    for y in range(h):
        for x in range(w):
            if (x - cx)**2 + (y - cy)**2 > r**2:
                px[x, y] = 255
            elif px[x, y] > 225:
                # Force very light background areas to white
                px[x, y] = 255

    # Gentle unsharp mask to accentuate eyes, eyebrows, nose, mouth lines
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=160, threshold=3))
    
    # Save prepped image
    im.save(out_path)
    print(f"Prepped photo written to {out_path} ({w}x{h})")

if __name__ == "__main__":
    prep(INP, OUT)
