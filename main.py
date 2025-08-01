import os
import pygame
import sys
import pygamepal
import random
import math
from random import randint
from button import Button
from spritesheet import Spritesheet



#general setup
pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
running = True
clock = pygame.time.Clock()  # FPS

#resoluçao do jogo
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 800, 600
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))




#icone e nome do jogo
pygame.display.set_icon(pygame.image.load('../tomoni\images\icon.png'))
pygame.display.set_caption("TOMONI")


#Tela de inicio
start_screen = True
start_img = pygame.image.load('assets/background/start_screen.png')
start_img = pygame.transform.scale(start_img, (VIRTUAL_WIDTH,VIRTUAL_HEIGHT))

#Background Imagem
background_img = pygame.image.load('assets/background/background.png')


#Efeitos sonoros do jogo
attack_sfx = pygame.mixer.Sound('assets\sfx\switch01.wav')
attack_sfx.set_volume(0.1)  #10% do volume  


#Colors
black = (0,0,0)
green = '#108058'
gray = '#3c3c3c'
crimson_red = (63, 4, 4)
red = '#dc143c'
white = (255,255,255)

#Player Class
class Player(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(*groups)
    #------------------------Animaçao--------------------------------------------    
        self.sprite_sheet = Spritesheet('assets\player\marisa_forward.png')
        self.animation_sprites = []

        #posição do primeiro sprite 
        initial_x = 4
        initial_y = 4

        #distacia de pixel de uma imagem para outra
        distance_pixel = 25

        #dimensoes dos sprites da imagem
        sprite_width = 22
        sprite_height = 45

        for i in range(8):
            # Acha a posiçao x,y do proximo sprite
            current_x = initial_x + (i * distance_pixel)

            #usa o get image para pegar o sprite do loop
            frame = self.sprite_sheet.get_image(current_x, initial_y, sprite_width, sprite_height, 1, black)
            self.animation_sprites.append(frame)
       

        self.current_sprite_index = 0
        self.animation_speed = 150  #velocidade que a animaçao vai ter em ms
        self.last_animation_time = pygame.time.get_ticks()
        self.image = self.animation_sprites[self.current_sprite_index]  #define a imagem atual do loop como o sprite atual 
    #---------------------------------------------------------------------------------------------------

        #configuraçoes gerais do player
        self.rect = self.image.get_frect()
        self.rect.center = (VIRTUAL_WIDTH / 2, VIRTUAL_HEIGHT - 100)
        self.direction = pygame.math.Vector2() 
        self.speed = 300
        self.current_speed = 0

        #logica da vida
        self.lives = 7
        self.invicible = False
        self.invicible_time = 2000
        self.last_hit_time = 0
        
        #efeito piscando apos ser atingido
        self.frame_count = 0

        #cooldown 
        self.can_attack = True
        self.shoot_cooldown = 100  #ms entre cada tiro da marisa
        self.last_shot_time = 0

        #logica do raio da hitbox
        self.hitbox_radius = 4                                                                                      #raio da hitbox 
        self.hitbox_image = pygame.image.load("assets/player/hitbox.png").convert_alpha()
        self.hitbox_offset = pygame.Vector2(self.hitbox_image.get_width() // 2, self.hitbox_image.get_height() // 2)

        #velocidade da marisa quando aperta shift no modo lento
        self.slow_speed = 100


        #MASK 
        self.mask = pygame.mask.from_surface(self.image)
      


    def animate(self):
        now = pygame.time.get_ticks()
        
        if now - self.last_animation_time > self.animation_speed:
            self.last_animation_time = now
            self.current_sprite_index = (self.current_sprite_index + 1) % len(self.animation_sprites) #fica loopando entre 0 e 8, voltando a 0 no final
            self.image = self.animation_sprites[self.current_sprite_index]


    def attack_timer(self):
        if not self.can_attack:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time >= self.attack_cooldown_duration:
                self.can_attack = True


    def input(self):                    
        keys = pygame.key.get_pressed()                                                             
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])    #Quando a tecla pressionada ser True, o int transforma em 1 
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction.length() > 0 else self.direction  #iguala a velocidade nas diagonais

        if keys[pygame.K_LSHIFT]:                   #Logica do modo lento ao apertar shift
            self.current_speed = self.slow_speed
        else:
            self.current_speed = self.speed

    def movimento(self,dt):
        self.rect.x += self.direction.x * self.current_speed * dt   #A direçao do input é multiplicada pelo dt e velocidade atual, podendo ser a lenta ou rapida
        self.rect.y += self.direction.y * self.current_speed * dt

    #Logica do desenho da hitbox
    def draw_hitbox(self, surface):                         
        x = self.rect.centerx - self.hitbox_offset.x - 3     #Numero tres apenas para precisao do local do local pro meu toque :)
        y = self.rect.centery - self.hitbox_offset.y
        surface.blit(self.hitbox_image, (x, y))



    def update(self, dt):
        
        
        self.rect.clamp_ip(playable_rect) #metodo pra deixar o player na area jogavel

        self.input()
        self.movimento(dt)
        self.animate()

        current_time = pygame.time.get_ticks()      
        recent_key = pygame.key.get_pressed()
        if recent_key[pygame.K_SPACE]:                                      #logica pra controlar quantas balas sao atiradas pela marisa
            if current_time - self.last_shot_time >= self.shoot_cooldown:   
                Bullet(marisa_bullet, self.rect.midtop, (all_sprites,bullet_sprites))
                self.last_shot_time = current_time
                attack_sfx.play()
        
        if self.invicible:
            #efeito piscando
            self.frame_count += 1
            if self.frame_count%10 < 5:
                self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)
            #tempo do iframe apos ser atingido
            now = pygame.time.get_ticks()
            if now - self.last_hit_time >= self.invicible_time:
                self.invicible = False
        else:
            self.image.set_alpha(255)

