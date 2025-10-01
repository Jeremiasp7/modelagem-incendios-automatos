import numpy as np
import pygame
from time import sleep

class SfbSimulator:
    def __init__(self, width, height, scale, offset, padding, limit="fixed"):
        self.width = width
        self.height = height
        self.scale = scale
        self.offset = offset
        self.padding = padding
        self.limit = limit

        self.columns = 90
        self.rows = 90
        self.size = (self.columns, self.rows)

        # variaveis de contagem
        self.grid_array = np.zeros(shape=self.size, dtype=int)
        self.suscetiveis = 0
        self.inflamadas = 0
        self.queimadas = 0

        # array identificando os tipos: 0 - baixa, 1 - média, 2 - alta
        self.grid_vegetacao = np.random.choice([0, 1, 2], size=self.size)

        # controle de atualização e geração do grid
        self.timing = 1
        self.geracao = 1

        # arrays de controle
        self.s_series = []
        self.i_series = []
        self.r_series = []
        self.t_series = []

        # características para transição de fase para a vegetação baixa através de uma matriz de preferências para o vento na velocidade 1 *valores são alteráveis
        self.matriz_pref_veg_baixa_v1 = ([
            [0.01, 0.01, 0.01],
            [0.01, 0.0, 0.01],
            [0.01, 0.02, 0.01]
        ])
        self.matriz_pref_veg_baixa_v1_norte = self.matriz_pref_veg_baixa_v1
        self.matriz_pref_veg_baixa_v1_sul = np.rot90(self.matriz_pref_veg_baixa_v1, k=2)
        self.matriz_pref_veg_baixa_v1_leste = np.rot90(self.matriz_pref_veg_baixa_v1, k=3)
        self.matriz_pref_veg_baixa_v1_oeste = np.rot90(self.matriz_pref_veg_baixa_v1, k=1)

        # matriz de preferências da vegeração baixa para o vento na velocidade 2
        self.matriz_pref_veg_baixa_v2 = ([
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.01, 0.01, 0.01, 0.0],
            [0.0, 0.01, 0.0, 0.01, 0.0],
            [0.0, 0.02, 0.03, 0.02, 0.0],
            [0.0, 0.01, 0.02, 0.01, 0.0]
        ])
        self.matriz_pref_veg_baixa_v2_norte = self.matriz_pref_veg_baixa_v2
        self.matriz_pref_veg_baixa_v2_sul = np.rot90(self.matriz_pref_veg_baixa_v2, k=2)
        self.matriz_pref_veg_baixa_v2_leste = np.rot90(self.matriz_pref_veg_baixa_v2, k=3)
        self.matriz_pref_veg_baixa_v2_oeste = np.rot90(self.matriz_pref_veg_baixa_v2, k=1)

        # dicionario das matrizes para a vegetação baixa
        self.matrizes_pref_veg_baixa = {
            (1, "norte"): self.matriz_pref_veg_baixa_v1_norte,
            (1, "sul"): self.matriz_pref_veg_baixa_v1_sul,
            (1, "leste"): self.matriz_pref_veg_baixa_v1_leste,
            (1, "oeste"): self.matriz_pref_veg_baixa_v1_oeste,
            (2, "norte"): self.matriz_pref_veg_baixa_v2_norte,
            (2, "sul"): self.matriz_pref_veg_baixa_v2_sul,
            (2, "leste"): self.matriz_pref_veg_baixa_v2_leste,
            (2, "oeste"): self.matriz_pref_veg_baixa_v2_oeste,
        }

        self.t_det_veg_baixa = 3
        self.grid_carac_veg_baixa = np.full(shape=(self.columns, self.rows, 2), fill_value=-1, dtype=float) # matriz tridimensional com três valores de duas camadas, valores para exposição acumulada e tempo de deterioração de para cada célula
        self.grid_carac_veg_baixa[:, :, 0] = 0 # o estado de exposição acumulada começa em 0 para todas as células do grid
        self.grid_carac_veg_baixa[:, :, 1] = -1 # tempo ainda não iniciado
        self.grid_t_det_veg_baixa = np.full(shape=self.grid_array.shape, fill_value=self.t_det_veg_baixa, dtype=int) # conta regressivamente quando uma célula está queimando até ser deteriorada 

        # características para transição de fase para a vegetação media através de uma matriz de preferências para o vento na velocidade 1 *valores são alteráveis
        self.matriz_pref_veg_media_v1 = ([
            [0.01, 0.02, 0.01],
            [0.02, 0.0, 0.02],
            [0.02, 0.03, 0.02]
        ])
        self.matriz_pref_veg_media_v1_norte = self.matriz_pref_veg_media_v1
        self.matriz_pref_veg_media_v1_sul = np.rot90(self.matriz_pref_veg_media_v1, k=2)
        self.matriz_pref_veg_media_v1_leste = np.rot90(self.matriz_pref_veg_media_v1, k=3)
        self.matriz_pref_veg_media_v1_oeste = np.rot90(self.matriz_pref_veg_media_v1, k=1)
       
       # matriz de preferências da vegeração media para o vento na velocidade 2
        self.matriz_pref_veg_media_v2 = ([
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.01, 0.01, 0.01, 0.0],
            [0.0, 0.02, 0.0, 0.02, 0.0],
            [0.0, 0.03, 0.04, 0.03, 0.0],
            [0.0, 0.01, 0.03, 0.01, 0.0]
        ])
        self.matriz_pref_veg_media_v2_norte = self.matriz_pref_veg_media_v2
        self.matriz_pref_veg_media_v2_sul = np.rot90(self.matriz_pref_veg_media_v2, k=2)
        self.matriz_pref_veg_media_v2_leste = np.rot90(self.matriz_pref_veg_media_v2, k=3)
        self.matriz_pref_veg_media_v2_oeste = np.rot90(self.matriz_pref_veg_media_v2, k=1)

        # dicionario das matrizes para a vegetação media
        self.matrizes_pref_veg_media = {
            (1, "norte"): self.matriz_pref_veg_media_v1_norte,
            (1, "sul"): self.matriz_pref_veg_media_v1_sul,
            (1, "leste"): self.matriz_pref_veg_media_v1_leste,
            (1, "oeste"): self.matriz_pref_veg_media_v1_oeste,
            (2, "norte"): self.matriz_pref_veg_media_v2_norte,
            (2, "sul"): self.matriz_pref_veg_media_v2_sul,
            (2, "leste"): self.matriz_pref_veg_media_v2_leste,
            (2, "oeste"): self.matriz_pref_veg_media_v2_oeste,
        }

        self.t_det_veg_media = 2
        self.grid_carac_veg_media = np.full(shape=(self.columns, self.rows, 2), fill_value=-1, dtype=float)
        self.grid_carac_veg_media[:, :, 0] = 0
        self.grid_carac_veg_media[:, :, 1] = -1
        self.grid_t_det_veg_media = np.full(shape=self.grid_array.shape, fill_value=self.t_det_veg_media, dtype=int)

        # # características para transição de fase para a vegetação alta através de uma matriz de preferências para o vento na velocidade 1 *valores são alteráveis
        self.matriz_pref_veg_alta_v1 = ([
            [0.01, 0.02, 0.01],
            [0.03, 0.0, 0.03],
            [0.03, 0.04, 0.03]
        ])
        self.matriz_pref_veg_alta_v1_norte = self.matriz_pref_veg_alta_v1
        self.matriz_pref_veg_alta_v1_sul = np.rot90(self.matriz_pref_veg_alta_v1, k=2)
        self.matriz_pref_veg_alta_v1_leste = np.rot90(self.matriz_pref_veg_alta_v1, k=3)
        self.matriz_pref_veg_alta_v1_oeste = np.rot90(self.matriz_pref_veg_alta_v1, k=1)

        # matriz de preferências da vegeração alta para o vento na velocidade 2
        self.matriz_pref_veg_alta_v2 = ([
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.01, 0.01, 0.01, 0.0],
            [0.0, 0.03, 0.0, 0.03, 0.0],
            [0.0, 0.04, 0.05, 0.04, 0.0],
            [0.0, 0.01, 0.04, 0.01, 0.0]
        ])
        self.matriz_pref_veg_alta_v2_norte = self.matriz_pref_veg_alta_v2
        self.matriz_pref_veg_alta_v2_sul = np.rot90(self.matriz_pref_veg_alta_v2, k=2)
        self.matriz_pref_veg_alta_v2_leste = np.rot90(self.matriz_pref_veg_alta_v2, k=3)
        self.matriz_pref_veg_alta_v2_oeste = np.rot90(self.matriz_pref_veg_alta_v2, k=1)

        # dicionario das matrizes para a vegetação alta
        self.matrizes_pref_veg_alta = {
            (1, "norte"): self.matriz_pref_veg_alta_v1_norte,
            (1, "sul"): self.matriz_pref_veg_alta_v1_sul,
            (1, "leste"): self.matriz_pref_veg_alta_v1_leste,
            (1, "oeste"): self.matriz_pref_veg_alta_v1_oeste,
            (2, "norte"): self.matriz_pref_veg_alta_v2_norte,
            (2, "sul"): self.matriz_pref_veg_alta_v2_sul,
            (2, "leste"): self.matriz_pref_veg_alta_v2_leste,
            (2, "oeste"): self.matriz_pref_veg_alta_v2_oeste,
        }

        self.t_det_veg_alta = 1
        self.grid_carac_veg_alta = np.full(shape=(self.columns, self.rows, 2), fill_value=-1, dtype=float)
        self.grid_carac_veg_alta[:, :, 0] = 0
        self.grid_carac_veg_alta[:, :, 1] = -1
        self.grid_t_det_veg_alta = np.full(shape=self.grid_array.shape, fill_value=self.t_det_veg_alta, dtype=int)

        self.dir_vento = "norte" # Direção do vento padrão
        self.vel_vento = 1 # Velocidade do vento padrão

    def check(self): # função que conta as células do grid
        self.suscetiveis = np.count_nonzero(self.grid_array == 0)
        self.inflamadas = np.count_nonzero(self.grid_array == 1)
        self.queimadas = np.count_nonzero(self.grid_array == 2)

        if self.geracao not in self.t_series or self.t_series == []:
            self.s_series.append(self.suscetiveis)
            self.i_series.append(self.inflamadas)
            self.r_series.append(self.queimadas)
            self.t_series.append(self.geracao)

        # máscaras de estado
        mask_suscetivel = self.grid_array == 0
        mask_inflamada = self.grid_array == 1
        mask_queimada = self.grid_array == 2

        # máscaras de vegetação
        veg_baixa = self.grid_vegetacao == 0
        veg_media = self.grid_vegetacao == 1
        veg_alta  = self.grid_vegetacao == 2

        self.queimadas_veg_baixa = np.sum(mask_queimada & veg_baixa)
        self.queimadas_veg_media = np.sum(mask_queimada & veg_media)
        self.queimadas_veg_alta = np.sum(mask_queimada & veg_alta)

        # vegetação baixa
        self.exposicao_veg_baixa = 0.02
        mask_exp_default_baixa = self.grid_carac_veg_baixa[:, :, 0] == -1
        mask_tempo_default_baixa = self.grid_carac_veg_baixa[:, :, 1] == -1

        grid_exp_baixa = self.grid_carac_veg_baixa[:, :, 0]
        grid_tempo_baixa = self.grid_carac_veg_baixa[:, :, 1]
            
        grid_exp_baixa = np.where(mask_suscetivel & veg_baixa & mask_exp_default_baixa, 0,grid_exp_baixa) # inicializa exposição acumulada    
        grid_tempo_baixa = np.where(mask_inflamada & veg_baixa & mask_tempo_default_baixa,self.grid_t_det_veg_baixa, grid_tempo_baixa) # inicializa tempo de deterioraçãoquando inflamada

        self.grid_carac_veg_baixa[:, :, 0] = grid_exp_baixa
        self.grid_carac_veg_baixa[:, :, 1] = grid_tempo_baixa

        # vegetação média
        self.exposicao_veg_media = 0.04
        mask_exp_default_media = self.grid_carac_veg_media[:, :, 0] == -1
        mask_tempo_default_media = self.grid_carac_veg_media[:, :, 1] == -1

        grid_exp_media = self.grid_carac_veg_media[:, :, 0]
        grid_tempo_media = self.grid_carac_veg_media[:, :, 1]

        grid_exp_media = np.where(mask_suscetivel & veg_media & mask_exp_default_media, 0,grid_exp_media)
        grid_tempo_media = np.where(mask_inflamada & veg_media & mask_tempo_default_media,self.grid_t_det_veg_media, grid_tempo_media)

        self.grid_carac_veg_media[:, :, 0] = grid_exp_media
        self.grid_carac_veg_media[:, :, 1] = grid_tempo_media

        # vegeração alta
        self.exposicao_veg_alta = 0.06
        mask_exp_default_alta = self.grid_carac_veg_alta[:, :, 0] == -1
        mask_tempo_default_alta = self.grid_carac_veg_alta[:, :, 1] == -1

        grid_exp_alta = self.grid_carac_veg_alta[:, :, 0]
        grid_tempo_alta = self.grid_carac_veg_alta[:, :, 1]

        grid_exp_alta = np.where(mask_suscetivel & veg_alta & mask_exp_default_alta, 0,grid_exp_alta)
        grid_tempo_alta = np.where(mask_inflamada & veg_alta & mask_tempo_default_alta, self.grid_t_det_veg_alta, grid_tempo_alta)

        self.grid_carac_veg_alta[:, :, 0] = grid_exp_alta
        self.grid_carac_veg_alta[:, :, 1] = grid_tempo_alta

    def runnable(self, sus_color, inflam_color, queim_color, veg_colors, surface, pause):
        for x in range(self.columns):
            for y in range(self.rows):
                y_pos = self.padding + y * (self.scale + 1)
                x_pos = self.padding + x * (self.scale + 1)

                veg_type = self.grid_vegetacao[x][y]
                base_color = veg_colors[veg_type]

                if self.grid_array[x][y] == 0: # Suscetível
                    color = base_color
                elif self.grid_array[x][y] == 1: # Inflamada
                    color = inflam_color
                else: # Queimada
                    color = queim_color

                pygame.draw.rect(surface, color, [x_pos, y_pos, self.scale, self.scale])

        nextc = np.ndarray(shape=self.size, dtype=int)

        if not pause:
            sleep(self.timing / 60)
            self.geracao += 1

            for x in range(self.columns):
                for y in range(self.rows):
                    nextc[x, y] = self.rules(x, y, self.vel_vento, self.dir_vento)

            self.grid_array = nextc
        self.check()

    def rules(self, x, y, vel_vento, dir_vento): # função que implementa as regras do jogo
        cel_state = self.grid_array[x, y]
        cel_type = self.grid_vegetacao[x, y]
        var_auxiliar = cel_state

        colunas = self.columns
        linhas = self.rows

        if cel_state == 0: # se suscetivel
            alcance = 1 if vel_vento == 1 else 2 # variável auxiliar para determinar a vizinhança
            if cel_type == 0: # vegetação baixa
                matriz_preferencia = self.matrizes_pref_veg_baixa[(vel_vento, dir_vento)]
                exposicao_acumulada = self.grid_carac_veg_baixa[x, y, 0]
                soma_prob = 0

                for i in range(-alcance, alcance + 1):
                    for j in range(-alcance, alcance + 1):
                        if i == 0 and j == 0: 
                            continue

                        xi, yj = x + i, y + j

                        if 0 <= xi < colunas and 0 <= yj < linhas:
                            if self.grid_array[xi, yj] == 1:
                                prob_vizinho = matriz_preferencia[j + alcance][i + alcance]
                                soma_prob += prob_vizinho
                if soma_prob < 0.01:  # ou 0.005
                    prob_inflamar = 0
                else:
                    prob_inflamar = min(1, soma_prob + exposicao_acumulada)
                if np.random.rand() <= prob_inflamar:
                    var_auxiliar = 1
                else:
                    nova_exposicao = min(0.08, exposicao_acumulada + self.exposicao_veg_baixa)
                    self.grid_carac_veg_baixa[x, y, 0] = nova_exposicao
            
            elif cel_type == 1: # vegetação media
                matriz_preferencia = self.matrizes_pref_veg_media[(vel_vento, dir_vento)]
                exposicao_acumulada = self.grid_carac_veg_media[x, y, 0]
                soma_prob = 0

                for i in range(-alcance, alcance + 1):
                    for j in range(-alcance, alcance + 1):
                        if i == 0 and j == 0:
                            continue

                        xi, yj = x + i, y + j

                        if 0 <= xi < colunas and 0 <= yj < linhas:
                            if self.grid_array[xi, yj] == 1:
                                prob_vizinho = matriz_preferencia[j + alcance][i + alcance]
                                soma_prob += prob_vizinho
                if soma_prob < 0.01:  # ou 0.005
                    prob_inflamar = 0
                else:
                    prob_inflamar = min(1, soma_prob + exposicao_acumulada)
                if np.random.rand() <= prob_inflamar:
                    var_auxiliar = 1
                else:
                    nova_exposicao = min(0.11, exposicao_acumulada + self.exposicao_veg_media)
                    self.grid_carac_veg_media[x, y, 0] = nova_exposicao
            
            elif cel_type == 2: # vegetação alta
                matriz_preferencia = self.matrizes_pref_veg_alta[(vel_vento, dir_vento)]
                exposicao_acumulada = self.grid_carac_veg_alta[x, y, 0]
                soma_prob = 0

                for i in range(-alcance, alcance + 1):
                    for j in range(-alcance, alcance + 1):
                        if i == 0 and j == 0:
                            continue

                        xi, yj = x + i, y + j

                        if 0 <= xi < colunas and 0 <= yj < linhas:
                            if self.grid_array[xi, yj] == 1:
                                prob_vizinho = matriz_preferencia[j + alcance][i + alcance]
                                soma_prob += prob_vizinho
                if soma_prob < 0.01:  # ou 0.005
                    prob_inflamar = 0
                else:
                    prob_inflamar = min(1, soma_prob + exposicao_acumulada)
                if np.random.rand() <= prob_inflamar:
                    var_auxiliar = 1
                else:
                    nova_exposicao = min(0.14, exposicao_acumulada + self.exposicao_veg_alta)
                    self.grid_carac_veg_alta[x, y, 0] = nova_exposicao
        
        if cel_state == 1: # se inflamada
            if cel_type == 0: # vegetação baixa
                tempo_recuperacao = self.grid_carac_veg_baixa[x, y, 1]

                if tempo_recuperacao == 0:
                    var_auxiliar = 2
                    self.grid_carac_veg_baixa[x, y, :] = [-1, -1]
                else:
                    self.grid_carac_veg_baixa[x, y, 1] -= 1
            
            elif cel_type == 1: # vegetação média 
                tempo_recuperacao = self.grid_carac_veg_media[x, y, 1]

                if tempo_recuperacao == 0:
                    var_auxiliar = 2
                    self.grid_carac_veg_media[x, y, :] = [-1, -1]
                else:
                    self.grid_carac_veg_media[x, y, 1] -= 1
            
            elif cel_type == 2: # vegetação alta
                tempo_recuperacao = self.grid_carac_veg_alta[x, y, 1]

                if tempo_recuperacao == 0:
                    var_auxiliar = 2
                    self.grid_carac_veg_alta[x, y, :] = [-1, -1]
                else:
                    self.grid_carac_veg_alta[x, y, 1] -= 1

        return var_auxiliar

    def clear(self):
        self.grid_array = np.zeros(shape=self.size, dtype=int)
        self.check()
        self.geracao = 1

        self.s_series = []
        self.i_series = []
        self.r_series = []
        self.t_series = []

        self.grid_carac_veg_baixa.fill(-1)
        self.grid_carac_veg_baixa[:, :, 0] = 0
        self.grid_carac_veg_media.fill(-1)
        self.grid_carac_veg_media[:, :, 0] = 0
        self.grid_carac_veg_alta.fill(-1)
        self.grid_carac_veg_alta[:, :, 0] = 0

    def random_grid(self, distribution_type=0):
        self.clear()
        if distribution_type == 0: # distribuição realista
            self.grid_vegetacao = np.random.choice([0, 1, 2], size=self.size, p=[0.4, 0.35, 0.25])
        elif distribution_type == 1: # distribuição de risco
            self.grid_vegetacao = np.random.choice([0, 1, 2], size=self.size, p=[0.3, 0.4, 0.3])
        elif distribution_type == 2: # distribuição didática
            self.grid_vegetacao = np.random.choice([0, 1, 2], size=self.size, p=[1/3, 1/3, 1/3])
        self.check()

    def handle_mouse(self, x, y, status=1):
        _x = (x - self.padding) // (self.scale + 1)
        _y = (y - self.padding) // (self.scale + 1)

        if 0 <= _x < self.columns and 0 <= _y < self.rows:
            self.grid_array[_x][_y] = status

        self.check()

    def set_wind_direction(self, direction):
        self.dir_vento = direction

    def set_wind_speed(self, speed):
        self.vel_vento = speed

    def set_initial_fire(self, x, y):
        if 0 <= x < self.columns and 0 <= y < self.rows:
            self.grid_array[x, y] = 1 # Define a célula como inflamada
            self.check()

    def set_vegetation_type(self, x, y, veg_type):
        if 0 <= x < self.columns and 0 <= y < self.rows:
            self.grid_vegetacao[x, y] = veg_type
            self.check()

    def standard(self, tipo):
        self.clear()
        if tipo == 1: # ponto no centro
            _x = self.columns // 2
            _y = self.rows // 2
            self.grid_array[_x, _y] = 1
        elif tipo == 2: # dois pontos equidistantes no centro
            _x = self.columns // 3
            _y = self.rows // 2
            self.grid_array[_x, _y] = 1
            self.grid_array[_x * 2, _y] = 1
        elif tipo == 3: # três pontos equidistantes no centro
            _x = self.columns // 4
            _y = self.rows // 2
            self.grid_array[_x, _y] = 1
            self.grid_array[_x * 2, _y] = 1
            self.grid_array[_x * 3, _y] = 1
        elif tipo == 4: # um ponto no centro de cada quadrante
            _x = self.columns // 4
            _y = self.rows // 4
            for i in range(1, 4, 2):
                for j in range(1, 4, 2):
                    x_ = i * _x
                    y_ = j * _y
                    self.grid_array[x_, y_] = 1
        elif tipo == 5: # linha vertical
            _y = self.rows // 2
            self.grid_array[:, _y] = 1
        elif tipo == 6: # linha horizontal
            _x = self.columns // 2
            self.grid_array[_x, :] = 1