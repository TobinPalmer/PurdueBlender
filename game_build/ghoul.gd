extends CharacterBody3D
var game: Node3D
var health := 70.0
var speed := 2.2
var attack := 0.0
var kind := 0
func _ready() -> void:
	collision_layer = 2
	collision_mask = 1
	var collision := CollisionShape3D.new()
	var capsule := CapsuleShape3D.new()
	capsule.radius = 0.4
	capsule.height = 1.7
	collision.shape = capsule
	collision.position.y = 0.85
	add_child(collision)
	var body := MeshInstance3D.new()
	var mesh := CapsuleMesh.new()
	mesh.radius = 0.4
	mesh.height = 1.7
	body.mesh = mesh
	body.position.y = 0.85
	var material := StandardMaterial3D.new()
	material.albedo_color = [Color(0.22,0.4,0.29),Color(0.7,0.3,0.16),Color(0.3,0.22,0.45)][kind]
	body.material_override = material
	add_child(body)
	add_to_group("enemies")
func _physics_process(delta: float) -> void:
	if game.paused or game.ended:
		return
	attack -= delta
	var direction: Vector3 = game.player.global_position-global_position
	direction.y = 0
	var distance := direction.length()
	if distance > 1.3:
		direction = direction.normalized()
		# Local obstacle steering for the first arena prototype.
		for angle in [0.0,0.8,-0.8,1.5,-1.5]:
			var candidate := direction.rotated(Vector3.UP,angle)
			var query := PhysicsRayQueryParameters3D.create(global_position+Vector3.UP,global_position+Vector3.UP+candidate*1.3,1,[get_rid()])
			if get_world_3d().direct_space_state.intersect_ray(query).is_empty():
				direction = candidate
				break
		velocity.x = direction.x*speed
		velocity.z = direction.z*speed
	else:
		velocity.x = 0
		velocity.z = 0
		if attack <= 0:
			game.player.take_damage(12 if kind != 2 else 22)
			attack = 1.0
	if not is_on_floor():
		velocity.y -= 20*delta
	move_and_slide()
	if position.y < -25:
		take_damage(9999)
func take_damage(amount: float) -> void:
	health -= amount
	if health <= 0 and not is_queued_for_deletion():
		game.enemy_killed(global_position)
		queue_free()
