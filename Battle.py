import pygame

def battle_field(board):
    """ Draw a Battle field for the game"""

    pygame.init()
    # using the following colors for the battlefield - white and black
    colors = [(255,255,255), (0,0,0)]

    n = len(board)         # This is an NxN chess board.
    surface_size = 400           # Proposed physical surface size.
    square_size = surface_size // n    # sq_sz is length of a square.
    surface_size = n * square_size     # Adjust to exactly fit n squares.

    # Create the surface of (width, height), and its window.
    surface = pygame.display.set_mode((surface_size, surface_size))
    pygame.display.set_caption("Dragon slayer")



    # Use an extra offset to centre the ball in its square.
    # If the square is too small, offset becomes negative,
    #   but it will still be centered :-)


    while True:

        # Look for an event from keyboard, mouse, etc.
        ev = pygame.event.poll()
        if ev.type == pygame.QUIT:
            break;

        # Draw a fresh background (a blank chess board)
        for row in range(n):           # Draw each row of the board.
            c_indx = row % 2           # Alternate starting color
            for col in range(n):       # Run through cols drawing squares
                the_square = (col*square_size, row*square_size, square_size, square_size)
                surface.fill(colors[c_indx], the_square)
                # Now flip the color index for the next square
                c_indx = (c_indx + 1) % 2



        pygame.display.flip()


    pygame.quit()

if __name__ == "__main__":
    battle_field([0, 5, 3, 1, 6, 4, 2])    # 7 x 7 to test window size
