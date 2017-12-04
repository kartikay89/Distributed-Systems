import pygame

def battle_field(board, units):
    """ Draw a Battle field for the game"""

    pygame.init()
    # using the following colors for the battlefield - white and black
    colors = [(255,255,255), (0,0,0)]

    n = len(board)
    surface_size = 400                        # Battlefield surface size.
    square_size = surface_size / n            # square_size is length of a square.
    surface_size = n * square_size            # fitting within squares.

    # Creating surface of (width, height), and its window.
    surface = pygame.display.set_mode((surface_size, surface_size))

    # Loading the dragon on the battle field
    dragon = pygame.image.load("Dragon.png")
    dragon_img = pygame.transform.scale(dragon, (square_size, square_size))

    # Loading superman
    player = pygame.image.load("Superman.png")
    player_img = pygame.transform.scale(player, (square_size, square_size))

    # Using offset to centre the dragon on the square
    dragon_offset = square_size / 2

    # Adding the name for the game
    pygame.display.set_caption("Dragon Arena")

    while True:
        # Quit event
        ev = pygame.event.poll()
        if ev.type == pygame.QUIT:
            break

        for row in range(n):
            c_indx = row % 2
            for col in range(n):
                the_square = (col*square_size, row*square_size, square_size, square_size)
                surface.fill(colors[c_indx], the_square)
                c_indx = (c_indx + 1) % 2

        for unit in units:
        	x, y = unit.field.position
        	if type(unit) == Dragon:
        		surface.blit(dragon_img, (x * square_size, y * square_size))
        	else:
        		surface.blit(player_img, (x * square_size, y * square_size))
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    battle_field([0, 5, 3, 1, 6, 4, 2], None)
