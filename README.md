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

2. Criar um Workflow

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

3. Validar e Executar

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


