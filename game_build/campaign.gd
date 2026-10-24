extends Node3D
const Player = preload("res://scripts/survivor.gd")
const Enemy = preload("res://scripts/ghoul.gd")
var player: CharacterBody3D
var stage := 0
var wave := 0
var credits := 0
var level := 0
var xp := 0
var cleared := 0
var ended := false
var paused := false
var intermission := 8.0
var pending := 0
var spawn_clock := 0.0
var hit_flash := 0.0
var hurt_flash := 0.0
var arena: Node3D
var loot: Array = []
var spawn_point := Vector3.ZERO
var status := ""
var ui: Label
var center: Label
var panel: VBoxContainer
var crosshair: Label
var overlay: ColorRect
var transition := false

func _ready() -> void:
	load_profile()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.32,0.44,0.58)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.75,0.8,0.9)
	env.ambient_light_energy = 0.65
	var world := WorldEnvironment.new()
	world.environment = env
	add_child(world)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-45,-30,0)
	sun.light_energy = 1.1
	sun.shadow_enabled = true
	add_child(sun)
	player = Player.new()
	player.game = self
	add_child(player)
	build_ui()
	load_stage()

func build_ui() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)
	var font := SystemFont.new()
	font.font_names = PackedStringArray(["Segoe UI","Arial"])
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	canvas.add_child(root)
	var theme := Theme.new()
	theme.default_font = font
	theme.default_font_size = 20
	root.theme = theme
	ui = Label.new()
	ui.position = Vector2(24,20)
	ui.add_theme_color_override("font_shadow_color",Color.BLACK)
	ui.add_theme_constant_override("shadow_offset_x",2)
	ui.add_theme_constant_override("shadow_offset_y",2)
	root.add_child(ui)
	center = Label.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	center.position = Vector2(-310,75)
	root.add_child(center)
	crosshair = Label.new()
	crosshair.text = "+"
	crosshair.add_theme_font_size_override("font_size",30)
	crosshair.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	crosshair.position = Vector2(-10,-20)
	root.add_child(crosshair)
	panel = VBoxContainer.new()
	panel.position = Vector2(24,240)
	root.add_child(panel)
	for i in range(1,4):
		var button := Button.new()
		button.text = "Buy %s — %d credits" % [Player.GUNS[i].name,Player.GUNS[i].price]
		button.pressed.connect(buy.bind(i))
		panel.add_child(button)
	for entry in [["Refill ammo — 120",0],["Medkit — 100",1],["Permanent damage rank — 250",2],["Continue / Resume",3],["Restart campaign",4]]:
		var button := Button.new()
		button.text = entry[0]
		button.pressed.connect(shop_action.bind(entry[1]))
		panel.add_child(button)
	panel.hide()
	overlay = ColorRect.new()
	overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	overlay.color = Color(0.7,0,0,0)
	root.add_child(overlay)

func load_stage() -> void:
	if is_instance_valid(arena):
		arena.free()
	for enemy in get_tree().get_nodes_in_group("enemies"):
		enemy.queue_free()
	for item in loot:
		if is_instance_valid(item.node): item.node.queue_free()
	loot.clear()
	arena = Node3D.new()
	add_child(arena)
	var path := "res://assets/map/walc.glb" if stage == 0 else "res://assets/map/beering.glb"
	var packed := load(path) as PackedScene
	var building := packed.instantiate() as Node3D
	arena.add_child(building)
	var bounds := AABB()
	var first := true
	for mesh in building.find_children("*","MeshInstance3D",true,false):
		if not mesh.mesh: continue
		var box: AABB = mesh.global_transform * mesh.get_aabb()
		bounds = box if first else bounds.merge(box)
		first = false
		mesh.create_trimesh_collision()
	# Only translate a stage to local space; preserve all mesh dimensions and relative transforms.
	if stage == 0:
		building.position = Vector3.ZERO
		spawn_point = Vector3(-10,0.4,0)
	else:
		var mid := bounds.get_center()
		building.position = Vector3(-mid.x,-bounds.position.y,-mid.z)
		spawn_point = Vector3(0,0.4,bounds.size.z*0.5+12)
	var floor_body := StaticBody3D.new()
	var floor_shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(100,0.4,100)
	floor_shape.shape = box
	floor_body.position = spawn_point+Vector3(0,-0.6,0)
	floor_body.add_child(floor_shape)
	arena.add_child(floor_body)
	var floor_mesh := MeshInstance3D.new()
	var floor_box := BoxMesh.new()
	floor_box.size = box.size
	floor_mesh.mesh = floor_box
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.25,0.28,0.3)
	floor_mesh.material_override = mat
	floor_body.add_child(floor_mesh)
	respawn_player()
	wave = 0
	intermission = 10
	player.health = 100
	status = "WALC: survive 5 rounds" if stage == 0 else "Beering Hall: survive 5 rounds"

func respawn_player() -> void:
	player.position = spawn_point
	player.velocity = Vector3.ZERO
	player.rotation.y = -PI/2 if stage == 0 else 0.0