#Classe Danmaku -> Bala do inimigo
class Danmaku(pygame.sprite.Sprite):


    def __init__(self,surf, pos, direction, speed, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        
        
        self.direction = direction.normalize() if direction.length() > 0 else pygame.Vector2(0,0)
        self.speed = speed
        self.pos = pygame.Vector2(self.rect.center)
        
        # --- logica do tempo de vida da bala na area jogavel ---
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 8000                                    
        
        # --- ----------------Mask-------- ----------------------
        self.mask = pygame.mask.from_surface(self.image)


    def update(self, dt):
        # logica do movimento
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

        # Mata o Danmaku depois do tempo do lifetime
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

         # Outro metodo pra matar o danmaku se passar do retangulo da tela do player
        if not self.rect.colliderect(virtual_surface.get_rect()):
            self.kill()
        
        
#Classe da Cirno -> Boss fight   
class Boss_fight(pygame.sprite.Sprite):
    def __init__(self, surf, groups, boss_sprites):
        super().__init__(groups,boss_sprites)
        self.image = surf
        self.rect = self.image.get_frect(centerx=playable_rect.centerx, top=playable_rect.top + 50) #Posiciona ela no centro da tela pra segunda fase
        self.pos = pygame.Vector2(self.rect.topleft)        
        self.speed = 200
        self.direction = pygame.Vector2(1,0)
        self.phase = 0

    #----------------Transiçao entre fases----------------------------
        self.is_in_transition = False
        self.transition_time = 1000         #Tempo da transiçao entre fases
        self.transition_start_time = 0

    #----------------Logica da vida da Cirno -------------------------
        self.max_life = 50
        self.life = self.max_life
        self.alive = True

    #-----------------Mask------------------------------------
        self.mask = pygame.mask.from_surface(self.image)
     


    # ------------ Logica do ataque -------------------------------
        self.shoot_cooldown = 10                            # Cooldown entre o disparo individual das danmakus
        self.attack_pattern_cooldown = 1000                  # Cooldown entre ataques
        self.last_shot_time = pygame.time.get_ticks()


    
        self.spiral_angle = 0                               #ANGULO pro ataque espiral


#-----------------------Movimentos------------------------------------------------------------
    def move_left_right(self,dt):                           #Vai ficar indo do lado pro outro
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        if self.rect.right > playable_rect.right:           #Metodo pra Cirno nao escapar da tela jogavel
           self.rect.right = playable_rect.right
           self.pos.x = self.rect.x                         #Sincroniza o vetor pra posiçao dentro da area jogavel
           self.direction.x *= -1                           #Multiplica por -1 pra ir pra outra direçao
        elif self.rect.left < playable_rect.left:
            self.rect.left = playable_rect.left
            self.pos.x = self.rect.x 
            self.direction.x *= -1

#-----------------------Danmaku Patterns ------------------------------------------------
    def danmaku_spiral(self):                                                                   #Ataque espiral

        #calcula o angulo pro Danmaku
        angle_rad = math.radians(self.spiral_angle)
        direction = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad))

        Danmaku(cirno_danmaku, self.rect.center, direction, 80, all_sprites, danmaku_sprites)   #Cria um Danmaku com essa direçao

       
        increment = random.uniform(8, 12)                                                       #Incrementa para proxima direçao
        self.spiral_angle = (self.spiral_angle + increment) % 360                               #Vai ate 360
    


    def danmaku_spread_attack(self, player, num_bullets=5, angle_spread=60):                    #Ataque escopeta 
        # 1. Get the positions of the boss and the player
        boss_pos = pygame.Vector2(self.rect.center)
        player_pos = pygame.Vector2(player.rect.center)

        # 2. Calculate the direction vector and the angle from the boss to the player
        direction_vector = player_pos - boss_pos
        # math.atan2 gives us the angle in radians. We convert it to degrees.
        angle_to_player = math.degrees(math.atan2(direction_vector.y, direction_vector.x))

        # 3. Calculate the starting angle for our spread, centered on the player
        # This replaces the old hardcoded '90'
        start_angle = angle_to_player - (angle_spread / 2)
        angle_step = angle_spread / (num_bullets - 1) if num_bullets > 1 else 0

        # 4. The rest of the function is the same! It just uses our new dynamic angles.
        for i in range(num_bullets):
            angle = math.radians(start_angle + i * angle_step)
            direction = pygame.Vector2(math.cos(angle), math.sin(angle))
            Danmaku(cirno_kunai, self.rect.center, direction, 250, all_sprites, danmaku_sprites)

    # --- ----------------------------Logica das fases----------------------------------------------
    def update_phase_0(self, dt, now):                                  #Fase 0
        self.move_left_right(dt)                                        #Cirno se move pros lados e usa o tiro escopeta

        if now - self.last_shot_time >= self.attack_pattern_cooldown:   #Tempo entre cada disparo    
            self.danmaku_spread_attack(player)
            self.last_shot_time = now                                   #Reseta depois do tiro
    


    def update_phase_1(self, dt, now):                                  #Fase 1
        init_x = playable_rect.centerx                                  #Primeiro a Cirno volta ao centro da tela

        if not math.isclose(self.rect.centerx, init_x, abs_tol=5):      #Verifica se ela ta perto do centro da tela, com tolerancia de 5 pixels
            if self.rect.centerx < init_x:
                self.pos.x += self.speed * dt                           #Volta pra posiçao andando ate o centro
            else:
                self.pos.x -= self.speed * dt
            self.rect.centerx = round(self.pos.x)
    
        else:                                                           #Quando chega no centro, começa a atirar o Ataque espral
            if now - self.last_shot_time >= self.shoot_cooldown:
                self.danmaku_spiral()
                self.last_shot_time = now


    def check_phase_transition(self, now):                              #Funçao pra checar se ta na hora de mudar de fase

        if self.life <= self.max_life / 2 and self.phase == 0 and not self.is_in_transition:
            self.phase = 1
            self.is_in_transition = True
            self.transition_start_time = now
            print("--- Entering Phase Transition ---")
            # self.image = new_boss_image                                  #Talvez eu mude o sprite aqui?
    


    def update(self, dt):
        if not self.alive:                                                               #Se nao tiver viva, retorna nada
            return

        now = pygame.time.get_ticks()
        
                                                                                         #Logica do cooldown da transiçao de fase
        if self.is_in_transition:
            if now - self.transition_start_time >= self.transition_time:                 #Tempo de transiçao
                self.is_in_transition = False
                self.last_shot_time = now                                                #Reseta o ultimo ataque como medida pra ela nao atirar instantaniamente
                print(f"--- Starting Phase {self.phase} ---")
            return                                                                       

                                                                                        #Executa a logica da fase 0
        if self.phase == 0:
            self.update_phase_0(dt, now)

        elif self.phase == 1:                                                           #Executa a logica da fase 1
            self.update_phase_1(dt, now)                                                

                                                                                        #Checa se ta a vida do boss ja ta no momento pra mudar de fase
        self.check_phase_transition(now)

                                                                                                
        self.rect.clamp_ip(playable_rect)                                              #Mantem a Cirno presa na tela jogavel
        print(f"Boss HP: {self.life}")

       
            

