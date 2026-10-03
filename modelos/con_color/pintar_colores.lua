-- Pegar en Roblox Studio: View > Command Bar, y apretar Enter (después de importar los modelos de con_color/).
-- Pinta cada pieza con el color que tiene en el nombre: "Torso__1A6BFF" -> Color = #1A6BFF.
-- Las que terminan en "_N" (las que brillan) quedan en Neon.
-- Si seleccionás un modelo antes de ejecutarlo, pinta solo ese; si no, todo el Workspace.

local Selection = game:GetService("Selection")
local root = Selection:Get()[1] or workspace
local total = 0

for _, part in root:GetDescendants() do
	if part:IsA("MeshPart") then
		local hex, neon = string.match(part.Name, "__(%x%x%x%x%x%x)(_?N?)")
		if hex then
			part.TextureID = ""
			part.Color = Color3.fromHex("#" .. hex)
			part.Material = (neon == "_N") and Enum.Material.Neon or Enum.Material.SmoothPlastic
			part.RenderFidelity = Enum.RenderFidelity.Precise
			total += 1
		end
	end
end

print(("Listo: %d piezas pintadas en %s"):format(total, root:GetFullName()))
