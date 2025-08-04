import pygame
import random
import math
from button import Button
from spritesheet import Spritesheet



#setup
pygame.init()


#configuracoes da tela
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
display_surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 800, 600
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))


#Colors
black = (0,0,0)
green = '#108058'
gray = '#3c3c3c'
crimson_red = (63, 4, 4)
red = '#dc143c'
white = (255,255,255)
yellow = "#d0da15"


#Area jogavel
PLAYABLE_POS = (50, 40)
PLAYABLE_SIZE = (512, 512)
playable_rect = pygame.Rect(PLAYABLE_POS, PLAYABLE_SIZE)



#Icone e nome do jogo
pygame.display.set_icon(pygame.image.load('../tomoni/assets\icon/icon.png'))
pygame.display.set_caption("西方:tomoni")


#Telas de inicio e Result
start_img = pygame.image.load('assets/background/start_screen.png')
start_img = pygame.transform.scale(start_img, (VIRTUAL_WIDTH,VIRTUAL_HEIGHT))
score_img = pygame.image.load('assets/background/result_screen.png')
score_img = pygame.transform.scale(score_img, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))


#Background Imagem e tela da area jogavel
background_img = pygame.image.load('assets/background/background.png')
playable_field = pygame.image.load('assets/background/playable_screen.png')
playable_field = pygame.transform.scale(playable_field, (512, 512))


#Botoes
start_surf = pygame.image.load('assets/buttons/start_button.png')
start_button = Button(100,100,start_surf,2)
exit_surf = pygame.image.load('assets/buttons/exit_button.png')
exit_button = Button(100,500,exit_surf,2)
options_surf = pygame.image.load('assets/buttons/option_button.png')
options_button = Button(80,200,options_surf,2)
        
#Spritesheets
knives_spritesheet = Spritesheet('assets/player/knives.png') 
danmaku_spritesheet = Spritesheet('assets/enemies/danmaku_spritesheet.png')
cirno_spritesheet = Spritesheet('assets/enemies/cirno_spritesheet.png')


#Surfaces -> Imagens dos sprites
marisa_bullet = pygame.image.load('assets\player\marisa_bullet.png')
cirno_kunai = pygame.image.load('assets\enemies\kunai_0.png')
cirno_danmaku = pygame.image.load('assets/enemies/bullet_0.png')
remilia_surf = pygame.image.load('assets\enemies/remilia_sprite.png')
remilia_ball = pygame.image.load('assets\enemies/remilia_ball.png')
knives_surf = knives_spritesheet.get_image(59,1,46,31,1, black)
danmaku_surf = danmaku_spritesheet.get_image(322,73,16,16,1,black)
cirno_surf = cirno_spritesheet.get_image(180,166,41,53,1,black)


#Efeitos sonoros do jogo
attack_sfx = pygame.mixer.Sound('assets\sfx\switch01.wav')
attack_sfx.set_volume(0.1)  #10% do volume  
death_sfx = pygame.mixer.Sound("assets\sfx\DEAD.wav")
death_sfx.set_volume(0.1)
graze_sfx = pygame.mixer.Sound("assets\sfx\graze.wav")
graze_sfx.set_volume(0.03)
cancel_sfx = pygame.mixer.Sound('assets/sfx/cancel00.wav')
cancel_sfx.set_volume(0.1)
life_up_sfx = pygame.mixer.Sound('assets/sfx/1UP.wav')
life_up_sfx.set_volume(0.1)

