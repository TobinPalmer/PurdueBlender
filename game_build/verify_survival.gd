extends SceneTree
func _initialize() -> void:
	call_deferred("verify")
func verify() -> void:
	var scene = load("res://scenes/campaign.tscn").instantiate()
	root.add_child(scene)
	await process_frame
	scene.set_process(false)
	scene.player.set_physics_process(false)
	scene.paused = true
	scene.credits = 2000
	scene.intermission = 10
	scene.buy(1)
	assert(1 in scene.player.owned)
	assert(scene.credits == 1650)
	var ammo_before: int = scene.player.ammo[1]
	scene.player.shoot()
	assert(scene.player.ammo[1] == ammo_before-1)
	scene.player._reload()
	await create_timer(2.0).timeout
	assert(scene.player.ammo[1] == 30)
	for building in range(2):
		for round_index in range(5):
			scene.paused = false
			scene.wave = round_index+1
			scene.intermission = 0
			scene.pending = 0
			scene._process(0.01)
			scene.paused = true
			await process_frame
		if building == 0:
			assert(scene.stage == 1)
			assert(scene.wave == 0)
	assert(scene.ended)
	assert(scene.cleared == 2)
	print("PASS: weapon purchase, ammo use, reload, two building transitions, campaign victory")
	quit()
