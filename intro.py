import pgzrun
import random as rand
import math

from pgzero.actor import Actor
from pgzero.keyboard import keyboard

#Constants
WIDTH = 640
HEIGHT = 480
TITLE = "Underwater Passover"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (64, 255, 64)

GRAVITY = 0.5
SPD = 5
J_SPD = -15
P_INIT_HEIGHT = 415
PLATAFORM_HEIGHT = (HEIGHT / 2) + 100

transparent_black = Actor("trans_black.png")
transparent_aqua = Actor("underwater.png")

# State Constants
MENU = 0
GAME = 1
DEAD = 2

# Menu Constants
START_COLLISION = Rect(65, 165, 300, 30)
SOUNDS_COLLISION = Rect(65, 205, 300, 30)
EXIT_COLLISION = Rect(65, 250, 300, 30)

# Music Constants
JUKEBOX = ["menu.ogg", "main title.ogg", "death.ogg"]
lastState = -1
music_enabled = True

#Variables
score = 0
state = 0

obstacles = []
num_obstacles = 5

mouse_pos = (0, 0)
start_button_hover = False
sounds_button_hover = False
exit_button_hover = False

platforms = []
num_platforms = 3

shooters = []
num_shooters = 2
bullets = []

bubbles = []

#Actors
#Player
player = Actor('player0.png')
player.vertical_velocity = 0
player.jump = False
player.x = 40
player.y = 415
player.moveValue = 0


def jump():
    if not player.jump:
        player.vertical_velocity = J_SPD
        player.jump = True


def walk():
    if keyboard.left or keyboard.a:
        player.x -= SPD
        player.moveValue += 1
    elif keyboard.right or keyboard.d:
        player.x += SPD
        player.moveValue += 1
    else:
        player.moveValue = 0
        player.image = "player0.png"

    if player.moveValue > 64:
        player.moveValue = 0
    elif player.moveValue > 47:
        player.image = "player3.png"
    elif player.moveValue > 31:
        player.image = "player2.png"
    elif player.moveValue > 15:
        player.image = "player1.png"
    else:
        player.image = "player0.png"


def player_update(dt):
    player.vertical_velocity += GRAVITY
    player.y += player.vertical_velocity

    if player.y >= P_INIT_HEIGHT:
        player.y = P_INIT_HEIGHT
        player.vertical_velocity = 0
        player.jump = False

    walk()

    if keyboard.up or keyboard.space or keyboard.w:
        jump()


def reset():
    player.x = 40
    player.y = 415


#Background
background = Actor('background.jpg', center=(100, 0))

#Ground
ground = Actor('ground.png')
ground.y = HEIGHT - (ground.height / 2)


#Platform
class Platform(Actor):
    def __init__(self):
        super().__init__("platform.png")
        self.x = WIDTH + rand.randint(20, 1200)
        self.y = HEIGHT - rand.randint(135, 200)
        self.speed = rand.randint(1, 5)

    def update(self):
        if state == GAME:
            self.x -= self.speed
            self.verifyColision()

        if self.x < -50:
            self.reset()

    def reset(self):
        self.x = WIDTH + rand.randint(20, 1200)
        self.y = HEIGHT - rand.randint(135, 200)
        self.speed = rand.randint(1, 5)

    def verifyColision(self):
        if player.vertical_velocity >= 0 and player.colliderect(
                self) and player.bottom <= self.top + player.vertical_velocity:
            player.y = self.top - player.height / 2  # Posiciona o jogador no topo da plataforma
            player.vertical_velocity = 0  # Para a queda
            player.jump = False


#Obstacle
class Obstacle(Actor):
    def __init__(self):
        super().__init__("enemy0.png")
        self.x = WIDTH + rand.randint(100, 1000)
        self.y = HEIGHT - rand.randint(20, 100)
        self.speed = rand.randint(4, 7)
        self.passed_player = False
        self.moveValue = 0

    def update(self):
        if state == GAME:
            self.x -= self.speed
            self.moveValue += 1

            if self.x < -50:
                self.reset()

            if self.moveValue > 63:
                self.moveValue = 0
            elif self.moveValue > 31:
                self.image = "enemy1.png"
            else:
                self.image = "enemy0.png"

    def reset(self):
        self.x = WIDTH + rand.randint(50, 300)
        self.y = HEIGHT - rand.randint(20, 50)
        self.speed = rand.randint(4, 7)
        self.passed_player = False


#Shooter
class Shooter(Obstacle):
    def __init__(self):
        super().__init__()
        self.image = "enemy2.png"
        self.x = WIDTH + rand.randint(50, 500)
        self.y = HEIGHT - rand.randint(80, 120)
        self.speed = rand.randint(1, 3)
        self.passed_player = False
        self.seeingPlayer = False
        self.shoot_cooldown = 0

    def update(self):
        if state == GAME:
            self.x -= self.speed
            self.moveValue += 1

            if self.x < -50:
                self.reset()

            if self.moveValue > 63:
                self.moveValue = 0
            elif self.moveValue > 31:
                self.image = "enemy3.png"
            else:
                self.image = "enemy2.png"

            if player.y + player.width >= self.y and WIDTH > self.x > player.x:
                self.shoot_cooldown += 1
                self.seeingPlayer = True
            else:
                self.seeingPlayer = False
                self.shoot_cooldown = 0

            if self.seeingPlayer:
                self.shoot()

    def reset(self):
        self.image = "enemy2.png"
        self.x = WIDTH + rand.randint(50, 300)
        self.y = HEIGHT - rand.randint(20, 100)
        self.speed = rand.randint(1, 3)
        self.passed_player = False

    def shoot(self):
        if self.shoot_cooldown > 15:
            new_bullet = Bullet()
            new_bullet.x = self.x
            new_bullet.y = self.y
            new_bullet.speed = self.speed + 3
            bullets.append(new_bullet)
            self.shoot_cooldown = 0


