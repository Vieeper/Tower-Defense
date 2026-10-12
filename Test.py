import pygame

pygame.init()

fenster = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# Farben
GRUEN = (50, 150, 50)
BRAUN = (120, 80, 40)
ROT = (200, 50, 50)

# Gegner
gegner_x = 25
gegner_y = 175

geschwindigkeit = 2

# Wegpunkte
# Der Gegner läuft immer von Punkt zu Punkt.
wegpunkte = [
    (325, 175),  # 1. Gerade nach rechts
    (325, 375),  # 2. Nach unten
    (475, 375),  # 3. Nach rechts
    (475, 225),  # 4. Nach oben
    (800, 225)   # 5. Nach rechts
]

punkt = 0

running = True

while running:

    # Fenster-Ereignisse
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ==================================
    # GEGNER BEWEGEN
    # ==================================

    ziel_x, ziel_y = wegpunkte[punkt]

    # Horizontal bewegen
    if gegner_x != ziel_x:

        if gegner_x < ziel_x:
            gegner_x += geschwindigkeit

            if gegner_x > ziel_x:
                gegner_x = ziel_x

        else:
            gegner_x -= geschwindigkeit

            if gegner_x < ziel_x:
                gegner_x = ziel_x

    # Wenn X stimmt -> vertikal bewegen
    elif gegner_y != ziel_y:

        if gegner_y < ziel_y:
            gegner_y += geschwindigkeit

            if gegner_y > ziel_y:
                gegner_y = ziel_y

        else:
            gegner_y -= geschwindigkeit

            if gegner_y < ziel_y:
                gegner_y = ziel_y

    # Ziel erreicht
    else:
        punkt += 1

        # Am Ende wieder zum Anfang
        if punkt >= len(wegpunkte):
            punkt = 0
            gegner_x = 25
            gegner_y = 175

    # ==================================
    # ZEICHNEN
    # ==================================

    fenster.fill(GRUEN)

    # Brauner Weg
    pygame.draw.rect(
        fenster,
        BRAUN,
        (0, 150, 300, 50)
    )

    pygame.draw.rect(
        fenster,
        BRAUN,
        (300, 150, 50, 250)
    )

    pygame.draw.rect(
        fenster,
        BRAUN,
        (300, 350, 150, 50)
    )

    pygame.draw.rect(
        fenster,
        BRAUN,
        (450, 250, 50, 150)
    )

    pygame.draw.rect(
        fenster,
        BRAUN,
        (450, 200, 350, 50)
    )

    # Gegner
    pygame.draw.circle(
        fenster,
        ROT,
        (int(gegner_x), int(gegner_y)),
        15
    )

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
