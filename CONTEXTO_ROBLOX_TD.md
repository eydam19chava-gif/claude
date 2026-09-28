# Contexto: juego Roblox "rpg de defensa de torre" (placeId 139992564356539)

## Conexión (PC Windows del usuario "eydam")
- Roblox Studio MCP: `%LOCALAPPDATA%\Roblox\mcp.bat` → supergateway en puerto **8000** (`/mcp`, streamableHttp, --stateful) → cloudflared quick tunnel → conector claude.ai "roblox estudio".
- Blender MCP: `C:\Users\eydam\.local\bin\uvx.exe --python 3.11 mcp-for-blender` (env `UV_PYTHON_PREFERENCE=only-managed`) → supergateway puerto **8001** → cloudflared → conector "blender".
- Usar `--sessionTimeout 86400000` en supergateway para que no se caiga la sesión.
- La URL de trycloudflare cambia cada vez que se reinicia el túnel: hay que actualizar el conector (terminada en `/mcp`).
- OJO: el plugin MCP de Roblox restaura `workspace.Camera.CameraType` al valor que tenía antes de cada llamada. Si queda en `Scriptable`, el clic derecho no gira la cámara en Studio: arreglar a mano (Workspace → Camera → CameraType = Fixed).

## Cambios ya hechos en Roblox (mapa)
- Mapa hexagonal: 6 islas (1 Tropical, 2 Bosque, 3 Nieve, 4 Desierto, 5 Volcán, 6 Cristal) + plaza central. Las islas 2-6 son la isla 1 girada 60° × (índice-1).
- `Workspace.Scene` escalado de 3.52 a **1.76** (mapa ~893×941 studs, islas ~246). Duplicado movido a `ServerStorage.Scene_Respaldo_Original`.
- Torretas (plantillas en `ReplicatedStorage.PlantillasTorretas` y vitrina en Workspace) escaladas a ~2.9 studs de alto (personaje = 5.83).
- `TorretasConfig.MEDIO_ANCHO_CAMINO` = 5.75.
- `ShopVisuals` y `RoofFix` DESACTIVADOS (usaban medidas fijas del mapa grande). Las tiendas decoradas están horneadas en `Scene.TiendasMejoradas`. Las casas quedaron con su techo original (el usuario no quiere techo superpuesto; el mesh de la casa es una sola pieza y trae un frontón torcido: solo se puede arreglar editando el mesh en Blender).
- Caminos nuevos en `Scene.CaminosNuevos` (piso de 10 studs, bordillos, 15 faroles por isla, estilo por isla). Waypoints `IslaN_Waypoint_XX` y `Bordes` originales ocultos (Transparency 1), los scripts siguen usando la posición de los waypoints.
- Pendiente de decidir: velocidad de zombis (10) y alcances de torretas (22-60) ahora son grandes para el mapa más chico.

## Modelos en Blender (C:\Users\eydam\Desktop\EdificiosTD\, todo en EdificiosTD.blend)
Piezas nombradas `Modelo_Material` para poner colores en Roblox después.
- `EdificiosTD.fbx`: TorreVigia, Cuartel, PortonFortaleza, TorreMago, Herreria, BastionCanon.
- `Volcan.fbx` (roca + ríos de lava → Neon naranja), `ArbolSecoAlto.fbx`, `ArbolSecoRetorcido.fbx` (isla volcán).
- `Cactus.fbx` (5 cactus versión simple) y `Piramide.fbx` (maya, 9 niveles, isla desierto).
- `Cactus\Cactus_1_Saguaro.fbx`: cactus 1 rehecho con detalle (costillas marcadas, aréolas blancas con racimo de 4 púas). El usuario quiere los cactus **uno por uno** con ese nivel de detalle.
- Isla nieve: 3 árboles de hielo ya creados en Blender (Nieve_ArbolHielo_1..3, colección NieveArbolesHielo), sin exportar.
- Ningún FBX se importó todavía en Roblox (lo hace el usuario con Importar 3D).

## Pendiente (el usuario quiere detalle, uno por uno, con captura de cada uno)
1. Árboles frondosos (tronco café con raíces, copa de "nubes" verdes en 2 tonos) – varias variantes.
2. Pinos cartoon (capas de ramas en punta caídas, 2 tonos, tronco café) – varias variantes.
3. Hongos (sombrero rojo brillante, borde blanco con escamas, tallo blanco) – varias variantes.
4. Rocas cartoon (caras planas, bordes claros, grietas) – **al menos 20**, con paletas para cada isla.
5. Cactus 2 al 5 con el nivel de detalle del cactus 1.
6. Isla nieve: 3 pinos nevados, muñeco de nieve detallado (sombrero de copa, bufanda, zanahoria, pipa, carbón, brazos de rama), iglú de bloques de hielo con túnel.
7. Después: importar en Roblox, colorear por nombre y ubicar en las islas.
