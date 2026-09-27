"""Arma modelos/todo_roblox.zip con torretas, puestos y mapa (glb con color + obj)."""
import glob
import os
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
out = "todo_roblox.zip"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    z.write("README.md", "todo/LEEME.md")
    for d in sorted(glob.glob("torreta_*/")) + sorted(glob.glob("puestos/puesto_*/")):
        n = os.path.basename(d.rstrip("/"))
        top = "torretas" if n.startswith("torreta") else "puestos"
        for ext in (".glb", ".obj", ".mtl", "_paleta.png"):
            f = os.path.join(d, n + ext)
            if os.path.exists(f):
                z.write(f, f"todo/{top}/{n}/{n}{ext}")
        if os.path.exists(os.path.join(d, "vista_frente.png")):
            z.write(os.path.join(d, "vista_frente.png"), f"todo/{top}/{n}/{n}_vista.png")
    for f in sorted(glob.glob("mapa/*.glb")) + ["mapa/mapa_completo.obj", "mapa/mapa_completo.mtl", "mapa/mapa_paleta.png"]:
        if os.path.exists(f):
            z.write(f, "todo/mapa/" + os.path.basename(f))
    for f in sorted(glob.glob("mapa/vista_*.png")):
        z.write(f, "todo/mapa/fotos/" + os.path.basename(f))
print(out, os.path.getsize(out) // (1024 * 1024), "MB,", len(zipfile.ZipFile(out).namelist()), "archivos")
