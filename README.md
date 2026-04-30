# N8N Workflow DAG Editor - Setup & Usage Guide

## 🎯 Overview

Um **editor visual de workflows tipo n8n** construído do zero com Python, projetado especificamente para **Google Colab**, sem precisar de interfaces gráficas complexas.

### ✨ Recursos

- ✅ **DAG Engine**: Gerenciamento de grafos direcionados acíclicos
- ✅ **Node-based Editor**: Criar nós e conexões programaticamente
- ✅ **Drag-and-Drop Simulation**: Interface que simula arrastar nós
- ✅ **Validation**: Detectar ciclos automaticamente
- ✅ **Execution**: Executar workflows com logging
- ✅ **Visualization**: Gráficos interativos com Plotly
- ✅ **Export/Import**: JSON serialization para workflows
- ✅ **Colab-friendly**: Sem dependências pesadas de GUI

---

## 🚀 Quick Start

### 1. Instalação (Google Colab)

```python
!pip install dash plotly cytoscape networkx pydantic -q

```
### 2. Criar um Workflow

```
from n8n_editor_colab import (
    WorkflowDAGEngine, NodeData, EdgeData, NodeType,
    create_example_workflow
)

# Usar exemplo pronto
engine = create_example_workflow()

# Ou criar do zero
engine = WorkflowDAGEngine()

# Adicionar nó
start_node = NodeData(
    id="node_1",
    name="START",
    type=NodeType.START,
    position=(0, 0)
)
engine.add_node(start_node)

# Adicionar conexão
action_node = NodeData(
    id="node_2",
    name="My Action",
    type=NodeType.ACTION,
    position=(200, 0)
)
engine.add_node(action_node)

edge = EdgeData(
    id="edge_1",
    source="node_1",
    target="node_2",
    label="execute"
)
engine.add_edge(edge)

```
### 3. Validar e Executar
```

from n8n_editor_colab import WorkflowExecutor, WorkflowVisualizer

# Validar DAG
is_valid, msg = engine.is_valid_dag()
print(f"✅ {msg}")

# Visualizar
fig = WorkflowVisualizer.visualize(engine)
fig.show()

# Executar
executor = WorkflowExecutor(engine)
success, msg = executor.execute({"data": "input"})
print(executor.get_log())

```
# 📚 Arquivos

## 1. n8n_editor_colab.py (Core Engine)

#### Classes principais:

Classe	Responsabilidade
WorkflowDAGEngine	Gerenciar grafo DAG, nós e arestas
NodeData	Dataclass para nó (id, nome, tipo, posição, config)
EdgeData	Dataclass para conexão (source, target, label)
WorkflowVisualizer	Renderizar com Plotly
WorkflowExecutor	Executar workflow com logging
WorkflowSerializer	Exportar/importar JSON


#### Métodos principais:
```
# Gerenciamento de nós
engine.add_node(node: NodeData) -> bool
engine.remove_node(node_id: str) -> bool

# Gerenciamento de arestas
engine.add_edge(edge: EdgeData) -> bool
engine.remove_edge(edge_id: str) -> bool

# Validação
engine.is_valid_dag() -> Tuple[bool, str]
engine.detect_cycles() -> List[List[str]]
engine.get_execution_order() -> List[str]

# Análise
engine.get_node_dependencies(node_id: str) -> List[str]
engine.get_node_dependents(node_id: str) -> List[str]

```
## 2. colab_dashboard.py (Web UI com Dash)

#### Interface Dash com:

📝 Painel de criação de nós
🔗 Painel de conexão entre nós
📊 Gráfico interativo em tempo real
✅ Validação contínua de DAG
🚀 Botão para executar workflow
📋 Log de execução em tempo real
📤/📥 Exportar/Importar JSON
📱 Design responsivo

#### Executar:
```
python colab_dashboard.py
# Acesse: http://localhost:8050
```
## 3. N8N_Workflow_Editor_Colab.ipynb (Notebook Tutorial)

#### 10 células pré-configuradas:

⚙️ Instalação de dependências
📦 Importar classes
🚀 Criar workflow de exemplo
📊 Validar e visualizar
🏃 Executar workflow
💾 Exportar/importar JSON
🔧 Adicionar nós dinamicamente
📈 Análise e estatísticas
🎨 Interface interativa com ipywidgets
🎓 Dicas e próximos passos

# 🎓 Exemplos de Uso

## Exemplo 1: Workflow Simples
```
engine = WorkflowDAGEngine()

# Criar pipeline: START → Action → END
nodes = [
    NodeData("n1", "START", NodeType.START, (0, 0)),
    NodeData("n2", "Process", NodeType.ACTION, (200, 0)),
    NodeData("n3", "END", NodeType.END, (400, 0)),
]

edges = [
    EdgeData("e1", "n1", "n2", "go"),
    EdgeData("e2", "n2", "n3", "done"),
]

for node in nodes:
    engine.add_node(node)

for edge in edges:
    engine.add_edge(edge)

# Executar
executor = WorkflowExecutor(engine)
success, msg = executor.execute()
```

## Exemplo 2: Workflow com Condição
```
# Adicionar nó de condição
condition = NodeData(
    "n_cond",
    "Check Status",
    NodeType.CONDITION,
    (300, 0),
    config={"condition": "status == 'success'"}
)

engine.add_node(condition)

# Duas saídas possíveis
success_edge = EdgeData("e_success", "n_cond", "n_success", "true")
error_edge = EdgeData("e_error", "n_cond", "n_retry", "false")

engine.add_edge(success_edge)
engine.add_edge(error_edge)
```