#fontes
font_ui = pygame.font.Font('assets/font/DFPPOPCorn-W12.ttf', 28)
font_title = pygame.font.Font('assets/font/DFPPOPCorn-W12.ttf', 72)
font_medium = pygame.font.Font('assets/font/DFPPOPCorn-W12.ttf', 48)
font_text = pygame.font.Font('assets/font/DFPPOPCorn-W12.ttf', 32)


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
        self.speed = 250
        self.current_speed = 0

        #logica da vida
        self.lives = 3
        self.invicible = False
        self.invicible_time = 2000
        self.last_hit_time = 0
        
        #efeito piscando apos ser atingido
        self.frame_count = 0

        #cooldown 
        self.shoot_cooldown = 100  #ms entre cada tiro da marisa, quanto menor mais balas ela vai atirar, o dano è 1 ainda, mas è mais rapido
        self.last_shot_time = 0

        #logica do raio da hitbox
        self.hitbox_radius = 5                            #raio da hitbox 
        self.hitbox_image = pygame.image.load("assets/player/hitbox.png").convert_alpha()
        self.hitbox_offset = pygame.Vector2(self.hitbox_image.get_width() // 2, self.hitbox_image.get_height() // 2)
        

        #velocidade da marisa quando aperta shift no modo lento
        self.slow_speed = 100


        #MASK 
        self.mask = pygame.mask.from_surface(self.image)
      
        #Graze
        self.graze_score = 0.0          #Graze é uma mecanica que ganha pontos por passar de raspao em uma bala
        self.graze_rate = 20            #valor multiplicado por cada ponto de grazw
        self.graze_radius = 15          #raio que o graze conta

        #Modo fantasma                   #A marisa fica invencivel e meio invisvel por 5 segundos ao apertar x
        self.ghost_mode_active = False
        self.ghost_power = 3            #quantidade de vezes que o ghost power pode ser ativado
        self.ghost_duration = 4000      #5 segundos
        self.ghost_start_time = 0       #variavel que vai ser alterada pro tempo que o ghost power for ativado
        

    def animate(self):
        now = pygame.time.get_ticks()
        
        if now - self.last_animation_time > self.animation_speed:
            self.last_animation_time = now
            self.current_sprite_index = (self.current_sprite_index + 1) % len(self.animation_sprites) #fica loopando entre 0 e 8, voltando a 0 no final
            self.image = self.animation_sprites[self.current_sprite_index]


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
        x = self.rect.centerx - self.hitbox_offset.x - 3     #Numero tres apenas para precisao e pra nao deixar ninguem maluco :)
        y = self.rect.centery - self.hitbox_offset.y         #Subtrai pelo offset pra colocar a imagem centralizada com o centro do player
        surface.blit(self.hitbox_image, (x, y))

         
      

    def update(self, dt):
        
        
        self.rect.clamp_ip(playable_rect) #metodo pra deixar o player na area jogavel

        self.input()
        self.movimento(dt)
        self.animate()

        current_time = pygame.time.get_ticks()      #Variavel que vai ser usada pra guardar o tempo de jogo 
        recent_key = pygame.key.get_pressed()       #Variavel que vai ser usada pra guardar a tecla pressionada pelo teclado

        if recent_key[pygame.K_z]:                                      #logica pra controlar quantas balas sao atiradas pela marisa
            if current_time - self.last_shot_time >= self.shoot_cooldown:   
                Bullet(marisa_bullet, self.rect.midtop, (all_sprites,bullet_sprites))
                self.last_shot_time = current_time
                attack_sfx.play()
        
           
        if recent_key[pygame.K_x]:
            if self.ghost_power > 0 and not self.ghost_mode_active:          # Checa se tem poder e se não está já no modo fantasma
                self.ghost_power -= 1
                self.ghost_mode_active = True
                self.invicible = True                                         # Fica invencível
                self.ghost_start_time = current_time                        # Inicia o timer UMA VEZ

        

        if self.ghost_mode_active:                                          #Aqui verifica se o ghost mode precisa terminar
            if current_time - self.ghost_start_time > self.ghost_duration:
                self.ghost_mode_active = False
                self.invicible = False                                      #Deixa de ser invencível
            else:
                self.image.set_alpha(100)                                   #se tiver ativo, coloca a imagem meio trasparente 


        elif self.invicible:                                    #Se nao tiver no ghost mode e tiver invencivel, executa a logica do iframe
            #efeito piscando
            self.frame_count += 1                                #Vai incremnentar 1 para o frame
            if self.frame_count%10 < 5:                         #5 vezes o if ira ser verdadeiro, deixando o sprite invisivel, e 5 vezes falso deixando visivel
                self.image.set_alpha(0)
            else:
                self.image.set_alpha(255)
            if current_time - self.last_hit_time >= self.invicible_time:    #quando acaba o tempo invencivel, volta o normal e o efeito acaba
                self.invicible = False
        else:
            self.image.set_alpha(255)


#Classe Danmaku -> Bala do inimigo
class Danmaku(pygame.sprite.Sprite):


    def __init__(self,surf, pos, direction, speed, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        
        
        self.direction = direction.normalize() if direction.length() > 0 else pygame.Vector2(0,0)  #Normaliza o vetor caso o vetor nao seja um vetor nulo
        self.speed = speed
        self.pos = pygame.Vector2(self.rect.center)             #vetor que vai ser incrementado pela vetor direction multiplicado pela velocidade e dt, e o que moviementa o rect da bala
                                         
        
        # --- ----------------Mask-------- ----------------------
        self.mask = pygame.mask.from_surface(self.image)


    def update(self, dt):
        # logica do movimento
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

     
        if not self.rect.colliderect(virtual_surface.get_rect()):     #Assim que a bala para de colidir com a tela inteira, ela e excluida
            self.kill()
        
        
#Classe mae da Boss fight   
class Boss_fight(pygame.sprite.Sprite):
    def __init__(self, surf, max_life, speed, transition_time, straight_cooldown, spread_cooldown, burst_cooldown, spiral_cooldown, groups, boss_sprites):
        super().__init__(groups,boss_sprites)
        self.image = surf
        self.rect = self.image.get_frect(centerx=playable_rect.centerx, top=playable_rect.top + 50) #Posiciona ela no centro da tela 
        self.pos = pygame.Vector2(self.rect.topleft)        
        self.speed = speed
        self.direction = pygame.Vector2(1,0)
        self.phase = 0

    #----------------Transiçao entre fases----------------------------
        self.is_in_transition = False
        self.transition_time = transition_time         #Tempo da transiçao entre fases
        self.transition_start_time = 0

    #----------------Logica da vida dos bosses -------------------------
        self.max_life = max_life
        self.life = self.max_life
        self.alive = True

    #-----------------Mask------------------------------------
        self.mask = pygame.mask.from_surface(self.image)
     
    #----------------Logica do movimento de parar e andar--------------------

        self.pause_duration = 1000  # Ela fica parada por 1 segundo
        self.pause_end_time = 0     # Variavel que vai receber quando ela deve parar no futuro
    
    # ------------ Logica do ataque -------------------------------   
        self.staight_cooldown = straight_cooldown                                   # Cooldown de cada ataque danmaku dos bosses
        self.spread_cooldown = spread_cooldown                                      
        self.burst_cooldown = burst_cooldown
        self.spiral_cooldown = spiral_cooldown                         
        self.last_shot_time = pygame.time.get_ticks()


    
        self.spiral_angle = 0                                           #Angulo inicial pro ataque espiral

   


#-----------------------Movimentos------------------------------------------------------------
    def move_left_right(self,dt):                           #Vai ficar indo do lado pro outro
        self.pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self.pos.x)
        if self.rect.right > playable_rect.right:           #Metodo pra nao escapar da tela jogavel
           self.rect.right = playable_rect.right
           self.pos.x = self.rect.x                         #Sincroniza o vetor pra posiçao dentro da area jogavel
           self.direction.x *= -1                           #Multiplica por -1 pra ir pra outra direçao
        elif self.rect.left < playable_rect.left:
            self.rect.left = playable_rect.left
            self.pos.x = self.rect.x 
            self.direction.x *= -1

    def move_and_pause(self, dt):                           #Esse aqui ela anda pro lado, para, e move pro outro lado, para.

        now = pygame.time.get_ticks()

                                                            #Se o tempo atual for menor que o timer da parada, ela ta parada
        if now < self.pause_end_time:   
            return                                          #nesse estado pula toda funçao

        
        self.pos.x += self.direction.x * self.speed * dt    #Quando ela nao ta parada, executa o movimento
        self.rect.x = round(self.pos.x)


        hit_right_wall = self.rect.right > playable_rect.right     #Checa se colidiu com a parede da direita ou esquerda
        hit_left_wall = self.rect.left < playable_rect.left

        if hit_right_wall or hit_left_wall:
                                                                     #prende ela na posiçao pra nao fugir
            if hit_right_wall:
                self.rect.right = playable_rect.right
            else: 
                self.rect.left = playable_rect.left
            self.pos.x = self.rect.x                                 #ajusta a posiçao do pos pra logica do movimento funcionar

                                                                    #Reverte a direçao pra andar na outra direçao
            self.direction.x *= -1
            
    
            self.pause_end_time = now + self.pause_duration         #define quando ela deve parar no futuro, somando o tempo atual com a duraçao do pause
#-----------------------Danmaku Patterns ------------------------------------------------
    def danmaku_spiral(self):                                                                   #Ataque espiral

        #calcula o angulo pro Danmaku
        angle_rad = math.radians(self.spiral_angle)                                             #transforma em radianos pro python
        direction = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad))                    #pega o Cos e Sen do angulo para o vetor direction 

        Danmaku(cirno_danmaku, self.rect.center, direction, 80, all_sprites, danmaku_sprites)   #Cria um Danmaku com essa direçao

       
        increment = random.uniform(8, 12)                                                       #Incrementa para proxima direçao
        self.spiral_angle = (self.spiral_angle + increment) % 360                               #Vai ate 360
    
    


    def danmaku_straight(self, player, speed=500, num_bullets=1, step=30):
     
        player_pos = pygame.Vector2(player.rect.center)
        boss_pos = pygame.Vector2(self.rect.center)
        direction = player_pos - boss_pos
        if direction.length() == 0:
            direction = pygame.Vector2(0, 1)
        else:
            direction = direction.normalize()


        # Usa um loop para criar as balas, subtraindo da posiçao do boss a direçao multiplicada pelo numero da bala e step
        for i in range(num_bullets):
            #As balas novas ficam a um step de distancia atras da outra
            start_pos = boss_pos - direction * i * step

            # Cria a bala naquela posição
            Danmaku(cirno_kunai, start_pos, direction, speed, all_sprites, danmaku_sprites)


                                                                 

    def danmaku_spread_attack(self, player, num_bullets=5, angle_spread=60):                    #Ataque escopeta 
        #Primeiro pega a posiçao do jogador e do boss
        boss_pos = pygame.Vector2(self.rect.center)
        player_pos = pygame.Vector2(player.rect.center)

        #calcula a "mira" pro player, subtraindo os vetores, do player pelo vetor do boss
        direction_vector = player_pos - boss_pos

        #Usa o atan2, que faz o oposto da funçao tangente, a arcotangente recebe as coordenadas y,x e devolve um angulo
        angle_to_player = math.degrees(math.atan2(direction_vector.y, direction_vector.x)) 

        #Calcula o angulo inicial do tiro subtraindo do centro do jogador metade do angulo do "leque"
        start_angle = angle_to_player - (angle_spread / 2)          

        #Calcula o step entre cada angulo, dividindo o angulo do leque pelo numero de balas do ataque                            
        angle_step = angle_spread / (num_bullets - 1) if num_bullets > 1 else 0

        #Usa o loop pra calcular a distancia entre cada bala, multiplicando step pelo numero da bala e somando no angulo inicial
        for i in range(num_bullets):
            angle = math.radians(start_angle + i * angle_step)
            direction = pygame.Vector2(math.cos(angle), math.sin(angle))
            Danmaku(cirno_kunai, self.rect.center, direction, 250, all_sprites, danmaku_sprites)
    

    def danmaku_random_burst(self, num_bullets, speed):
        # As balas vao sair do centro da Cirno
        start_pos = self.rect.center

        for _ in range(num_bullets):
            #Gera um angulo aleatorio pra cada bala
            random_angle = random.uniform(0, 360)

            #converte pra radianos pro python usar 
            angle_rad = math.radians(random_angle)

            #cria um vetor a partir desse angulo aleatorio
            direction = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad))

            #Cria a bala com esse essa posiçao nova 
            Danmaku(cirno_danmaku, start_pos, direction, speed, all_sprites, danmaku_sprites)

    # --- ----------------------------Logica das fases----------------------------------------------
    def update_phase_0(self, dt, now): 
        self.move_and_pause(dt)                                 #Fase 0
        if now - self.last_shot_time >= self.staight_cooldown:   #Tempo entre cada disparo    
            self.danmaku_straight(player, speed=500, num_bullets=4, step=30)
            self.last_shot_time = now                                   #Reseta depois do tiro
    


    def update_phase_1(self, dt, now):                                  #Fase 1
        self.move_left_right(dt)
        if now - self.last_shot_time >= self.spread_cooldown:
            self.danmaku_spread_attack(player)
            self.last_shot_time = now

    def update_phase_2(self, dt, now):
        init_x = playable_rect.centerx                                  #Primeiro a Cirno volta ao centro da tela

        if not math.isclose(self.rect.centerx, init_x, abs_tol=5):      #Verifica se ela ta perto do centro da tela, com tolerancia de 5 pixels
            if self.rect.centerx < init_x:
               self.pos.x += self.speed * dt                           #Volta pra posiçao andando ate o centro
            else:
                self.pos.x -= self.speed * dt
            self.rect.centerx = round(self.pos.x)
    
        else:                                                           #Quando chega no centro, começa a atirar o Ataque espral       
            if now - self.last_shot_time >= self.burst_cooldown:                        # Cooldown de 1.5 segundos entre explosões
                self.danmaku_random_burst(20, 90) # Chama o novo ataque
                self.last_shot_time = now
    
    def check_phase_transition(self, now):                              #Funçao pra checar se ta na hora de mudar de fase

        if self.life <= self.max_life / 2 and self.phase == 0 and not self.is_in_transition:
            self.phase = 1
            self.is_in_transition = True
            self.transition_start_time = now


        elif self.life <= self.max_life / 4 and self.phase == 1 and not self.is_in_transition:
            self.phase = 2
            self.is_in_transition = True
            self.transition_start_time = now
         


    def update(self, dt):
        if not self.alive:                                                               #Se nao tiver viva, retorna nada
            return

        now = pygame.time.get_ticks()
        
                                                                                         #Logica do cooldown da transiçao de fase
        if self.is_in_transition:
            if now - self.transition_start_time >= self.transition_time:                 #Tempo de transiçao
                self.is_in_transition = False
                self.last_shot_time = now                                                #Reseta o ultimo ataque como medida pra ela nao atirar instantaniamente
                
            return                                                                       

                                                                                        #Executa a logica da fase 0
        if self.phase == 0:
            self.update_phase_0(dt, now)

        elif self.phase == 1:                                                           #Executa a logica da fase 1
            self.update_phase_1(dt, now) 

        elif self.phase == 2:                                                           #Executa a logiica da fase 2                
            self.update_phase_2(dt, now)
                                                                                        
        self.check_phase_transition(now)                                                #Checa se ta a vida do boss ja ta no momento pra mudar de fase

                                                                                                
        self.rect.clamp_ip(playable_rect)                                              #Mantem a Cirno presa na tela jogavel
   

       
