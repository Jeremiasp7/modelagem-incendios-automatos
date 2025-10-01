Modelagem de incêndios em florestas heterogêneas utilizando autômatos celulares 
    - Este projeto apresenta uma modelagem utilizando autômatos celulares para a simulação de incêndios em florestas heterogêneas, considerando diferentes tipos de vegetação velocidades e direções do vento. O objetivo é estudar o comportamento do fogo sob diversas circunstâncias ambientais.

Estrutura do projeto:
    - sfb.py: implementação da lógica de propagação do fogo.
    - auxiliar.py: funções auxiliares para salvar os resultados das simulações.
    - main.py: script principal para a execução automática das simulações.
    - projeto.py: implementação da lógica do pygame
    - resultados/: pasta em que serão salvos os resultados finais de cada simulação.
    - resultados_series/: pasta em que serão salvas as séries temporais de cada simulação.
    - resultados_analise/: pasta com notebooks com as análises de cada cenário
*Ao rodar o projeto, o usuário será direcionado para o menu com a visualização da simulação do grid
    
Como Rodar:
    1. Clone o repositório:
        git clone https://github.com/seu_usuario/seu_repositorio.git
        cd seu_repositorio
    2. Instale as dependências:
        pip install - r requirements.txt
    3. Execute o programa:
        python main.py
    