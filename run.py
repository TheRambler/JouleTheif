import game, pygame, time, loader, sys, ui, random, maploader, util

loader.assets.load_dir("assets_shared")

username="User-"+str(random.randint(0,9))
if "server" in sys.argv or "saserver" in sys.argv:
	print "Starting Server..."
	server = game.Server(('', 1228))
	time.sleep(0.1)
	maploader.load_map_fn('maps/test4.tmx', server, False, True)
	server.start_handle_loop()
	server.start_update_loop()
	if len(sys.argv)>2:
		username=sys.argv[2]
if "saserver" in sys.argv:
	while 1:pass
time.sleep(0.1)
pygame.init()

screen_size=(832,600)
screen = pygame.display.set_mode(screen_size)#((650,500))
sscreen = util.ScrollingWorldManager(screen)

loader.assets.load_dir("assets_client")

if len(sys.argv)>1 and "server" not in sys.argv:
	username=sys.argv[1]
print "Connecting Client..."
client = game.Client(('localhost' if 'server' in sys.argv else 'a.zapflame.com', 1228), username, sscreen)
maploader.load_map_fn('maps/test4.tmx', client, True, False)
client.start_handle_loop()
client.start_send_loop()
print "Starting Loop..."
clock=pygame.time.Clock()

chatbox=ui.TextBox()

while True:
	screen.fill((0,0,0))
	sscreen.blit(client.map_surf, (0,0))
	client.particle_manager.update()
	clock.tick(40)
	for event in pygame.event.get():
		chatbox.update(event)
		if event.type==pygame.QUIT:
			pygame.quit()

	if chatbox.buf:
		msg=chatbox.buf.pop()
		if msg.startswith("\\"):
			msg=msg.replace("\\","")
			if msg=="toggleboxes":
				client.show_boxes=not client.show_boxes
		else:
			client.post_chat_message('', msg)
	client.input_frozen = chatbox.enabled
	
	with client.entity_lock:
		for entity in client.entities.values():
			entity.update(1/clock.get_fps() if clock.get_fps()>10 else 0)
			entity.render()
			if entity.kill:
				del client.entities[entity.eid]

	if client.player in client.entities:
		sscreen.set_offset((client.entities[client.player].x-screen_size[0]/2-client.entities[client.player].width/2, client.entities[client.player].y-screen_size[1]/2-client.entities[client.player].height/2))

	chatbox.render(screen, (3, 579))
	client.chatwin.render((0, 525))
	screen.blit(pygame.font.SysFont('monospace',14).render("Ping: "+str(float(client.ping))+"ms", False, (0,255,0)), (0,0))
	screen.blit(pygame.font.SysFont('monospace',14).render(str(int(clock.get_fps()))+" FPS", False, (0,0,255)), (0,10))
	screen.blit(pygame.font.SysFont('monospace',14).render("Rrate: "+str(int(client.recv_rate)), False, (255,0,0)), (0,20))

	pygame.display.flip()