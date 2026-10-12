import pygame

pygame.init()

fenster = pygame.display.set_mode((800,600))

running = True

gegner_x = 25
gegner_y = 175

geschwindigkeit = 2

# Wegpunkte des braunen Pfades
wegpunkte = [
    (300, 175),  # nach rechts
    (325, 350),  # nach unten
    (450, 375),  # nach rechts
    (475, 250),  # nach oben
    (800, 225)   # nach rechts
]

aktueller_punkt = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --------------------------------
    # Gegner zum nächsten Punkt bewegen
    # --------------------------------

    ziel_x, ziel_y = wegpunkte[aktueller_punkt]

    dx = ziel_x - gegner_x
    dy = ziel_y - gegner_y

    # Entfernung zum Ziel
    entfernung = (dx**2 + dy**2) ** 0.5

    if entfernung < geschwindigkeit:
        # Ziel erreicht -> nächster Wegpunkt
        gegner_x = ziel_x
        gegner_y = ziel_y

        aktueller_punkt += 1

        # Wenn das Ende erreicht wurde
        if aktueller_punkt >= len(wegpunkte):
            aktueller_punkt = len(wegpunkte) - 1

    else:
        # Richtung zum Ziel berechnen
        gegner_x += dx / entfernung * geschwindigkeit
        gegner_y += dy / entfernung * geschwindigkeit


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    fenster.fill((50, 150, 50))
    pygame.draw.rect(fenster, (120, 80, 40), (0, 150, 300, 50))
    pygame.draw.rect(fenster, (120, 80, 40), (300, 150, 50, 250))
    pygame.draw.rect(fenster, (120, 80, 40), (300, 350, 150, 50))
    pygame.draw.rect(fenster, (120, 80, 40), (450, 250, 50, 150))
    pygame.draw.rect(fenster, (120, 80, 40), (450, 200, 350, 50))
    pygame.draw.circle(fenster, (200, 50, 50), (25, 175), 15)
    pygame.display.flip()