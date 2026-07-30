#!/usr/bin/env python3
"""Controleert of de upload naar GitHub klopt: bestaat elk bestand, klopt de
grootte en klopt de inhoud (sha256)? Draait vanuit de hoofdmap van de repo
of vanuit weerbot-modellen; zoekt MANIFEST.txt zelf.

  python3 weerbot-modellen/controleer_upload.py
"""
import hashlib, sys
from pathlib import Path

hier = Path(__file__).resolve().parent
kandidaten = [hier / "MANIFEST.txt", hier.parent / "MANIFEST.txt", Path("MANIFEST.txt")]
manifest = next((p for p in kandidaten if p.exists()), None)
if manifest is None:
    print("MANIFEST.txt niet gevonden; upload dat bestand ook.")
    sys.exit(1)
wortel = manifest.parent

goed, fout, mist = [], [], []
for regel in manifest.read_text().splitlines():
    if not regel or regel.startswith("#"):
        continue
    h, n, pad = regel.split(None, 2)
    p = wortel / pad
    if not p.exists():
        mist.append(pad); continue
    b = p.read_bytes()
    if len(b) != int(n):
        fout.append(f"{pad}: {len(b)} bytes, verwacht {n}")
    elif hashlib.sha256(b).hexdigest()[:16] != h:
        fout.append(f"{pad}: zelfde grootte maar andere inhoud")
    else:
        goed.append(pad)

print(f"  in orde : {len(goed)}")
if mist:
    print(f"  ontbreekt: {len(mist)}")
    for p in mist: print(f"     {p}")
if fout:
    print(f"  FOUT    : {len(fout)}")
    for p in fout: print(f"     {p}")
if not mist and not fout:
    print("\n  Alles klopt. De upload is goed aangekomen.")
sys.exit(1 if (mist or fout) else 0)
