-- Pegar en Roblox Studio: View > Command Bar, y apretar Enter.
-- Arregla lo importado desde los .glb:
--   * RenderFidelity = Precise: Roblox no simplifica las mallas con la distancia (si no, desaparecen detalles).
--   * Anchored = true: nada se cae.
--   * Los waypoints quedan invisibles y sin colisión.
--   * Las piezas chicas de decoración no chocan (mejor rendimiento).
-- Si seleccionás un modelo antes de ejecutarlo, arregla solo ese; si no, todo el Workspace.

local Selection = game:GetService("Selection")
local root = Selection:Get()[1] or workspace
local total = 0

for _, part in root:GetDescendants() do
	if part:IsA("MeshPart") then
		part.RenderFidelity = Enum.RenderFidelity.Precise
		part.Anchored = true
		local name = part.Name
		if string.find(name, "Waypoint") then
			part.Transparency = 1
			part.CanCollide = false
			part.CanQuery = false
			part.CastShadow = false
		elseif string.find(name, "Nubes") or string.find(name, "Arboles") or string.find(name, "Plantas")
			or string.find(name, "Rocas") or string.find(name, "Detalles") then
			part.CanCollide = false
			part.CollisionFidelity = Enum.CollisionFidelity.Box
		end
		total += 1
	end
end

print(("Listo: %d mallas arregladas en %s"):format(total, root:GetFullName()))