class Cirno(Boss_fight):
    def __init__(self, groups, boss_sprites):
        life = 300
        speed = 200
        transition_time = 1000
        straight_cooldown = 700
        spread_cooldown = 700
        burst_cooldown = 100
        spiral_cooldown = 0                 #Nao vou usar essa na cirno
        
        # Chama a classe mãe com o sprite e os atributos da Cirno
        super().__init__(
            surf=cirno_surf, 
            max_life=life, 
            speed=speed,
            transition_time = transition_time,
            straight_cooldown=straight_cooldown, 
            spread_cooldown=spread_cooldown, 
            burst_cooldown=burst_cooldown,
            spiral_cooldown=spiral_cooldown,
            groups=groups, 
            boss_sprites=boss_sprites
        )

class Remilia(Boss_fight):
    def __init__(self, groups, boss_sprites):
        life = 400
        speed = 200
        transition_time = 2000
        straight_cooldown = 700
        spread_cooldown = 700
        burst_cooldown = 500
        spiral_cooldown = 150
        
        # Chama a classe mãe com o sprite e os atributos da Remilia
        super().__init__(
            surf=remilia_surf, 
            max_life=life, 
            speed=speed,
            transition_time=transition_time,
            straight_cooldown=straight_cooldown, 
            spread_cooldown=spread_cooldown, 
            burst_cooldown=burst_cooldown,
            spiral_cooldown=spiral_cooldown,
            groups=groups, 
            boss_sprites=boss_sprites
        )

    def update_phase_0(self, dt, now):
        if now - self.last_shot_time >= self.spread_cooldown:
            self.danmaku_spread_attack(player)
            self.last_shot_time = now

    def update_phase_1(self, dt, now):
        self.move_left_right(dt)       
        if now - self.last_shot_time >= 250: # Cooldown de 1.5 segundos entre explosões
            self.danmaku_random_burst(num_bullets=4, speed=200) # Chama o novo ataque
            self.last_shot_time = now

    def update_phase_2(self, dt, now):                              
        init_x = playable_rect.centerx                                  #Primeiro a Remilia volta ao centro da tela

        if not math.isclose(self.rect.centerx, init_x, abs_tol=5):      #Verifica se ela ta perto do centro da tela, com tolerancia de 5 pixels
            if self.rect.centerx < init_x:
               self.pos.x += self.speed * dt                           #Volta pra posiçao andando ate o centro
            else:
                self.pos.x -= self.speed * dt
            self.rect.centerx = round(self.pos.x)
        else:    
            self.danmaku_spiral()
            if now - self.last_shot_time >= self.burst_cooldown:    
                self.danmaku_random_burst(10, 200)
                self.last_shot_time = now                                   

    def danmaku_random_burst(self, num_bullets, speed):
        # As balas vao sair do centro da Cirno
        start_pos = self.rect.center

        for _ in range(num_bullets):
            #Gera um angulo aleatorio pra cada bala
            random_angle = random.uniform(0, 180)

            #converte pra radianos pro python usar 
            angle_rad = math.radians(random_angle)

            #cria um vetor a partir desse angulo aleatorio
            direction = pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad))

            #Cria a bala com esse essa posiçao nova 
            Danmaku(remilia_ball, start_pos, direction, speed, all_sprites, danmaku_sprites)

    def danmaku_spread_attack(self, player, num_bullets=9, angle_spread=180):                    #Ataque escopeta 
        #Primeiro pega a posiçao do jogador e do boss
        boss_pos = pygame.Vector2(self.rect.center)
        player_pos = pygame.Vector2(player.rect.center)

        #calcula a "mira" pro player, subtraindo os vetores, do player pelo vetor do boss
        direction_vector = player_pos - boss_pos

        #Usa o atan2, que faz o oposto da funçao tangente, a arcotangente recebe as coordenadas y,x e devolve um angulo
        angle_to_player = math.degrees(math.atan2(direction_vector.y, direction_vector.x)) 

        #Calcula o angulo inicial do tiro subtraindo do centro do jogador metade do angulo do "leque"
        start_angle = angle_to_player - (angle_spread / 2)          

        #Calcula o step entre cada angulo, dividindo o angulo do leque pelo numero de balas do ataque                            
        angle_step = angle_spread / (num_bullets - 1) if num_bullets > 1 else 0

        #Usa o loop pra calcular a distancia entre cada bala, multiplicando step pelo numero da bala e somando no angulo inicial
        for i in range(num_bullets):
            angle = math.radians(start_angle + i * angle_step)
            direction = pygame.Vector2(math.cos(angle), math.sin(angle))
            Danmaku(remilia_ball, self.rect.center, direction, 250, all_sprites, danmaku_sprites)


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
        self.ui_color = (white)

 # --------------------------- Icone da vida------------------------ ---
        self.life_icon = pygame.image.load('assets/player/Hearth_icon.png')
        self.life_icon = pygame.transform.scale(self.life_icon, (20, 20))
        self.life_icon_rect = self.life_icon.get_rect(topleft=(620, 100))                                   #Talvez eu coloque mais em baixo depois?

