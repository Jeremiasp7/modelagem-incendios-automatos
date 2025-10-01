import matplotlib
import matplotlib.backends.backend_agg as agg
import matplotlib.pyplot as plt
import numpy as np
import pygame
import csv
import os

matplotlib.use("Agg")

class GraficoSFB:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(3.5, 2.5), dpi=100)
        self.max_y = 0
        self.raw_data = None
        self.size = None
        self.pygame_surface = None
        self.setup_graph()

    def setup_graph(self):
        self.ax.set_title("Evolução ao longo do tempo", fontweight="bold")
        self.ax.grid(alpha=0.5)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.set_xlabel("Gerações", fontsize=10)
        self.ax.set_ylabel("Quantidade de células", fontsize=10)
        self.ax.tick_params(axis="both", labelsize=8)
        self.fig.subplots_adjust(left=0.2)

        canvas = agg.FigureCanvasAgg(self.fig)
        canvas.draw()
        renderer = canvas.get_renderer()

        self.raw_data = renderer.buffer_rgba()
        self.size = canvas.get_width_height()
        self.pygame_surface = pygame.image.frombuffer(self.raw_data, self.size, "RGBA")
        plt.close()

    def update(self, x, y):
        cores = ["#5dad4d", "#e23236", "#06a8e4"]  # Cores para Suscetíveis, Inflamadas, Queimadas
        legend = ["Suscetíveis", "Inflamadas", "Queimadas"]

        self.ax.clear()

        self.ax.set_title("Evolução ao longo do tempo", fontweight="bold")
        self.ax.grid(alpha=0.5)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.set_xlabel("Gerações", fontsize=10)
        self.ax.set_ylabel("Quantidade de células", fontsize=10)
        self.ax.tick_params(axis="both", labelsize=8)
        self.fig.subplots_adjust(left=0.2)

        self_y_flat = [item for sublist in y for item in sublist] # Flatten the list of lists for max_y calculation

        if self_y_flat:
            self.max_y = max(self_y_flat) + 1000 if max(self_y_flat) > 0 else 1000
        else:
            self.max_y = 1000

        self.ax.scatter(x, y[0], color=cores[0], label=legend[0], s=5)
        self.ax.scatter(x, y[1], color=cores[1], label=legend[1], s=5)
        self.ax.scatter(x, y[2], color=cores[2], label=legend[2], s=5)

        self.ax.legend(loc="lower right", fontsize=6)

        if x:
            self.ax.set_xlim(1, max(x) + 1)
        if y != [[], [], []]:
            self.ax.set_ylim(0, self.max_y)

        canvas = agg.FigureCanvasAgg(self.fig)
        canvas.draw()
        renderer = canvas.get_renderer()

        self.raw_data = renderer.buffer_rgba()
        self.size = canvas.get_width_height()
        self.pygame_surface = pygame.image.frombuffer(self.raw_data, self.size, "RGBA")

    def get_surface(self):
        return self.pygame_surface

def create_button(screen, caixa, texto, cor_caixa, cor_texto, clicado=False, size=36):
    pygame.init()

    if clicado:
        caixa.inflate_ip(-5, -5)

    pygame.draw.rect(screen, cor_caixa, caixa)
    fonte = pygame.font.Font(None, size)
    texto_surface = fonte.render(texto, True, cor_texto)
    texto_caixa = texto_surface.get_rect(center=caixa.center)
    screen.blit(texto_surface, texto_caixa)

    if clicado:
        caixa.inflate_ip(5, 5)

def align_buttons_center(screen, button_box, text_list, cor_caixa, cor_texto, padding=10):
    y_center = (screen.get_height() - button_box[0].height * len(text_list)) // 2

    for i, (button_rect, text) in enumerate(zip(button_box, text_list)):
        button_rect.topleft = (button_rect.topleft[0], y_center + i * (button_rect.height + padding))
        create_button(screen, button_rect, text, cor_caixa, cor_texto)

    pygame.display.flip()

def get_values(texto_label, var_value, cor_texto, cor_var, font_size, screen, box_pos, alinhamento="topleft"):
    font = pygame.font.Font(None, font_size)
    text_label_surface = font.render(texto_label, True, (255, 255, 0))   # Amarelo para o label
    text_var_surface = font.render(str(var_value), True, (255, 255, 255)) # Branco para o valor

    box_rect = pygame.Rect(box_pos)
    pygame.draw.rect(screen, (30, 30, 30), box_rect, border_radius=6)  # Fundo ainda mais escuro e arredondado

    if alinhamento == "topleft":
        text_label_rect = text_label_surface.get_rect(topleft=(box_rect.left + 5, box_rect.top + 5))
        text_var_rect = text_var_surface.get_rect(topleft=(box_rect.left + 5, text_label_rect.bottom + 5))
    else:
        text_label_rect = text_label_surface.get_rect(midtop=(box_rect.centerx, box_rect.top + 5))
        text_var_rect = text_var_surface.get_rect(midtop=(box_rect.centerx, text_label_rect.bottom + 5))

    screen.blit(text_label_surface, text_label_rect)
    screen.blit(text_var_surface, text_var_rect)

def get_resultados(geracao, suscetiveis, inflamadas, queimadas, tipo_grid, modo_distribuicao, vel_vento, dir_vento, queimadas_baixa, queimadas_media, queimadas_alta):
    resultados_dir = os.path.join(os.path.dirname(__file__), "resultados")

    if not os.path.exists(resultados_dir):
        os.makedirs(resultados_dir)

    num_file = len([n for n in os.listdir(resultados_dir)]) + 1
    name_file = os.path.join(resultados_dir, f"teste_{num_file}.csv")

    with open(name_file, "w", newline="", encoding="utf-8") as f:
        csv_f = csv.writer(f)
        csv_f.writerow(["G", "S", "I", "Q", "TipoGrid", "ModoDistribuicao", "Vel_Vento", "Dir_Vento", "Q_Baixa", "Q_Media", "Q_Alta"])
        csv_f.writerow([geracao, suscetiveis, inflamadas, queimadas, tipo_grid, modo_distribuicao, vel_vento, dir_vento, queimadas_baixa, queimadas_media, queimadas_alta])

def get_series(gen, s, i, r):
    series_dir = os.path.join(os.path.dirname(__file__), "resultados_series")

    if not os.path.exists(series_dir):
        os.makedirs(series_dir)

    num_file = len([n for n in os.listdir(series_dir)]) + 1
    name_file = os.path.join(series_dir, f"teste_{num_file}.csv")

    with open(name_file, "w", newline="", encoding="utf-8") as f:
        csv_f = csv.writer(f)
        csv_f.writerow(["G", "S", "I", "Q"])

        for g, s, i, q in zip(gen, s, i, r):
            csv_f.writerow([g, s, i, q])