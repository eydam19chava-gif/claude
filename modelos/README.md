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

# Mapa (`mapa/`)
6 **islas flotantes**, una por jugador, alrededor de una **isla central** con la máquina de la **palanca**. Cada isla está unida al centro por un puente colgante.

**Zona de torretas libre:** a cada lado del camino hay una franja de 9 unidades sin árboles, rocas ni decoración; los monumentos y los puestos están lejos del camino.

**Todas las islas son justas:** tienen exactamente el mismo camino (mismo largo y mismos waypoints), el mismo lugar para torretas y los mismos espacios. Solo cambian el tema y la decoración.

| Isla | Tema | Monumento | Cascada |
|------|------|-----------|---------|
| 1 | Tropical | Molino | Agua |
| 2 | Bosque | Árbol gigante | Agua |
| 3 | Nieve | Iglú + muñeco de nieve | Hielo |
| 4 | Desierto | Pirámide con obeliscos | Agua |
| 5 | Volcán | Volcán con lava | Lava |
| 6 | Cristal | Cristal gigante flotante | Energía |

Cada isla tiene:
- **Portal-cueva** donde aparecen los enemigos (lado de afuera).
- **Camino en zigzag** con bordillos y faroles, con lugar libre a los costados para poner torretas.
- **Casa base** con el **cristal de vida** flotando arriba (lo que atacan los enemigos), cerca y bandera del color del jugador.
- **Zona de base con los 5 puestos** (los mismos modelos de `puestos/`, en el mismo lugar en todas las islas): `..._Palanca_*` (consola, brazo y 5 pedestales), `..._Tienda_*`, `..._Equipamientos_*`, `..._Diario_*` y `..._Mejoras_*` (con `Panel_Suerte` y `Panel_Giros`).
- **Waypoints**: cubitos `Isla<N>_Waypoint_01`, `_02`, ... sobre el camino, en orden desde el portal hasta la casa. En Roblox ponelos con `Transparency = 1`, `CanCollide = false` y `Anchored = true`, y usalos para que los enemigos caminen de uno a otro.
- Roca colgante debajo, rocas flotando, 2 islotes y una cascada que cae al vacío.

La isla central tiene una fuente, faroles y **6 carteles TOP** (Oleadas, Enemigos, Giros, Torretas, Monedas, Tiempo). Cada cartel tiene:
- una pantalla aparte (`Centro_Top_<Categoria>_Pantalla`) para ponerle un `SurfaceGui` con la tabla;
- un **pedestal** adelante para la estatua del jugador #1 de esa categoría.

Archivos:
- `mapa_completo.glb`: todo el mapa en un archivo, con color.
- `mapa_completo.obj` + `.mtl` + `mapa_paleta.png`: el mapa en OBJ (el color va en el PNG).
- `Centro.glb`, `Nubes.glb` e `Isla1_Tropical.glb` ... `Isla6_Cristal.glb`: cada parte por separado, por si preferís importarlas de a una (más liviano).
- `mapa.blend`: para editar en Blender.

Todas las piezas tienen menos de 20.000 triángulos. Después de importar, marcá todo como `Anchored`.

# Puestos (`puestos/`)
Modelos sueltos para poner donde quieras. Todos miran hacia **-Y** (el jugador se para de ese lado). Cada uno tiene su `.glb` con color en su carpeta y una copia en `roblox/`.

| Modelo | Para qué | Partes para programar |
|--------|----------|------------------------|
| `puesto_palanca` | Girar gratis ("Rodar") | `Consola` (ponele el `ProximityPrompt`), `Palanca_Brazo` (rota al tirar, el eje está en su origen), `Pedestal_1` ... `Pedestal_5` (ahí aparecen las torretas que salen), `Zona` (piso, vitrinas y faroles) |
| `puesto_tienda` | Tienda | `Puesto`, `Vendedor`, `Cartel` (para el `SurfaceGui` con "Tienda") |
| `puesto_equipamientos` | Comprar aceite y mejoras de máquina | `Puesto` (latas y barriles de aceite, engranaje), `Vendedor`, `Cartel` |
| `puesto_diario` | Recompensa diaria / por unirse al grupo y dar like | `Base` (con corazón y estrella), `Regalo` (se puede animar saltando), `Cartel` |
| `puesto_mejoras` | Mejoras de "Suerte de tirada" y "Giros" | `Marco`, `Iconos` (trébol y dado), `Panel_Suerte` y `Panel_Giros` (un `SurfaceGui` en cada uno) |

El script `puestos/puestos.py` los genera. Para regenerar uno solo: `python puestos.py puesto_tienda`.