#---------------------------Icone Ghost mode ---------------------------
        self.ghost_icon = pygame.image.load('assets/player/Ghost_icon.png')
        self.ghost_icon = pygame.transform.scale(self.ghost_icon, (20, 20))
        self.ghost_icon_rect = self.ghost_icon.get_rect(topleft=(620,150))

    def draw_score(self):
        score_text = str(pygame.time.get_ticks() // 100)                                                   #Score do jogo, baseado no tempo
        text_surf = font_ui.render(f'Score: {score_text}', True, self.ui_color)
        text_rect = text_surf.get_frect(topright=(VIRTUAL_WIDTH - 20, 40))
        self.image.blit(text_surf, text_rect)

    def draw_player_lives(self):                                                                           #Ui da vida do jogador
        for i in range(self.player.lives):                                                                 #Loop que itera na quantidade de vida que o plahyer tem                                   
            x_pos = self.life_icon_rect.left + (i * (self.life_icon_rect.width + 5))                       #offset de 5 pixels entre cada icone e a largura
            y_pos = self.life_icon_rect.top
            self.image.blit(self.life_icon, (x_pos, y_pos))

    def draw_player_ghost(self):
        for i in range(self.player.ghost_power):
            x_pos = self.ghost_icon_rect.left + (i *(self.ghost_icon_rect.width + 5))
            y_pos = self.ghost_icon_rect.top
            self.image.blit(self.ghost_icon, (x_pos, y_pos))

    def draw_boss_health(self):
    
        max_width = 300                                                                        #Tamanho total da barra
        health_ratio = self.boss.life / self.boss.max_life                                     #Porcetagem da vida do Boss
        health_width = int(max_width * health_ratio)                                           #Tamanho da barra enquanto diminui

    
        x, y = VIRTUAL_WIDTH // 2 - max_width // 2, 10                                         #Posiçao da barra
        bar_height = 10                                                                        #Altura da barra

      
        pygame.draw.rect(self.image, (gray), (x, y, max_width, bar_height))            # Background da barra
        pygame.draw.rect(self.image, (red), (x, y, health_width, bar_height))           # Barra da vida
        pygame.draw.rect(self.image, (white), (x, y, max_width, bar_height), 2)     # Borda da barra

    def draw_graze(self):
        graze_text = str(int(self.player.graze_score)) 
        text_surf = font_ui.render(f'Graze: {graze_text}', True, self.ui_color)
        text_rect = text_surf.get_frect(topright=(VIRTUAL_WIDTH - 20, 70))
        self.image.blit(text_surf, text_rect)

    def update(self, dt):
        self.image.fill((0, 0, 0, 0))     #Cada vez que o update roda, a tela e pintada de transparente 
                                        #Isso e extremamente necessario pq a tela ta sendo atualizada a todo momento, para nao sobscrever tudo
        self.draw_player_lives()
        self.draw_boss_health()
        self.draw_score()
        self.draw_graze()
        self.draw_player_ghost()


#Funçao das colisoes do jogo
def collisions(dt):

#----------------------Player colisoes------------------------------------------------------------------------------
    
                                                                                #Logica da colisao da esfera de hitbox
    player_center = pygame.Vector2(player.rect.center)                          #Pega um vetor do centro do rect do player
    for danmaku in danmaku_sprites:                                         
        danmaku_center = pygame.Vector2(danmaku.rect.center)                    #Pega um vetor do centro da Danmaku
        distance = player_center.distance_to(danmaku_center)                    
        
        if distance < player.hitbox_radius and not player.invicible:            #Se a distancia for maior que o raio da hitbox, tome :)
            if not player.invicible:                               
                player.lives -= 1                                       
                death_sfx.play()
                player.invicible = True
                player.last_hit_time = pygame.time.get_ticks()
                player.frame_count = 0
                player.rect.center = (VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT - 50)
    
                if player.lives <= 0:
                    player.kill()
                    
            continue
        #Logica do Graze
        if distance < player.graze_radius:
            # Adiciona pontos de graze com base na taxa e no tempo do quadro (dt)
            player.graze_score += player.graze_rate * dt
            graze_sfx.play()

#-------------------Bullet Colisoes -------------------------------------------------------------
    for bullet in bullet_sprites:
        colided = pygame.sprite.spritecollide(bullet,boss_sprites,False,pygame.sprite.collide_mask)   
        if colided:                                                             #Verifica se a mascara da bullet colidiu com a mascara do boss
            current_boss.life -= 1
            bullet.kill()
            if current_boss.life == 0:
                current_boss.kill()
                current_boss.alive = False
                pygame.mixer.music.stop()


def reset_game():
    global player, cirno, ui_elements, all_sprites, danmaku_sprites, bullet_sprites, boss_sprites, ui_sprites

    # Apaga todos os sprites dos grupos
    all_sprites.empty()
    danmaku_sprites.empty()
    bullet_sprites.empty()
    boss_sprites.empty()
    ui_sprites.empty()

    # Recria os objetos
    player = Player(all_sprites)
    ui_elements = Ui(player, None, all_sprites, ui_sprites) 
    transition_screen = False
    boss_stage = 1
    spawn_boss(boss_stage)

    #Reinicia a musica
    pygame.mixer.music.load('assets/sfx/Tomboyish Girl in Love.mp3')
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)


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


