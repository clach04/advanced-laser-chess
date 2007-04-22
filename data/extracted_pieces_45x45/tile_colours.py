
# EDITME!
# Keep alc colours
p1colour = (178, 32, 0)
p1mirror_colour = (243, 48, 0)

p2colour = (0, 162, 0)
p2mirror_colour = (146, 227, 0)

frozen_colour = (180, 180, 180)

orig_background_colour = (255, 255, 255)
new_background_colour = (0, 0, 0)

# New colours
new_p1colour = (180, 72, 72)
new_p1mirror_colour = (255, 180, 180)
p2colour = (72, 180, 72)
p2mirror_colour = (180, 255, 180)



# EDITME!
#orig_to_p1_colours = {orig_background_colour:new_background_colour}
orig_to_p1_colours = {p1colour:new_p1colour, p1mirror_colour:new_p1mirror_colour, orig_background_colour:new_background_colour}
p1top2_colours = {p1mirror_colour : p2mirror_colour, p1colour : p2colour, orig_background_colour:new_background_colour}
p1tofrozen_colours = {p1mirror_colour : frozen_colour, p1colour : frozen_colour, orig_background_colour:new_background_colour}