func _process(delta: float) -> void:
	if not is_instance_valid(player): return
	hit_flash = maxf(0,hit_flash-delta)
	hurt_flash = maxf(0,hurt_flash-delta)
	overlay.color.a = hurt_flash*0.6
	crosshair.modulate = Color.GOLD if hit_flash > 0 else Color.WHITE
	ui.text = "%s  |  ROUND %d / 5\nHEALTH %d    %s  %d / %d %s\nCredits %d    XP %d    Damage rank %d\n%s\nWASD move · Shift sprint · Space jump · RMB aim · R reload\n1–4 weapons · E supply menu between rounds · Esc pause" % ["WALC" if stage==0 else "BEERING",wave,maxi(0,int(player.health)),Player.GUNS[player.gun].name,player.ammo[player.gun],player.reserve[player.gun],"RELOADING" if player.reload_time>0 else "",credits,xp,level,status]
	if paused or ended: return
	if intermission > 0:
		intermission -= delta
		center.text = "Next round in %d — E: supplies" % ceili(intermission)
		if intermission <= 0:
			wave += 1
			pending = 4+wave*2+stage*4
			status = "Clear the wave"
		return
	center.text = "Enemies remaining: %d" % (pending+get_tree().get_nodes_in_group("enemies").size())
	spawn_clock -= delta
	if pending > 0 and spawn_clock <= 0:
		spawn_enemy()
		pending -= 1
		spawn_clock = 1.1
	if pending == 0 and get_tree().get_nodes_in_group("enemies").is_empty():
		credits += 100+wave*25
		xp += 50
		save_profile()
		if wave == 5:
			if stage == 0:
				stage = 1
				cleared = maxi(cleared,1)
				load_stage()
			else:
				cleared = 2
				finish(true)
		else:
			intermission = 15
			status = "Round cleared — supplies available"
	for item in loot.duplicate():
		item.node.rotate_y(delta)
		if item.node.global_position.distance_to(player.global_position+Vector3.UP)<1.8:
			match item.type:
				0: player.health = minf(100,player.health+35)
				1:
					for i in range(4): player.reserve[i] += Player.GUNS[i].clip
				2: credits += 100
				3: player.damage_boost = 20
			status = ["Medkit +35 HP","Ammo cache collected","Salvage +100 credits","Overdrive: damage boosted 20 seconds"][item.type]
			item.node.queue_free()
			loot.erase(item)

func spawn_enemy() -> void:
	var enemy := Enemy.new()
	enemy.game = self
	enemy.kind = randi_range(0,2) if wave >= 3 else 0
	enemy.health = (55+wave*12+stage*15)*(2 if enemy.kind==2 else 1)
	enemy.speed = 3.6 if enemy.kind==1 else 2.1
	add_child(enemy)
	var angle := randf()*TAU
	enemy.position = spawn_point+Vector3(cos(angle)*18,0.5,sin(angle)*18)

func enemy_killed(pos: Vector3) -> void:
	credits += 25
	xp += 10
	if randf() < 0.45:
		var type := randi_range(0,3)
		var node := MeshInstance3D.new()
		var mesh := BoxMesh.new()
		mesh.size = Vector3(0.45,0.45,0.45)
		node.mesh = mesh
		var mat := StandardMaterial3D.new()
		mat.albedo_color = [Color.LIME_GREEN,Color.CORNFLOWER_BLUE,Color.GOLD,Color.MAGENTA][type]
		mat.emission_enabled = true
		mat.emission = mat.albedo_color*0.3
		node.material_override = mat
		add_child(node)
		node.position = pos+Vector3.UP*0.7
		loot.append({"node":node,"type":type})

func use_station() -> void:
	if intermission > 0 or ended: toggle_pause()
func toggle_pause() -> void:
	paused = not paused
	panel.visible = paused
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE if paused else Input.MOUSE_MODE_CAPTURED
func buy(index: int) -> void:
	if ended or intermission <= 0: return
	if index in player.owned or credits < Player.GUNS[index].price: return
	credits -= Player.GUNS[index].price
	player.owned.append(index)
	player.gun = index
func shop_action(action: int) -> void:
	if action == 4:
		get_tree().reload_current_scene()
		return
	if action == 3:
		if not ended: toggle_pause()
		return
	if ended or intermission <= 0: return
	if action == 0 and credits >= 120:
		credits -= 120
		for i in range(4): player.reserve[i] += Player.GUNS[i].clip*3
	if action == 1 and credits >= 100:
		credits -= 100
		player.health = 100
	if action == 2 and xp >= 250 and level < 10:
		xp -= 250
		level += 1
		save_profile()
func finish(won: bool) -> void:
	ended = true
	status = "Campaign complete — both buildings cleared" if won else "Overrun — restart to try again"
	center.text = status
	save_profile()
	panel.show()
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
func save_profile() -> void:
	var file := FileAccess.open("user://survival_profile.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"xp":xp,"level":level,"cleared":cleared}))
func load_profile() -> void:
	if FileAccess.file_exists("user://survival_profile.json"):
		var data = JSON.parse_string(FileAccess.get_file_as_string("user://survival_profile.json"))
		if data is Dictionary:
			xp = int(data.get("xp",0))
			level = int(data.get("level",0))
			cleared = int(data.get("cleared",0))
