extends CharacterBody3D

const GUNS = [
	{"name":"Sidearm", "damage":32.0,"rate":0.24,"clip":12,"reload":1.2,"pellets":1,"spread":0.008,"price":0},
	{"name":"Carbine", "damage":26.0,"rate":0.10,"clip":30,"reload":1.7,"pellets":1,"spread":0.015,"price":350},
	{"name":"Pump shotgun", "damage":18.0,"rate":0.85,"clip":6,"reload":2.2,"pellets":8,"spread":0.075,"price":600},
	{"name":"Marksman rifle", "damage":110.0,"rate":0.65,"clip":8,"reload":1.9,"pellets":1,"spread":0.002,"price":850}
]
var game: Node3D
var health := 100.0
var gun := 0
var owned := [0]
var ammo := [12,30,6,8]
var reserve := [60,90,24,32]
var cooldown := 0.0
var reload_time := 0.0
var damage_boost := 0.0
var aim := false
var camera: Camera3D
var model: MeshInstance3D
var muzzle: OmniLight3D
var flash := 0.0

func _ready() -> void:
	var shape := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.35
	capsule.height = 1.8
	shape.shape = capsule
	shape.position.y = 0.9
	add_child(shape)
	camera = Camera3D.new()
	camera.position.y = 1.65
	camera.current = true
	add_child(camera)
	model = MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(0.12,0.14,0.5)
	model.mesh = box
	model.position = Vector3(0.27,-0.25,-0.45)
	camera.add_child(model)
	muzzle = OmniLight3D.new()
	muzzle.position = Vector3(0.27,-0.2,-0.8)
	muzzle.light_color = Color(1,0.65,0.2)
	muzzle.omni_range = 5
	muzzle.visible = false
	camera.add_child(muzzle)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED and not game.ended:
		rotate_y(-event.relative.x * 0.002)
		camera.rotation.x = clampf(camera.rotation.x-event.relative.y*0.002,-1.45,1.45)
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_ESCAPE:
			game.toggle_pause()
		if event.keycode == KEY_R and reload_time <= 0 and reserve[gun] > 0 and ammo[gun] < GUNS[gun].clip:
			reload_time = GUNS[gun].reload
		for i in range(4):
			if event.keycode == KEY_1+i and i in owned:
				gun = i
				reload_time = 0
		if event.keycode == KEY_E:
			game.use_station()

func _physics_process(delta: float) -> void:
	if game.ended or game.paused:
		return
	cooldown = maxf(0,cooldown-delta)
	damage_boost = maxf(0,damage_boost-delta)
	flash = maxf(0,flash-delta)
	muzzle.visible = flash > 0
	if reload_time > 0:
		reload_time -= delta
		if reload_time <= 0:
			var amount := mini(GUNS[gun].clip-ammo[gun],reserve[gun])
			ammo[gun] += amount
			reserve[gun] -= amount
	var input := Input.get_vector("move_left","move_right","move_forward","move_back")
	var direction := transform.basis * Vector3(input.x,0,input.y)
	var speed := 6.0 if not Input.is_key_pressed(KEY_SHIFT) else 8.5
	velocity.x = direction.x*speed
	velocity.z = direction.z*speed
	if not is_on_floor():
		velocity.y -= 20*delta
	if is_on_floor() and Input.is_action_just_pressed("jump"):
		velocity.y = 6
	move_and_slide()
	if position.y < -30:
		game.respawn_player()
	aim = Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT)
	camera.fov = lerpf(camera.fov,60.0 if aim else 80.0,delta*12)
	if Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		shoot()

func shoot() -> void:
	if cooldown > 0 or reload_time > 0 or ammo[gun] <= 0:
		return
	ammo[gun] -= 1
	cooldown = GUNS[gun].rate
	flash = 0.045
	var spread: float = GUNS[gun].spread * (0.45 if aim else 1.0)
	for pellet in range(GUNS[gun].pellets):
		var direction := -camera.global_basis.z + camera.global_basis.x*randf_range(-spread,spread)+camera.global_basis.y*randf_range(-spread,spread)
		var query := PhysicsRayQueryParameters3D.create(camera.global_position,camera.global_position+direction*160,3,[get_rid()])
		var hit := get_world_3d().direct_space_state.intersect_ray(query)
		if not hit.is_empty() and hit.collider.has_method("take_damage"):
			hit.collider.take_damage(GUNS[gun].damage*(1.5 if damage_boost > 0 else 1.0)*(1.0+game.level*0.05))
			game.hit_flash = 0.15

func take_damage(amount: float) -> void:
	if game.ended:
		return
	health -= amount
	game.hurt_flash = 0.3
	if health <= 0:
		game.finish(false)