def spawn_boss(stage):
    global current_boss, ui_elements

    # Garante que o chefe anterior seja removido do jogo
    if current_boss:
        current_boss.kill()

    if stage == 1:
        # Cria uma instância da Cirno
        current_boss = Cirno(groups=(all_sprites, boss_sprites), boss_sprites=boss_sprites)

    
    elif stage == 2:
        # Cria uma instância da Remilia
        current_boss = Remilia(groups=(all_sprites, boss_sprites), boss_sprites=boss_sprites)
        
        player.ghost_power += 1
        player.lives += 2
        life_up_sfx.play()

        pygame.mixer.music.load('assets\sfx/13. Septette for a Dead Princess.mp3')
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play(-1)

    #Atualiza a UI para monitorar a vida do novo chefe
    ui_elements.boss = current_boss


#Essencial do jogo
running = True
clock = pygame.time.Clock()  # FPS


#Telas de inicio, vitoria e morte
start_screen = True
options_screen = False
game_over = False
victory_screen = False

transition_screen = False       #Transiction screen è uma tela criada momentaneamente por 6 segundos para fazer o efeito da remilia aparecendo dramaticamente
transition_duration = 6000      #Ela é desativada logo apos os 6 segundos, rodando o loop do jogo normalmente depois
transition_start_time = 0


