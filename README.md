# Vantage

> Behind every great campaign is a Master who sees the whole board.

Vantage é um aplicativo desktop para **Mestres de RPG** — centraliza rolagem de dados, fichas de personagens, mapas e anotações de lore em uma única tela.

---

## Pré-requisitos

- [Python 3.12+](https://www.python.org/downloads/) instalado e no PATH

---

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/Vantage.git
cd Vantage

# 2. Crie o ambiente virtual
py -m venv .venv

# 3. Ative o ambiente virtual
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (CMD)
.venv\Scripts\activate.bat
# Linux / macOS
source .venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt
```

---

## Rodando o projeto

Com o `.venv` ativo:

```bash
py main.py
```

Ou diretamente, sem ativar o venv:

```bash
.venv\Scripts\python main.py       # Windows
.venv/bin/python main.py           # Linux / macOS
```

---

## Gerando o executável (.exe)

```bash
pyinstaller vantage.spec
```

O executável final estará em `dist/Vantage.exe`.

> **Nota:** para incluir um ícone, adicione um arquivo `src/assets/icon.ico` e descomente a linha `icon=` no `vantage.spec`.

---

## Estrutura do projeto

```
Vantage/
├── main.py                        # Ponto de entrada
├── requirements.txt               # Dependências Python
├── vantage.spec                   # Configuração do PyInstaller
│
└── src/
    ├── core/
    │   ├── dice.py                # Lógica de rolagem de dados
    │   ├── character.py           # Modelo de personagem + gerador de NPC
    │   ├── map_data.py            # Modelo de mapa 2D e tokens
    │   ├── lore.py                # Modelo de anotações de lore
    │   └── storage.py             # Persistência JSON (%APPDATA%/Vantage)
    │
    ├── ui/
    │   ├── main_window.py         # Janela principal e navegação
    │   ├── titlebar.py            # Barra de título customizada (drag)
    │   ├── sidebar.py             # Menu lateral
    │   └── pages/
    │       ├── dice_roller.py     # Rolagem de dados
    │       ├── characters.py      # Gestão de personagens
    │       ├── map_editor.py      # Editor de mapas 2D
    │       └── lore.py            # Canto do Lore
    │
    └── assets/
        └── style.qss              # Tema visual (dark + dourado)
```

---

## Funcionalidades

| Funcionalidade       | Status        |
|----------------------|---------------|
| 🎲 Rolagem de Dados  | ✅ Disponível  |
| 🧙 Personagens       | ✅ Disponível  |
| 🗺️ Mapas 2D          | ✅ Disponível  |
| 📖 Canto do Lore     | ✅ Disponível  |

### 🎲 Rolagem de Dados

- Dados: **d4, d6, d8, d10, d12, d20, d100**
- Selecione o dado → configure quantidade e modificador → clique em **Rolar**
- Histórico de rolagens em tempo real

### 🧙 Personagens

- Criação de fichas com atributos (FOR, DES, CON, INT, SAB, CAR), perícias e anotações
- **Gerador automático de NPC** — nome, raça, classe, stats e perícias aleatórias
- Cálculo automático de modificadores
- Ficha completa com HP, CA, nível e 18 perícias

### 🗺️ Mapas 2D

- Editor grid-based com 10 tipos de terreno (grama, água, floresta, pedra, areia, lava, etc.)
- Ferramentas: **Pintar**, **Apagar**, **Token**
- Tokens coloridos para representar personagens no mapa
- Pan (botão do meio) e Zoom (scroll) para navegar o mapa
- Criação de múltiplos mapas com salvamento

### 📖 Canto do Lore

- Anotações organizadas por categoria: Locais, NPCs, Eventos, Itens, Facções, Notas
- Editor de texto para cada entrada
- Busca e filtro por categoria

---

## Dados persistentes

Todos os dados (personagens, mapas, lore) são salvos automaticamente em:

- **Windows:** `%APPDATA%\Vantage\`
- **Linux/macOS:** `~/.local/share/Vantage/`

---

## Tech Stack

- **[PyQt6](https://pypi.org/project/PyQt6/)** — interface gráfica
- **[PyInstaller](https://pyinstaller.org/)** — empacotamento como `.exe`
