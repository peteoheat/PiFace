import pyglet
 
vidPath = 'Images/granted_combined.avi'
window= pyglet.window.Window()
player = pyglet.media.Player()
source = pyglet.media.StreamingSource()
MediaLoad = pyglet.media.load(vidPath)
 
player.queue(MediaLoad)
player.play()
 
 
@window.event
def on_draw():
    if player.source and player.source.video_format:
        player.get_texture().blit(50,50)
 
 
 
pyglet.app.run()
