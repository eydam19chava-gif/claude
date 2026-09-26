# Torretas para el Tower Defense (Roblox)

5 torretas low-poly sci-fi, cada una con su base, su forma y su color de neón.
Todas apuntan hacia **+X** y están separadas en partes para poder animarlas en Roblox.

| # | Torreta | Rol sugerido | Neón | Triángulos | Partes |
|---|---------|--------------|------|-----------|--------|
| 1 | `torreta_ametralladora` | Disparo rápido, daño bajo | Verde | ~13.600 | Base, Pivot, Barrel, Laser |
| 2 | `torreta_canon` | Daño en área (artillería) | Naranja | ~10.200 | Base, Pivot, Barrel |
| 3 | `torreta_misiles` | Misiles teledirigidos | Rojo | ~7.500 | Base, Pivot, Barrel |
| 4 | `torreta_laser` | Rayo que perfora | Cian | ~6.500 | Base, Pivot, Barrel |
| 5 | `torreta_tesla` | Rayos en cadena | Violeta | ~6.800 | Base, Pivot |

Todas están por debajo del límite de **20.000 triángulos por malla** de Roblox.

## Partes
- **Base**: queda fija en el piso.
- **Pivot**: gira sobre el eje vertical para apuntar a los enemigos.
- **Barrel**: el cañón. Sube y baja (elevación) y retrocede al disparar.
- **Laser** (solo la ametralladora): la mira láser. Podés borrarla y usar un `Beam` en su lugar.

## Archivos de cada carpeta
- `.obj` + `.mtl`: el formato que pediste. Los colores van en el `.mtl`.
- `.fbx`: **recomendado para Roblox**, porque mantiene mejor las partes, la jerarquía y los materiales.
- `.glb`: alternativa moderna, también compatible con el importador de Roblox.
- `.blend`: para abrir y editar en Blender.
- `.py`: el script que genera el modelo. Se puede volver a correr para modificarlo.
- `vista_*.png`: vistas previas.

## Importar en Roblox Studio
1. **Home → Import 3D** (o **Avatar → Import 3D**, según la versión).
2. Elegí el `.fbx`, o el `.obj` si preferís ese formato.
3. En las opciones del importador:
   - Si aparece la opción **Merge Meshes**, dejala desactivada para que cada parte venga separada.
   - Si queda muy chica o muy grande, ajustá **Scale**. El modelo mide unos 4–5 studs de alto.
4. Se importa como un `Model` con un `MeshPart` por parte (Base, Pivot, Barrel).
5. Los neones: poné en esas partes el material **Neon** de Roblox, o agregá un `PointLight` para que brillen de verdad.

## Animar (idea base en Luau)
```lua
-- Pivot gira hacia el enemigo (solo en Y); Barrel sigue al Pivot.
local pivot = turret.Pivot
local base = turret.Base
local function aim(target)
    local pos = pivot.Position
    local look = Vector3.new(target.Position.X, pos.Y, target.Position.Z)
    pivot.CFrame = CFrame.lookAt(pos, look) * CFrame.Angles(0, math.rad(90), 0) -- el modelo apunta a +X
end
```
Para que las partes se muevan juntas, uní `Pivot` a `Base` con un `Motor6D` y `Barrel` a `Pivot` con otro, y animá sus `C0`.

## Regenerar o modificar
Con Blender instalado:
```bash
blender --background --python torreta_canon/torreta_canon.py
```
O en Python con `pip install bpy`:
```bash
python torreta_canon/torreta_canon.py
```
Variables opcionales: `NO_RENDER=1` (solo exporta), `SAMPLES=64`, `RES=900`.
