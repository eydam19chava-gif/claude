-- Arma el rig R6 de un enemigo HD importado. (Archivo generado: editá armar_r6_plantilla.lua.)
-- Uso: en Roblox Studio importá el .glb, seleccioná el Model importado, pegá esto en
-- View > Command Bar y apretá Enter.
--
-- Qué hace:
--   * Crea las partes R6 estándar (HumanoidRootPart, Torso, Head, Left/Right Arm, Left/Right Leg)
--     invisibles, del tamaño R6 por la escala del enemigo, en el lugar exacto de cada malla.
--   * Las une con los Motor6D estándar de R6 (RootJoint, Neck, Left/Right Shoulder, Left/Right Hip),
--     así funcionan las animaciones R6 normales (Animate de R6, caminar, atacar, etc.).
--   * Suelda cada malla a su parte con WeldConstraint. Las mallas quedan sin colisión, sin peso y con
--     RenderFidelity Automatic (rinden mejor en oleadas grandes). El "Arma" del gigante va al brazo derecho.
--   * Agrega un Humanoid con RigType R6.
-- Funciona aunque el modelo se haya importado movido, girado o escalado: las posiciones se sacan de
-- los centros de las propias mallas.

local DATOS = {
--DATOS--
}

local Selection = game:GetService("Selection")
local model = Selection:Get()[1]
assert(model and model:IsA("Model"), "Seleccioná el Model del enemigo importado")

local d
for nombre, v in DATOS do
	if string.find(model.Name, nombre, 1, true) then
		d = v
	end
end
assert(d, "El Model tiene que llamarse como el archivo (por ejemplo zombi_rapido_hd)")

local mallas = {}
for _, p in model:GetDescendants() do
	local n = string.gsub(p.Name, "_", " ") -- el .obj guarda "Right_Arm"; el .glb, "Right Arm"
	if p:IsA("MeshPart") and d.centros[n] then
		mallas[n] = p
	end
end
for _, n in { "Torso", "Head", "Left Arm", "Right Arm" } do
	assert(mallas[n], "Falta la malla " .. n)
end

-- marco del modelo: con los mismos 4 centros en el archivo y en Studio
local function marco(T, LA, RA, H)
	local x = (RA - LA).Unit
	local up = H - T
	up = (up - x * up:Dot(x)).Unit
	return CFrame.fromMatrix(T, x, up, x:Cross(up))
end
local c = d.centros
local E = marco(c["Torso"], c["Left Arm"], c["Right Arm"], c["Head"])
local W = marco(mallas["Torso"].Position, mallas["Left Arm"].Position, mallas["Right Arm"].Position, mallas["Head"].Position)
local k = (mallas["Right Arm"].Position - mallas["Left Arm"].Position).Magnitude / (c["Right Arm"] - c["Left Arm"]).Magnitude
local S = d.s * k -- studs por unidad R6

-- ubicación R6 estándar de cada parte (en el archivo el frente es +Z y la derecha -X)
local R6 = {
	HumanoidRootPart = { Vector3.new(0, 3, 0), Vector3.new(2, 2, 1) },
	Torso = { Vector3.new(0, 3, 0), Vector3.new(2, 2, 1) },
	Head = { Vector3.new(0, 4.5, 0), Vector3.new(2, 1, 1) },
	["Right Arm"] = { Vector3.new(-1.5, 3, 0), Vector3.new(1, 2, 1) },
	["Left Arm"] = { Vector3.new(1.5, 3, 0), Vector3.new(1, 2, 1) },
	["Right Leg"] = { Vector3.new(-0.5, 1, 0), Vector3.new(1, 2, 1) },
	["Left Leg"] = { Vector3.new(0.5, 1, 0), Vector3.new(1, 2, 1) },
}
local giro = E.Rotation:Inverse() * CFrame.Angles(0, math.pi, 0)

-- las mallas dejan libre su nombre para las partes R6
for n, m in mallas do
	m.Name = "Malla_" .. n
end

local partes = {}
for n, v in R6 do
	local p = Instance.new("Part")
	p.Name = n
	p.Size = v[2] * S
	local rel = E:PointToObjectSpace(v[1] * d.s) * k
	p.CFrame = W * CFrame.new(rel) * giro
	p.Transparency = 1
	p.CanCollide = (n == "HumanoidRootPart" or n == "Torso" or n == "Head")
	p.CanQuery = (n == "HumanoidRootPart")
	p.CanTouch = (n == "HumanoidRootPart")
	p.Anchored = false
	p.Parent = model
	partes[n] = p
end

local function motor(nombre, p0, p1, c0, c1)
	local m = Instance.new("Motor6D")
	m.Name = nombre
	m.Part0, m.Part1 = p0, p1
	m.C0, m.C1 = c0, c1
	m.Parent = p0
end
local function cf(x, y, z, ...)
	return CFrame.new(x * S, y * S, z * S, ...)
end
local P = partes
motor("RootJoint", P.HumanoidRootPart, P.Torso, cf(0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0), cf(0, 0, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0))
motor("Neck", P.Torso, P.Head, cf(0, 1, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0), cf(0, -0.5, 0, -1, 0, 0, 0, 0, 1, 0, 1, 0))
motor("Right Shoulder", P.Torso, P["Right Arm"], cf(1, 0.5, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0), cf(-0.5, 0.5, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0))
motor("Left Shoulder", P.Torso, P["Left Arm"], cf(-1, 0.5, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0), cf(0.5, 0.5, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0))
motor("Right Hip", P.Torso, P["Right Leg"], cf(1, -1, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0), cf(0.5, 1, 0, 0, 0, 1, 0, 1, 0, -1, 0, 0))
motor("Left Hip", P.Torso, P["Left Leg"], cf(-1, -1, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0), cf(-0.5, 1, 0, 0, 0, -1, 0, 1, 0, 1, 0, 0))

-- soldar cada malla a su parte y dejarla liviana
for n, m in mallas do
	local destino = P[n] or P["Right Arm"] -- "Arma" va al brazo derecho
	m.Anchored = false
	m.CanCollide = false
	m.CanQuery = false
	m.CanTouch = false
	m.Massless = true
	m.CollisionFidelity = Enum.CollisionFidelity.Box
	m.RenderFidelity = Enum.RenderFidelity.Automatic
	local w = Instance.new("WeldConstraint")
	w.Part0, w.Part1 = destino, m
	w.Parent = m
end

local hum = model:FindFirstChildOfClass("Humanoid") or Instance.new("Humanoid")
hum.RigType = Enum.HumanoidRigType.R6
hum.Parent = model
model.PrimaryPart = P.HumanoidRootPart
print(("Listo: %s armado como R6 (escala %.2f)"):format(model.Name, S))
