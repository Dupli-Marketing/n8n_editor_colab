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