## Exemplo 3: Análise de Workflow
```
# Obter ordem de execução
order = engine.get_execution_order()
print("Execução:", " → ".join([engine.nodes[n].name for n in order]))

# Detectar ciclos
cycles = engine.detect_cycles()
if cycles:
    print("⚠️ Ciclos:", cycles)

# Dependências de um nó
deps = engine.get_node_dependencies("n2")
print("Depende de:", [engine.nodes[d].name for d in deps])

# Nós que dependem deste
dependents = engine.get_node_dependents("n2")
print("Afeta:", [engine.nodes[d].name for d in dependents])
```

## Exemplo 4: Exportar/Importar
```

from n8n_editor_colab import WorkflowSerializer

# Exportar
json_str = WorkflowSerializer.to_json(engine, "My Workflow")
print(json_str)

# Salvar arquivo
with open("workflow.json", "w") as f:
    f.write(json_str)

# Carregar em novo engine
new_engine = WorkflowDAGEngine()
success, msg = WorkflowSerializer.from_json(json_str, new_engine)
print(f"✅ {msg}")
```

# 📖 Tipos de Nós

Tipo	Cor	Uso
START	🟢 Verde	Início do workflow
END	🔴 Vermelho	Fim do workflow
ACTION	🔵 Azul	Executar ação (API, script, etc)
CONDITION	🟡 Amarelo	Tomada de decisão
LOOP	🟠 Laranja	Iteração/repetição
WEBHOOK	🟣 Roxo	Gatilho externo

# 🔄 Fluxo de Trabalho
```

┌─────────────────────────────────────────┐
│  1. CRIAR ENGINE                        │
│  engine = WorkflowDAGEngine()            │
└────────────────┬────────────────────────┘
                 │
┌─────────────────v────────────────────────┐
│  2. ADICIONAR NÓS                       │
│  engine.add_node(NodeData(...))         │
└────────────────┬────────────────────────┘
                 │
┌─────────────────v────────────────────────┐
│  3. CONECTAR NÓS                        │
│  engine.add_edge(EdgeData(...))         │
└────────────────┬────────────────────────┘
                 │
┌─────────────────v────────────────────────┐
│  4. VALIDAR DAG                         │
│  is_valid, msg = engine.is_valid_dag()  │
└────────────────┬────────────────────────┘
                 │
┌─────────────────v────────────────────────┐
│  5. VISUALIZAR                          │
│  fig = WorkflowVisualizer.visualize()   │
│  fig.show()                              │
└────────────────┬────────────────────────┘
                 │
┌─────────────────v────────────────────────┐
│  6. EXECUTAR                            │
│  executor = WorkflowExecutor(engine)    │
│  executor.execute(data)                  │
└────────────────┬────────────────────────┘
                 │
┌─────────────────v────────────────────────┐
│  7. EXPORTAR                            │
│  json_str = WorkflowSerializer.to_json()│
│  with open('workflow.json') as f: ...   │
└─────────────────────────────────────────┘
```

# 🛠️ Instalação no Google Colab

## Método 1: Uma célula (Rápido)
```
!pip install dash plotly cytoscape networkx pydantic -q

# Copiar arquivos
!wget https://raw.githubusercontent.com/seu-usuario/workflow-dag-editor/main/n8n_editor_colab.py
!wget https://raw.githubusercontent.com/seu-usuario/workflow-dag-editor/main/colab_dashboard.py

# Importar
from n8n_editor_colab import *
```

## Método 2: Notebook completo
Use o arquivo N8N_Workflow_Editor_Colab.ipynb diretamente no Colab.

# 🚀 Deploying a Web UI
Para usar a interface web colab_dashboard.py no Colab, execute:
```

# Em uma célula do Colab
!pip install dash plotly networkx pydantic -q

import subprocess
import time

# Iniciar servidor em background
process = subprocess.Popen(
    ["python", "colab_dashboard.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

time.sleep(3)
print("✅ Dashboard rodando!")
print("🌐 Acesse: http://localhost:8050")

# Ver output
import requests
response = requests.get("http://localhost:8050")
```

# 📊 Recursos Computacionais

Componente	Memória	CPU
Engine base	~1 MB	Mínimo
1000 nós	~10 MB	Mínimo
Plotly visualization	~20 MB	Baixo
Dash server	~50 MB	Baixo
Recomendação: Usar em ambiente Colab gratuito (suficiente)

# 🐛 Troubleshooting

## Erro: "ModuleNotFoundError: No module named 'dash'"
### Solução:
```

!pip install dash -q
```

## Erro: "Ciclos detectados"
### Solução: Verificar se há conexões circulares
```
cycles = engine.detect_cycles()
print(f"Ciclos: {cycles}")  # Remover essas conexões
```

## Workflow não executa
### Solução: Validar DAG
```

is_valid, msg = engine.is_valid_dag()
if not is_valid:
    print(f"❌ Problema: {msg}")
```

# 📚 Recursos Adicionais

NetworkX Docs: https://networkx.org/documentation/
Plotly Docs: https://plotly.com/python/
n8n Official: https://n8n.io
DAG Algorithms: https://en.wikipedia.org/wiki/Directed_acyclic_graph

# 📝 Próximas Features

 Editor visual drag-and-drop (ipycanvas)
 Suporte a webhooks reais
 Integração com APIs (HTTP, SQL, etc)
 Scheduler de execução
 Banco de dados para persistência
 Docker container
 Versioning de workflows
 Colaboração em tempo real

# 📄 Licença
MIT License - Sinta-se livre para usar, modificar e distribuir!

# 👨‍💻 Autor
GitHub Copilot - 2026-04-30

Para mais informações, visite: https://github.com/seu-usuario/workflow-dag-editor