#Classe da bala da Marisa
class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)               #Posicao da bala fica no top do rect do player
        self.speed = 500

#---------------------Mask----------------------------------------
        self.mask = pygame.mask.from_surface(self.image)


#--------------------Tempo de vida da bala---------------------------
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 100  

    def update(self, dt):
        self.rect.y -= self.speed * dt
        if self.rect.bottom < 0:                #Mata a bala depois que sai da tela jogavel
            self.kill() 
    
#Classe da Ui do jogo -> informaçoes fora da tela jogavel
class Ui(pygame.sprite.Sprite):
    def __init__(self, player, boss, *groups):
        super().__init__(*groups)
        self.player = player
        self.boss = boss


        self.image = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)                       #Definimos uma Surface transparente primeiro
        self.rect = self.image.get_frect(topleft=(0, 0))
        self.font = pygame.font.Font('assets/font/DFPPOPCorn-W12.ttf', 28)                                  #Fonte do jogo
        self.ui_color = (white)

 # --------------------------- Icone da vida------------------------ ---
        self.life_icon = pygame.image.load('assets/player/Hearth_icon.png')
        self.life_icon = pygame.transform.scale(self.life_icon, (20, 20))
        self.life_icon_rect = self.life_icon.get_rect(topleft=(620, 100))                                   #Talvez eu coloque mais em baixo depois?



    def draw_score(self):
        score_text = str(pygame.time.get_ticks() // 100)                                                   #Score do jogo, baseado no tempo
        text_surf = self.font.render(f'Score: {score_text}', True, self.ui_color)
        text_rect = text_surf.get_frect(topright=(VIRTUAL_WIDTH - 20, 40))
        self.image.blit(text_surf, text_rect)

    def draw_player_lives(self):                                                                           #Ui da vida do jogador
        for i in range(self.player.lives):                                                                 #Loop que itera na quantidade de vida que o plahyer tem                                   
            x_pos = self.life_icon_rect.left + (i * (self.life_icon_rect.width + 5))                       #offset de 5 pixels entre cada icone e a largura
            y_pos = self.life_icon_rect.top
            self.image.blit(self.life_icon, (x_pos, y_pos))

    def draw_boss_health(self):
    
        max_width = 300                                                                        #Tamanho total da barra
        health_ratio = self.boss.life / self.boss.max_life                                     #Porcetagem da vida do Boss
        health_width = int(max_width * health_ratio)                                           #Tamanho da barra enquanto diminui

    
        x, y = VIRTUAL_WIDTH // 2 - max_width // 2, 10                                         #Posiçao da barra
        bar_height = 10                                                                        #Altura da barra

        # Draw background, health fill, and border
        pygame.draw.rect(self.image, (gray), (x, y, max_width, bar_height))            # Background da barra
        pygame.draw.rect(self.image, (red), (x, y, health_width, bar_height))           # Barra da vida
        pygame.draw.rect(self.image, (white), (x, y, max_width, bar_height), 2)     # Borda da barra

    def update(self, dt):
        self.image.fill((0, 0, 0, 0))     #Cada vez que o update roda, a tela e pintada de transparente 
                                        #Isso e extremamente necessario pq a tela ta sendo atualizada a todo momento, para nao sobscrever tudo
        self.draw_player_lives()
        self.draw_boss_health()

#Funçao das colisoes do jogo
def collisions():
#----------------------Player colisoes------------------------------------------------------------------------------

    if player.invicible:
        return 
    
                                                                                #Logica da esfera de hitbox
    player_center = pygame.Vector2(player.rect.center)                          #Pega um vetor do centro do rect do player
    for danmaku in danmaku_sprites:                                         
        danmaku_center = pygame.Vector2(danmaku.rect.center)                    #Pega um vetor do centro da Danmaku
        distance = player_center.distance_to(danmaku_center)                    #Calcula a distancia do centro do player para a Danmaku
        if distance < player.hitbox_radius:                                     #Se a distancia for maior que o raio da hitbox, tome :)
                print("Colidiu!!")
                player.lives -= 1
                player.invicible = True
                player.last_hit_time = pygame.time.get_ticks()
                player.frame_count = 0
                player.rect.center = (VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT - 50)
    
                if player.lives <= 0:
                    player.kill()


#-------------------Bullet Colisoes -------------------------------------------------------------
    for bullet in bullet_sprites:
        colided = pygame.sprite.spritecollide(bullet,boss_sprites,False,pygame.sprite.collide_mask)   
        if colided:                                                             #Verifica se a mascara da bullet colidiu com a mascara do boss
            cirno.life -= 1
            bullet.kill()
            if cirno.life == 0:
                cirno.kill()
                cirno.alive = False
                pygame.mixer.music.stop()


def scale_and_offset():
    target_ratio = VIRTUAL_WIDTH / VIRTUAL_HEIGHT                   #Calcula a proporçao da tela virtual
    real_ratio = SCREEN_WIDTH / SCREEN_HEIGHT                       #Calcula a proporçao real da tela

    if real_ratio >= target_ratio:                                  #Se a tela real tem proporçao mais larga que a proporcao target
        scale_factor = SCREEN_HEIGHT / VIRTUAL_HEIGHT               #Bordas pretas nos lados
    else:
        scale_factor = SCREEN_WIDTH / VIRTUAL_WIDTH                 #Se a tela real tem proporçao mais alta que a proporcao target
                                                                    #Bordas pretas em cima e em baixo
    scaled_width = int(VIRTUAL_WIDTH * scale_factor)
    scaled_height = int(VIRTUAL_HEIGHT * scale_factor)              #calcula a escala da altura e largura

    x_offset = (SCREEN_WIDTH - scaled_width) // 2                   #Calculo do Offset para centralizar a tela
    y_offset = (SCREEN_HEIGHT - scaled_height) // 2

    return scale_factor, x_offset, y_offset


def scaled_screen():
    scale_factor, x_offset, y_offset = scale_and_offset()           #Usa a funcaçao scale_and_offset para ter o offset e scale
                                                                        #separado em dois pq o offset é necessario para posicao do mouse :)

    scaled_width = int(VIRTUAL_WIDTH * scale_factor)                    #calcula a escala da altura e largura
    scaled_height = int(VIRTUAL_HEIGHT * scale_factor)

    scaled_surface = pygame.transform.scale(virtual_surface, (scaled_width, scaled_height))    #Escala a tela virtual

    
    display_surface.fill("black")                                       #Coloca em preto para criar as barras
    display_surface.blit(scaled_surface, (x_offset, y_offset))




#---------------------Playable Area Logic-----------------------------------
playable_field = pygame.image.load('assets/background/playable_screen.png')
playable_field = pygame.transform.scale(playable_field, (512, 512))
PLAYABLE_POS = (50, 40)
PLAYABLE_SIZE = (512, 512)
playable_rect = pygame.Rect(PLAYABLE_POS, PLAYABLE_SIZE)


#Buttons
start_surf = pygame.image.load('assets/buttons/start_button.png')
start_button = Button(100,100,start_surf,2)

        
#Spritesheets
knives_spritesheet = Spritesheet('assets/player/knives.png') 
danmaku_spritesheet = Spritesheet('assets/enemies/danmaku_spritesheet.png')
cirno_spritesheet = Spritesheet('assets/enemies/cirno_spritesheet.png')

#surfaces 
marisa_bullet = pygame.image.load('assets\player\marisa_bullet.png')
cirno_kunai = pygame.image.load('assets\enemies\kunai_0.png')
cirno_danmaku = pygame.image.load('assets/enemies/bullet_0.png')
knives_surf = knives_spritesheet.get_image(59,1,46,31,1, black)
danmaku_surf = danmaku_spritesheet.get_image(322,73,16,16,1,black)
cirno_surf = cirno_spritesheet.get_image(180,166,41,53,1,black)


#Creating Sprites
all_sprites = pygame.sprite.Group()
danmaku_sprites = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()
boss_sprites = pygame.sprite.Group()
ui_sprites = pygame.sprite.Group()

player = Player(all_sprites)
cirno = Boss_fight(cirno_surf,all_sprites,boss_sprites)
ui_elements = Ui(player,cirno,all_sprites,ui_sprites)





#Game loop
while running:
    #delta time
    dt = clock.tick()/1000  # FPS

    #Teclas pressionadas
    keys = pygame.key.get_pressed()

    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE: 
                start_screen = True
    

    if start_screen:
        virtual_surface.fill(black)
        virtual_surface.blit(start_img)
        mouse_pos = pygame.mouse.get_pos()

        scale_factor, x_offset, y_offset = scale_and_offset()

        virtual_mouse_x = (mouse_pos[0] - x_offset) / scale_factor
        virtual_mouse_y = (mouse_pos[1] - y_offset) / scale_factor
        virtual_mouse_pos = (virtual_mouse_x, virtual_mouse_y)

        if start_button.drawn(virtual_surface,virtual_mouse_pos):
            start_screen = False

            #toca musica quando começa
            pygame.mixer.music.load('assets/sfx/Tomboyish Girl in Love.mp3')
            pygame.mixer.music.set_volume(0.1)  # 30% volume
            pygame.mixer.music.play(-1)

    else:
        virtual_surface.fill(black)
        # Atualizações 
        all_sprites.update(dt)
        collisions()


        # Desenhando elementos que nao entram no clip
        virtual_surface.blit(background_img)
        virtual_surface.blit(playable_field, PLAYABLE_POS)

        #Após essa linha, tudo desenhado na virtual surface vai apenas aparecer na playable area
        virtual_surface.set_clip(playable_rect)

        #Desenho doos sprites do personagens
        for sprite in all_sprites:
            virtual_surface.blit(sprite.image, sprite.rect)
        #desenho da hitbox da sakuya
        if keys[pygame.K_LSHIFT]:
            player.draw_hitbox(virtual_surface)
            

        #Removendo o Clip da virtual surface agora
        virtual_surface.set_clip(None)

        #desenho dos elementos fora da area jogavel
        ui_sprites.draw(virtual_surface)

        if player.lives == 0:
            # Create and draw death screen
            tela_de_morte = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
            tela_de_morte.fill('red')

            font = pygame.font.Font(None, 72)
            text = font.render("YOU DIED", True, (255, 255, 255))
            text_rect = text.get_rect(center=(VIRTUAL_WIDTH // 2, VIRTUAL_HEIGHT // 2))
            tela_de_morte.blit(text, text_rect)
            virtual_surface.blit(tela_de_morte, (0, 0))
            pygame.mixer.music.stop()



    

        
    
    scaled_screen()
    pygame.display.update()


pygame.quit()