#Grupo de Sprites
all_sprites = pygame.sprite.Group()
danmaku_sprites = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()
boss_sprites = pygame.sprite.Group()
ui_sprites = pygame.sprite.Group()

#Criacao dos objetos
boss_stage = 1          # 1 para Cirno, 2 para Remilia
current_boss = None     # Vai armazenar o objeto do chefe atual
player = Player(all_sprites) # O player é criado uma vez aqui
ui_elements = Ui(player, None, all_sprites, ui_sprites) # A ui começa com None e vai atualizar para o curremt_boss



#Musica do menu
pygame.mixer.music.load('assets/sfx/01. Eternal Night Vignette ~ Eastern Night.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)


#Game loop
while running:
    #delta time
    dt = clock.tick()/1000  # FPS

    mouse_pos = pygame.mouse.get_pos()
        
    #Logica para funcionamento do Input do mouse
    scale_factor, x_offset, y_offset = scale_and_offset()           #Pega o offset e a escala da tela
    virtual_mouse_x = (mouse_pos[0] - x_offset) / scale_factor
    virtual_mouse_y = (mouse_pos[1] - y_offset) / scale_factor
    virtual_mouse_pos = (virtual_mouse_x, virtual_mouse_y)

    #Teclas pressionadas
    keys = pygame.key.get_pressed()

    #event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: 
                running = False
            if event.key == pygame.K_BACKSPACE: 
                start_screen = True
                game_over = False
                victory_screen = False
                pygame.mixer.music.load('assets/sfx/01. Eternal Night Vignette ~ Eastern Night.mp3')
                pygame.mixer.music.play(-1)
    

      
    if player.lives <= 0 and not game_over:                                               #Checa se o player ta vivo
        game_over = True
        pygame.mixer.music.stop()
        death_sfx.play()
        continue


    if start_screen:
        virtual_surface.fill(black)
        virtual_surface.blit(start_img)
        if start_button.drawn(virtual_surface,virtual_mouse_pos):
            start_screen = False
            game_over = False
            reset_game()
            pygame.mixer.music.load('assets/sfx/Tomboyish Girl in Love.mp3')  #toca musica quando começa
            pygame.mixer.music.set_volume(0.1)  
            pygame.mixer.music.play(-1)
        if options_button.drawn(virtual_surface, virtual_mouse_pos):
            options_screen = True
            start_screen = False
        if exit_button.drawn(virtual_surface, virtual_mouse_pos):
            cancel_sfx.play()
            running = False
        
        
    elif options_screen:
        virtual_surface.blit(start_img)

        title_surf = font_medium.render("Controles", True, white)
        title_rect = title_surf.get_frect(center=(150,100))
        virtual_surface.blit(title_surf, title_rect)

        controls = [
        ("Shoot:  Z", 200),
        ("UP,DOWN:  up_arrow, down_arrow", 300),
        ("Left, Right:  left_arrow, right_arrow", 400),
        ("Ghost mode:  X", 500)
        ]

        for text, y_pos in controls:
            text_surf = font_text.render(text, True, yellow)
            text_rect = text_surf.get_frect(center=(VIRTUAL_WIDTH / 2, y_pos)) 
            virtual_surface.blit(text_surf, text_rect)

        if exit_button.drawn(virtual_surface, virtual_mouse_pos):
            cancel_sfx.play()
            options_screen = False
            start_screen = True
        
        
    elif game_over:
        virtual_surface.blit(score_img)
        text = font_title.render("YOU DIED", True, white)
        text_rect = text.get_rect(center=(VIRTUAL_WIDTH / 2, VIRTUAL_HEIGHT / 2 - 100))
        virtual_surface.blit(text, text_rect)
        if exit_button.drawn(virtual_surface, virtual_mouse_pos):
            cancel_sfx.play()
            game_over = False
            start_screen = True
            pygame.mixer.music.load('assets/sfx/01. Eternal Night Vignette ~ Eastern Night.mp3')
            pygame.mixer.music.play(-1)

    elif victory_screen:
        virtual_surface.blit(score_img)
        
        title_text = font_title.render("Results:", True, white)
        title_rect = title_text.get_rect(topleft=(100,100))
        virtual_surface.blit(title_text, title_rect)
    
        total_score = final_score + final_graze * player.lives * player.ghost_power                                      #Pontuaçao final do jogo é a soma do graze com os pontos
        total_surf = font_medium.render(f"Total Score: {total_score}", True, yellow)
        total_rect = total_surf.get_rect(topleft=(100,200))
        virtual_surface.blit(total_surf,total_rect)

        if exit_button.drawn(virtual_surface, virtual_mouse_pos):
            cancel_sfx.play()
            game_over = False
            start_screen = True
            pygame.mixer.music.stop()
            pygame.mixer.music.load('assets/sfx/01. Eternal Night Vignette ~ Eastern Night.mp3')
            pygame.mixer.music.play(-1)

    elif transition_screen:
        now = pygame.time.get_ticks()
        if now - transition_start_time >= transition_duration:
            transition_screen = False
            boss_stage = 2
            spawn_boss(boss_stage)
        virtual_surface.fill(black)

        # Atualiza os sprites que ainda existem (player)
        all_sprites.update(dt)
        collisions(dt) # Continua checando colisões para o graze e balas perdidas

        # Desenha o fundo e a área jogável
        virtual_surface.blit(background_img, (0,0))
        virtual_surface.blit(playable_field, PLAYABLE_POS)

        # Desenha os sprites dentro da área jogável
        virtual_surface.set_clip(playable_rect)
        for sprite in all_sprites:
            virtual_surface.blit(sprite.image, sprite.rect)
        if keys[pygame.K_LSHIFT]:
            player.draw_hitbox(virtual_surface)
        virtual_surface.set_clip(None)

        # Desenha a UI
        ui_sprites.draw(virtual_surface)

    else:
                                      
        if current_boss and not current_boss.alive:                               #Se a cirno morrer, vitoria :)
            if boss_stage == 1 and not transition_screen:
                transition_screen = True
                transition_start_time = pygame.time.get_ticks()
            elif boss_stage == 2 and not victory_screen:
                victory_screen = True
                final_score = pygame.time.get_ticks() // 100
                final_graze = int(player.graze_score)
                pygame.mixer.music.stop()
                pygame.mixer.music.load('assets/sfx/persona4.mp3')
                pygame.mixer.music.play(-1)

            continue

        else:

            virtual_surface.fill(black)                         #Preenche a tela de preto pra esconder as telas anteriores

            # Atualizações 
            all_sprites.update(dt)
            collisions(dt)


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




        

        
    
    scaled_screen()
    pygame.display.update()


pygame.quit()


