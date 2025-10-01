
import os
import threading
import time

import pygame

import auxiliar as aux  # Recursos auxiliares do código
from sfb import SfbSimulator # Importar a classe do simulador de incêndios
from auxiliar import *
from datetime import datetime

# Variáveis globais para o gráfico
continuar_execucao = True
x_points = []
y_points = [[], [], []]

def update_grafico(orr):  # Função para atualizar o gráfico que será executada em paralelo
    global continuar_execucao, x_points, y_points
    while continuar_execucao:
        orr.update(x_points, y_points)
        time.sleep(1)

class ProjectSfb:
    # Cores código RGB
    Azul = [0, 74, 173]
    Verde = [126, 217, 87]
    Preto = [0, 0, 0]
    Branco = [255, 255, 255]
    Azul_escuro = [36, 62, 106]
    Verde_abacate = [153, 204, 35]
    Ciano = [6, 168, 228]
    Cinza = [62, 68, 67]
    Verde_limao = [93, 173, 77]
    Vermelho = [226, 50, 54]
    Bege = [240, 240, 240]
    Laranja = [255, 165, 0] # Cor para vegetação baixa
    Marrom = [139, 69, 19] # Cor para vegetação média
    Verde_escuro = [0, 50, 0] # Cor para vegetação alta
    Verde_claro = [144, 238, 144]
    Verde_neutro = [0, 128, 0]

    def __init__(self):
        pygame.init()

        # Obter a resolução atual do monitor
        info = pygame.display.Info()
        screen_width = info.current_w
        screen_height = info.current_h

        # Definir uma proporção máxima para a janela do simulador (ex: 90% da tela)
        max_width = int(screen_width * 0.9)
        max_height = int(screen_height * 0.9)

        # Manter a proporção 16:9 ou ajustar para a proporção da tela se for mais restritiva
        aspect_ratio = 16 / 9
        calculated_width = max_width
        calculated_height = int(max_width / aspect_ratio)

        if calculated_height > max_height:
            calculated_height = max_height
            calculated_width = int(max_height * aspect_ratio)

        self.width = calculated_width
        self.height = calculated_height

        self.state = "MainMenu"

        self.selected_distribution = 0 # 0: Uniforme, 1: Mais baixa, 2: Mais alta
        self.selected_wind_direction = "norte" # norte, sul, leste, oeste
        self.selected_wind_speed = 1 # 1 ou 2

    def start(self):
        icon_surface = pygame.Surface([32, 32], pygame.SRCALPHA)
        pygame.display.set_icon(icon_surface)

        while self.state != "Quit":
            if self.state == "MainMenu":
                self.main_menu()
            elif self.state == "SfbSimulation":
                self.sfb_simulation()

        pygame.quit()

    def main_menu(self):
        pygame.display.set_caption("Simulador de Incêndios")
        screen = pygame.display.set_mode([self.width, self.height], pygame.RESIZABLE)
        clock = pygame.time.Clock()
        running = True

        width_button, height_button = 250, 50
        textos = ["Iniciar Simulação", "Configurações", "Sair"]
        botoes = [
            pygame.Rect((self.width - width_button) // 2, 0, width_button, height_button) for _ in range(len(textos))
        ]

        while running:
            clock.tick(30)
            screen.fill(self.Preto)

            aux.align_buttons_center(screen, botoes, textos, self.Azul_escuro, self.Branco)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.state = "Quit"

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, button_rect in enumerate(botoes):
                        if button_rect.collidepoint(pygame.mouse.get_pos()):
                            if i == 0:
                                self.state = "SfbSimulation"
                            elif i == 1:
                                self.config_menu()
                                pygame.display.set_mode([self.width, self.height], pygame.RESIZABLE) # Re-set display after config menu
                                pygame.display.set_caption("Simulador de Incêndios")
                            elif i == 2:
                                self.state = "Quit"
                            running = False

                            aux.create_button(screen, button_rect, textos[i], self.Azul, self.Branco, clicado=True)
                            pygame.display.flip()
                            pygame.time.wait(100)
                            aux.create_button(screen, button_rect, textos[i], self.Azul, self.Branco, clicado=False)

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        self.state = "Quit"

            pygame.display.flip()

    def config_menu(self):
        pygame.display.set_caption("Configurações")
        screen = pygame.display.set_mode([self.width, self.height], pygame.RESIZABLE)
        clock = pygame.time.Clock()
        running = True

        width_button, height_button = 300, 50

        # Botões para distribuição de vegetação
        veg_dist_texts = ["Realismo", "Risco", "Didático"]
        veg_dist_buttons = [
            pygame.Rect((self.width - width_button) // 2, 100 + i * (height_button + 10), width_button, height_button)
            for i in range(len(veg_dist_texts))
        ]

        # Botões para direção do vento
        wind_dir_texts = ["Vento: Norte", "Vento: Sul", "Vento: Leste", "Vento: Oeste"]
        wind_dir_buttons = [
            pygame.Rect((self.width - width_button) // 2, 300 + i * (height_button + 10), width_button, height_button)
            for i in range(len(wind_dir_texts))
        ]

        # Botões para velocidade do vento
        wind_speed_texts = ["Velocidade Vento: 1", "Velocidade Vento: 2"]
        wind_speed_buttons = [
            pygame.Rect((self.width - width_button) // 2, 550 + i * (height_button + 10), width_button, height_button)
            for i in range(len(wind_speed_texts))
        ]

        back_button_rect = pygame.Rect((self.width - width_button) // 2, self.height - 100, width_button, height_button)

        while running:
            clock.tick(30)
            screen.fill(self.Preto)

            # Desenhar botões de distribuição de vegetação
            for i, button_rect in enumerate(veg_dist_buttons):
                color = self.Azul_escuro if self.selected_distribution != i else self.Ciano
                aux.create_button(screen, button_rect, veg_dist_texts[i], color, self.Branco)

            # Desenhar botões de direção do vento
            for i, button_rect in enumerate(wind_dir_buttons):
                direction = ["norte", "sul", "leste", "oeste"][i]
                color = self.Azul_escuro if self.selected_wind_direction != direction else self.Ciano
                aux.create_button(screen, button_rect, wind_dir_texts[i], color, self.Branco)

            # Desenhar botões de velocidade do vento
            for i, button_rect in enumerate(wind_speed_buttons):
                speed = i + 1
                color = self.Azul_escuro if self.selected_wind_speed != speed else self.Ciano
                aux.create_button(screen, button_rect, wind_speed_texts[i], color, self.Branco)

            # Botão de voltar
            aux.create_button(screen, back_button_rect, "Voltar", self.Vermelho, self.Branco)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.state = "Quit"

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()

                    # Lógica para botões de distribuição de vegetação
                    for i, button_rect in enumerate(veg_dist_buttons):
                        if button_rect.collidepoint(mouse_pos):
                            self.selected_distribution = i
                            aux.create_button(screen, button_rect, veg_dist_texts[i], self.Ciano, self.Branco, clicado=True)
                            pygame.display.flip()
                            pygame.time.wait(100)
                            aux.create_button(screen, button_rect, veg_dist_texts[i], self.Ciano, self.Branco, clicado=False)

                    # Lógica para botões de direção do vento
                    for i, button_rect in enumerate(wind_dir_buttons):
                        if button_rect.collidepoint(mouse_pos):
                            self.selected_wind_direction = ["norte", "sul", "leste", "oeste"][i]
                            aux.create_button(screen, button_rect, wind_dir_texts[i], self.Ciano, self.Branco, clicado=True)
                            pygame.display.flip()
                            pygame.time.wait(100)
                            aux.create_button(screen, button_rect, wind_dir_texts[i], self.Ciano, self.Branco, clicado=False)

                    # Lógica para botões de velocidade do vento
                    for i, button_rect in enumerate(wind_speed_buttons):
                        if button_rect.collidepoint(mouse_pos):
                            self.selected_wind_speed = i + 1
                            aux.create_button(screen, button_rect, wind_speed_texts[i], self.Ciano, self.Branco, clicado=True)
                            pygame.display.flip()
                            pygame.time.wait(100)
                            aux.create_button(screen, button_rect, wind_speed_texts[i], self.Ciano, self.Branco, clicado=False)

                    # Lógica para botão de voltar
                    if back_button_rect.collidepoint(mouse_pos):
                        running = False
                        self.state = "MainMenu"
                        aux.create_button(screen, back_button_rect, "Voltar", self.Vermelho, self.Branco, clicado=True)
                        pygame.display.flip()
                        pygame.time.wait(100)
                        aux.create_button(screen, back_button_rect, "Voltar", self.Vermelho, self.Branco, clicado=False)

                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        self.state = "MainMenu"

            pygame.display.flip()

    def sfb_simulation(self):
        global continuar_execucao, x_points, y_points
        controller = True

        pygame.display.set_caption("Simulação de Propagação de Incêndios")
        screen = pygame.display.set_mode([self.width, self.height], pygame.RESIZABLE)
        clock = pygame.time.Clock()

        surface1 = pygame.Surface((int(self.width * 0.75), self.height))
        surface2 = pygame.Surface((int(self.width * 0.25), self.height))
        surface1.fill(self.Azul_escuro)
        surface2.fill(self.Verde)

        grid = SfbSimulator(width=surface1.get_width(), height=surface1.get_height(), scale=10, offset=1, padding=10)
        grid.random_grid(self.selected_distribution)
        grid.set_wind_direction(self.selected_wind_direction)
        grid.set_wind_speed(self.selected_wind_speed)

        running = True
        pause = True

        g_width_button, g_height_button = 350, 60
        play_pause_button_rect = pygame.Rect((290, 220, g_height_button, g_height_button))
        bg_1 = pygame.Rect((10, 10, g_width_button, g_height_button))

        image_pause = pygame.transform.scale(
            pygame.image.load(os.path.join(os.path.dirname(__file__), "img", "pause.png")),
            (g_height_button, g_height_button),
        )
        image_play = pygame.transform.scale(
            pygame.image.load(os.path.join(os.path.dirname(__file__), "img", "play.png")),
            (g_height_button, g_height_button),
        )

        grafico_sfb = aux.GraficoSFB() # Reutilizando a classe GraficoSIR, mas adaptando para SFB

        continuar_execucao = True
        x_points = grid.t_series
        y_points = [grid.s_series, grid.i_series, grid.r_series]
        threading.Thread(target=update_grafico, args=(grafico_sfb,)).start()

        # Cores para os tipos de vegetação
        veg_colors = {
            0: self.Verde_claro, # Baixa inflamabilidade
            1: self.Verde_neutro, # Média inflamabilidade
            2: self.Verde_escuro # Alta inflamabilidade
        }

        # Criar pasta frames se não existir
        if not os.path.exists("frames"):
            os.makedirs("frames")

        last_saved_gen = -1  # inicializa contador

        while running:
            clock.tick(60)
            screen.fill(self.Azul_escuro)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.state = "Quit"

                if event.type == pygame.KEYUP:
                    running, pause = self.keyup_sfb(event, running, grid, pause)

            self.update_menu_sfb(surface2, bg_1, image_pause, image_play, play_pause_button_rect, grid, pause)

            grid.runnable(
                sus_color=self.Branco, inflam_color=self.Vermelho, queim_color=self.Preto, 
                veg_colors=veg_colors, surface=surface1, pause=pause
            )

            if grid.geracao != last_saved_gen:
                pygame.image.save(surface1, os.path.join("frames", f"grid_{grid.geracao}.png"))
                last_saved_gen = grid.geracao

            x_points = grid.t_series
            y_points = [grid.s_series, grid.i_series, grid.r_series]

            self.interatividade_sfb(grid)

            grafico_height = grafico_sfb.get_surface().get_height()
            grafico_y = 290
            surface2.blit(grafico_sfb.get_surface(), (10, grafico_y))

            play_pause_button_rect = pygame.Rect(
                10,  # mesma margem da esquerda
                grafico_y + grafico_height + 10,  # 10 pixels abaixo do gráfico
                g_height_button,
                g_height_button
            )

            if grid.inflamadas == 0 and grid.geracao > 1: # Se não houver mais células inflamadas, pausa a simulação
                pause = True

            screen.blit(surface1, (0, 0))
            screen.blit(surface2, (int(self.width * 0.75), 0))

            pygame.display.flip()
            pygame.display.update()

        continuar_execucao = False

    def keyup_sfb(self, event, running, grid, pause):
        if event.key == pygame.K_ESCAPE:
            running = False
            self.state = "MainMenu"
        elif event.key == pygame.K_SPACE:
            pause = not pause
        elif event.key == pygame.K_c:
            grid.clear()
            grid.random_grid(self.selected_distribution) # Recria o grid de vegetação com a distribuição selecionada
            pause = True
        elif event.key == pygame.K_r:
            grid.random_grid(self.selected_distribution)
        elif event.key == pygame.K_LEFT and grid.timing > 1:
            grid.timing -= 1
        elif event.key == pygame.K_RIGHT and grid.timing < 60:
            grid.timing += 1
        elif event.key == pygame.K_TAB:
            grid.timing = min(grid.timing + 10, 60)
        elif event.key == pygame.K_LSHIFT:
            grid.timing = max(grid.timing - 10, 1)
        elif pygame.K_1 <= event.key <= pygame.K_7: # Adaptado para as opções de inicialização do fogo
            numero = event.key - pygame.K_0
            grid.standard(numero)
        elif event.key == pygame.K_0:
            grid.standard(0)

        return running, pause

    def update_menu_sfb(self, surface, bg_1, image_pause, image_play, play_pause_button_rect, grid, pause):
        surface.fill(self.Verde_abacate)

        pygame.draw.rect(surface, (0, 0, 0), play_pause_button_rect, border_radius=8)
        surface.blit(image_pause if pause else image_play, play_pause_button_rect.topleft)

        aux.create_button(
            surface, caixa=bg_1, texto="Simulador de Incêndios", cor_texto=self.Branco, cor_caixa=self.Azul_escuro, size=40
        )

        # Informações do grid
        aux.get_values("Geração", grid.geracao, self.Branco, self.Preto, 20, surface, (10, 80, 150, 60), alinhamento="topleft")
        aux.get_values("Suscetíveis", grid.suscetiveis, self.Branco, self.Preto, 20, surface, (170, 80, 150, 60), alinhamento="topleft")
        aux.get_values("Inflamadas", grid.inflamadas, self.Branco, self.Preto, 20, surface, (10, 150, 150, 60), alinhamento="topleft")
        aux.get_values("Queimadas", grid.queimadas, self.Branco, self.Preto, 20, surface, (170, 150, 150, 60), alinhamento="topleft")

        # Informações de vento e distribuição
        aux.get_values("Vento", f"{grid.dir_vento.capitalize()} (Vel: {grid.vel_vento})", self.Branco, self.Preto, 20, surface, (10, 220, 310, 60), alinhamento="topleft")
        
        dist_text = {
            0: "Realismo",
            1: "Risco",
            2: "Didático"
        }.get(self.selected_distribution, "Desconhecida")
        aux.get_values("Distribuição", dist_text, self.Branco, self.Preto, 20, surface, (10, 290, 310, 60), alinhamento="topleft")


    def interatividade_sfb(self, grid):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]: # Suscetível
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid.handle_mouse(mouse_x, mouse_y, status=0)
        if keys[pygame.K_i]: # Inflamada
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid.handle_mouse(mouse_x, mouse_y, status=1)
        if keys[pygame.K_q]: # Queimada
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid.handle_mouse(mouse_x, mouse_y, status=2)

        if pygame.mouse.get_pressed() and pygame.mouse.get_pressed(num_buttons=3)[0]:  # Botão esquerdo do mouse: Inflamar
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid.handle_mouse(mouse_x, mouse_y, status=1)
        elif pygame.mouse.get_pressed() and pygame.mouse.get_pressed(num_buttons=3)[1]:  # Botão scroll do mouse: Suscetível
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid.handle_mouse(mouse_x, mouse_y, status=0)
        elif pygame.mouse.get_pressed() and pygame.mouse.get_pressed(num_buttons=3)[2]:  # Botão direito do mouse: Queimada
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid.handle_mouse(mouse_x, mouse_y, status=2)