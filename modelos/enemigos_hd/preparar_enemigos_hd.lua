-- Pegar en Roblox Studio: View > Command Bar, con el enemigo HD importado SELECCIONADO, y apretar Enter.
-- Deja el modelo listo para oleadas grandes (muchos enemigos a la vez):
--   * Las mallas NO chocan ni reciben toques/raycasts: la física usa una sola caja invisible ("Hitbox").
--     Con 20.000 triángulos por enemigo, dejar la colisión en las mallas es lo que más baja el rendimiento.
--   * CollisionFidelity = Box: aunque algo las active después, el colisionador es una caja, no la malla.
--   * RenderFidelity = Automatic: Roblox baja el detalle de los enemigos lejanos (al revés que en el mapa).
--   * Massless: las mallas no suman peso; el Hitbox es la parte principal (PrimaryPart).
--   * Sin sombras en las piezas chicas (dientes, pernos, cadenas...), que no se notan y cuestan.
-- No crea las uniones de animación: uní cada parte al Torso con Motor6D (ver README).

local Selection = game:GetService("Selection")
local model = Selection:Get()[1]
assert(model and model:IsA("Model"), "Seleccioná el Model del enemigo importado")

local meshes = {}
for _, d in model:GetDescendants() do
	if d:IsA("MeshPart") then
		table.insert(meshes, d)
	end
end
assert(#meshes > 0, "El modelo no tiene MeshParts")

for _, m in meshes do
	m.CanCollide = false
	m.CanTouch = false
	m.CanQuery = false
	m.Massless = true
	m.Anchored = false
	m.CollisionFidelity = Enum.CollisionFidelity.Box
	m.RenderFidelity = Enum.RenderFidelity.Automatic
	if m.Size.Magnitude < 1 then
		m.CastShadow = false
	end
end

-- caja de colisión única del tamaño del enemigo
local cf, size = model:GetBoundingBox()
local hitbox = model:FindFirstChild("Hitbox") or Instance.new("Part")
hitbox.Name = "Hitbox"
hitbox.Size = size
hitbox.CFrame = cf
hitbox.Transparency = 1
hitbox.CanCollide = true
hitbox.CanQuery = true
hitbox.CanTouch = true
hitbox.CastShadow = false
hitbox.Anchored = false
hitbox.Parent = model
model.PrimaryPart = hitbox

-- pegar el Torso al Hitbox (el resto se une al Torso con Motor6D para animar)
local torso = model:FindFirstChild("Torso", true)
if torso and not hitbox:FindFirstChild("RootJoint") then
	local j = Instance.new("Motor6D")
	j.Name = "RootJoint"
	j.Part0 = hitbox
	j.Part1 = torso
	j.C0 = hitbox.CFrame:ToObjectSpace(torso.CFrame)
	j.Parent = hitbox
end

print(("Listo: %s — %d mallas sin colisión, Hitbox %s"):format(model.Name, #meshes, tostring(size)))
