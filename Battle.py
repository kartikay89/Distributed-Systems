import pygame

def battle_field(board):
    """ Draw a Battle field for the game"""

    pygame.init()
    # using the following colors for the battlefield - white and black
    colors = [(255,255,255), (0,0,0)]

    n = len(board)
    surface_size = 400                        # Battlefield surface size.
    square_size = surface_size // n           # square_size is length of a square.
    surface_size = n * square_size            # fitting within squares.

    # Creating surface of (width, height), and its window.
    surface = pygame.display.set_mode((surface_size, surface_size))
    # Adding the name for the game
    pygame.display.set_caption("Dragon slayer")

    while True:

        # Quit event
        ev = pygame.event.poll()
        if ev.type == pygame.QUIT:
            break;

        #background
        for row in range(n):
            c_indx = row % 2
            for col in range(n):
                the_square = (col*square_size, row*square_size, square_size, square_size)
                surface.fill(colors[c_indx], the_square)
                c_indx = (c_indx + 1) % 2



        pygame.display.flip()


    pygame.quit()

if __name__ == "__main__":
    battle_field([0, 5, 3, 1, 6, 4, 2])    