# Torretas para el Tower Defense (Roblox)

Torretas low-poly sci-fi, cada una con su base, su forma y su color de neón.
Todas apuntan hacia **+X** y están separadas en partes para poder animarlas en Roblox.

## Para Roblox: carpeta `roblox/`
Tiene **un solo archivo `.glb` por torreta**, con los colores incluidos.
1. En Roblox Studio: **Home → Import 3D** (o **Avatar → Import 3D**, según la versión).
2. Elegí el `.glb` de la torreta.
3. Listo: viene con color, porque el color está en una textura dentro del mismo archivo.

¿Por qué no OBJ? Un `.obj` solo **no guarda colores**. El color va en un `.mtl` y en una imagen aparte, y Roblox no los aplica al importar, por eso se veía gris. Igual cada torreta tiene su OBJ en su carpeta (ver abajo) por si lo necesitás en otro programa.

## Lista
| # | Torreta | Rol sugerido | Neón | Triángulos | Partes |
|---|---------|--------------|------|-----------|--------|
| 1 | `torreta_ametralladora` | Disparo rápido | Verde | ~13.600 | Base, Pivot, Barrel, Laser |
| 2 | `torreta_canon` | Daño en área | Naranja | ~10.200 | Base, Pivot, Barrel |
| 3 | `torreta_misiles` | Misiles teledirigidos | Rojo | ~7.500 | Base, Pivot, Barrel |
| 4 | `torreta_laser` | Rayo que perfora | Cian | ~6.500 | Base, Pivot, Barrel |
| 5 | `torreta_tesla` | Rayos en cadena | Violeta | ~6.800 | Base, Pivot |
| 6 | `torreta_lanzallamas` | Quemadura | Naranja fuego | ~5.400 | Base, Pivot, Barrel |
| 7 | `torreta_criogenica` | Ralentiza / congela | Celeste | ~4.500 | Base, Pivot, Barrel |
| 8 | `torreta_francotirador` | Alcance enorme, crítico | Amarillo | ~4.800 | Base, Pivot, Barrel |
| 9 | `torreta_mortero` | Disparo parabólico en área | Verde lima | ~5.200 | Base, Pivot, Barrel |
| 10 | `torreta_gatling` | DPS altísimo | Dorado | ~3.500 | Base, Pivot, Barrel, Spinner |
| 11 | `torreta_colmena` | Lanza drones | Amarillo/negro | ~3.900 | Base, Pivot (drones orbitando) |
| 12 | `torreta_mech` | Robot bípedo, doble cañón | Verde azulado/rojo | ~7.600 | Base, Pivot, Barrel |
| 13 | `torreta_ballesta` | Virote que atraviesa | Magenta | ~4.800 | Base, Pivot, Barrel |
| 14 | `torreta_sonica` | Aturde / empuja | Blanco/rosa | ~4.700 | Base, Pivot, Barrel |
| 15 | `torreta_acido` | Veneno, corroe armadura | Verde tóxico | ~5.600 | Base, Pivot, Barrel |

Todas están por debajo del límite de **20.000 triángulos por malla** de Roblox.

## Partes
- **Base**: queda fija en el piso.
- **Pivot**: gira sobre el eje vertical para apuntar a los enemigos.
- **Barrel**: el cañón. Sube y baja y retrocede al disparar.
- **Spinner** (gatling): los 6 cañones que giran al disparar.
- En la **colmena**, el `Pivot` es el anillo con los drones: hacelo girar constante.
- **Laser** (ametralladora): la mira láser. Podés borrarla y usar un `Beam` en su lugar.

Consejo: después de importar, podés poner en **Neon** las partes que quieras que brillen, o agregarles un `PointLight`.

## Archivos de cada carpeta `torreta_*/`
- `.glb`: el mismo de `roblox/` (un archivo, con color).
- `.obj` + `.mtl` + `_paleta.png`: versión OBJ. El color está en el PNG.
- `.fbx`: con la textura incrustada.
- `.blend`: para abrir y editar en Blender, con los materiales originales y los brillos.
- `.py`: el script que genera el modelo. Se puede volver a correr para modificarlo.
- `vista_*.png`: vistas previas.

## Animar (idea base en Luau)
```lua
-- Pivot gira hacia el enemigo (solo en Y). El modelo apunta a +X.
local function aim(pivot, target)
    local pos = pivot.Position
    local look = Vector3.new(target.Position.X, pos.Y, target.Position.Z)
    pivot.CFrame = CFrame.lookAt(pos, look) * CFrame.Angles(0, math.rad(90), 0)
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
