-- Colores y materiales para torreta_laser (generado automáticamente).
-- Uso: poné este Script dentro del Model importado, o seleccioná el Model
-- y pegá el código en la barra de comandos (View > Command Bar).
local COLORES = {
	["Barrel_Blindaje"] = {237, 239, 243, Enum.Material.SmoothPlastic},
	["Barrel_Blindaje_Claro"] = {97, 104, 123, Enum.Material.SmoothPlastic},
	["Barrel_Cristal"] = {90, 230, 255, Enum.Material.Neon},
	["Barrel_Metal_Gris"] = {123, 128, 138, Enum.Material.Metal},
	["Barrel_Metal_Oscuro"] = {56, 58, 62, Enum.Material.SmoothPlastic},
	["Barrel_Neon"] = {65, 237, 255, Enum.Material.Neon},
	["Base_Blindaje"] = {237, 239, 243, Enum.Material.SmoothPlastic},
	["Base_Blindaje_Claro"] = {97, 104, 123, Enum.Material.SmoothPlastic},
	["Base_Metal_Oscuro"] = {56, 58, 62, Enum.Material.SmoothPlastic},
	["Base_Neon"] = {65, 237, 255, Enum.Material.Neon},
	["Pivot_Blindaje"] = {237, 239, 243, Enum.Material.SmoothPlastic},
	["Pivot_Blindaje_Claro"] = {97, 104, 123, Enum.Material.SmoothPlastic},
	["Pivot_Cristal"] = {90, 230, 255, Enum.Material.Neon},
	["Pivot_Metal_Gris"] = {123, 128, 138, Enum.Material.Metal},
	["Pivot_Metal_Oscuro"] = {56, 58, 62, Enum.Material.SmoothPlastic},
	["Pivot_Neon"] = {65, 237, 255, Enum.Material.Neon},
}

local model = if script then script.Parent else game:GetService("Selection"):Get()[1]
local grupos = {}
for _, part in model:GetDescendants() do
	if part:IsA("MeshPart") then
		local c = COLORES[part.Name]
		if c then
			part.Color = Color3.fromRGB(c[1], c[2], c[3])
			part.Material = c[4]
		end
		-- soldar cada pieza a la primera de su grupo (Base / Pivot / Barrel / Laser)
		local grupo = string.match(part.Name, "^(%a+)_")
		if grupo then
			if grupos[grupo] then
				local w = Instance.new("WeldConstraint")
				w.Part0, w.Part1 = grupos[grupo], part
				w.Parent = part
			else
				grupos[grupo] = part
			end
		end
	end
end
if grupos.Base then grupos.Base.Anchored = true end
print("Torreta lista:", model.Name)