#Bullet
class Bullet(Obstacle):
    def __init__(self):
        super().__init__()
        self.image = "bullet.png"
        self.passed_player = False

    def update(self):
        if state == GAME:
            self.x -= self.speed
            self.moveValue += 1

            if self.x < -50:
                bullets.remove(self)

            if self.moveValue > 8:
                self.angle += 45
                self.moveValue = 0


#Bubble
class Bubble(Actor):
    def __init__(self):
        super().__init__("bubble.png")
        self.x = rand.randint(0,16) * 40
        self.y = HEIGHT + 10
        self.spd = rand.randint(1,3)
        self.height_stop = rand.randint(0, 24) * 20
        self.count_stop = 0

    def update(self):
        self.y -= self.spd

        if self.y == self.height_stop:
            self.spd = 0
            self.count_stop += 1
            if self.count_stop > 15:
                self.spd = rand.randint(1,3)

        if self.y < -50:
            bubbles.remove(self)


for _ in range(num_obstacles):
    obstacles.append(Obstacle())

    if _ > 0:
        obstacles[-1].x = obstacles[-2].x + rand.randint(200, 400)

for _ in range(num_platforms):
    platforms.append(Platform())

    if _ > 0:
        platforms[-1].x = platforms[-2].x + rand.randint(200, 400)

for _ in range(num_shooters):
    shooters.append(Shooter())

    if _ > 0:
        shooters[-1].x = shooters[-2].x + rand.randint(200, 400)


def on_mouse_move(pos):
    global mouse_pos
    mouse_pos = pos


def on_mouse_down(pos):
    global state, music_enabled

    if state == MENU:
        if START_COLLISION.collidepoint(pos):
            state = GAME
            reset()
        elif SOUNDS_COLLISION.collidepoint(pos):
            music_enabled = False if music_enabled else True
        elif EXIT_COLLISION.collidepoint(pos):
            exit()


def music_manager():
    global lastState

    if music_enabled:
        if state != lastState:
            music.play(JUKEBOX[state])
            music.set_volume(0.6)
            lastState = state
    else:
        music.pause()
        lastState = -1


def check_mouse_hoover():
    global start_button_hover, sounds_button_hover, exit_button_hover

    if START_COLLISION.collidepoint(mouse_pos):
        start_button_hover = True
    else:
        start_button_hover = False

    if SOUNDS_COLLISION.collidepoint(mouse_pos):
        sounds_button_hover = True
    else:
        sounds_button_hover = False

    if EXIT_COLLISION.collidepoint(mouse_pos):
        exit_button_hover = True
    else:
        exit_button_hover = False


def draw_menu():
    transparent_black.draw()

    start_color = GREEN if start_button_hover else WHITE
    sounds_color = GREEN if sounds_button_hover else WHITE
    exit_color = GREEN if exit_button_hover else WHITE

    screen.draw.text("Underwater Passover", (50, 90), color=WHITE, fontsize=70)
    screen.draw.text("Começar Jogo", (65, 165), color=start_color, fontsize=30)
    screen.draw.text("Ligar Sons", (65, 205), color=sounds_color, fontsize=30)
    screen.draw.text("Sair", (65, 250), color=exit_color, fontsize=30)


def update(dt):
    global score, state

    music_manager()

    if state == MENU:
        check_mouse_hoover()

    elif state == GAME:
        player_update(dt)

        for obstacle in obstacles:
            obstacle.update()

            if player.colliderect(obstacle):
                state = DEAD

            if not obstacle.passed_player and obstacle.x < player.x - player.width / 2:
                score += 100
                obstacle.passed_player = True

        for shooter in shooters:
            shooter.update()

            if player.colliderect(shooter):
                state = DEAD

            if not shooter.passed_player and shooter.x < player.x - player.width / 2:
                score += 100
                shooter.passed_player = True

        for bullet in bullets:
            bullet.update()

            if player.colliderect(bullet):
                state = DEAD

        for platform in platforms:
            platform.update()

        if rand.randint(0, 1000) < 6:
            bubbles.append(Bubble())

        for b in bubbles:
            b.update()

        print("Bubbles: ", len(bubbles))

    elif state == DEAD:

        if keyboard.r:
            state = GAME
            score = 0
            reset()

            for obstacle in obstacles:
                obstacle.reset()

            for shooter in shooters:
                shooter.reset()

            for platform in platforms:
                platform.reset()

            bullets.clear()
            bubbles.clear()

        elif keyboard.s:
            exit()

    if keyboard.escape:
        state = MENU


def draw():
    screen.fill(BLACK)

    background.draw()
    ground.draw()

    for obstacle in obstacles:
        obstacle.draw()

    for shooter in shooters:
        shooter.draw()

    for bullet in bullets:
        bullet.draw()

    for platform in platforms:
        platform.draw()

    for b in bubbles:
        b.draw()

    player.draw()

    transparent_aqua.draw()

    screen.draw.text(f"Pontos: {score}", (20, 20), color=WHITE, fontsize=40)

    if state == MENU:
        draw_menu()
    elif state == DEAD:
        transparent_black.draw()
        screen.draw.text("GAME OVER!", (WIDTH // 2 - 150, HEIGHT // 2 - 50), color=WHITE, fontsize=70)
        screen.draw.text("Pressione R para reiniciar", (WIDTH // 2 - 160, HEIGHT // 2 + 20), color=WHITE, fontsize=30)
        screen.draw.text("Pressione S para sair", (WIDTH // 2 - 160, HEIGHT // 2 + 50), color=WHITE, fontsize=30)


pgzrun.go()
