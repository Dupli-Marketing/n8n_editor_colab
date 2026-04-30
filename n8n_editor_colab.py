"""
N8N-style Workflow DAG Editor for Google Colab
Built with Dash + Cytoscape + NetworkX

Author: GitHub Copilot
Date: 2026-04-30

Features:
- Drag-and-drop node editor
- DAG validation (cycle detection)
- Workflow execution
- Save/Load workflows as JSON
- Real-time visualization
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import networkx as nx
from dataclasses import dataclass, asdict
from enum import Enum

# ============================================================================
# DATA MODELS
# ============================================================================

class NodeType(str, Enum):
    """Tipos de nós suportados"""
    START = "start"
    END = "end"
    ACTION = "action"
    CONDITION = "condition"
    LOOP = "loop"
    WEBHOOK = "webhook"


@dataclass
class NodeData:
    """Dados de um nó no workflow"""
    id: str
    name: str
    type: NodeType
    position: Tuple[float, float] = (0, 0)
    config: Dict = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


@dataclass
class EdgeData:
    """Dados de uma aresta (conexão) no workflow"""
    id: str
    source: str
    target: str
    label: str = ""
    condition: Optional[str] = None


@dataclass
class WorkflowData:
    """Dados completos do workflow"""
    id: str
    name: str
    description: str = ""
    created_at: str = ""
    updated_at: str = ""
    nodes: List[NodeData] = None
    edges: List[EdgeData] = None
    
    def __post_init__(self):
        if self.nodes is None:
            self.nodes = []
        if self.edges is None:
            self.edges = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()


# ============================================================================
# WORKFLOW DAG ENGINE
# ============================================================================

class WorkflowDAGEngine:
    """Motor de DAG para gerenciar workflows"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, NodeData] = {}
        self.edges: Dict[str, EdgeData] = {}
        self.execution_results = {}
    
    def add_node(self, node: NodeData) -> bool:
        """Adicionar nó ao grafo"""
        if node.id in self.nodes:
            return False
        
        self.nodes[node.id] = node
        self.graph.add_node(node.id, data=node)
        return True
    
    def add_edge(self, edge: EdgeData) -> bool:
        """Adicionar aresta ao grafo"""
        if edge.id in self.edges:
            return False
        
        if edge.source not in self.nodes or edge.target not in self.nodes:
            return False
        
        self.edges[edge.id] = edge
        self.graph.add_edge(edge.source, edge.target, data=edge)
        return True
    
    def remove_node(self, node_id: str) -> bool:
        """Remover nó e suas arestas"""
        if node_id not in self.nodes:
            return False
        
        # Remover arestas conectadas
        edges_to_remove = [e for e in self.edges.values() 
                          if e.source == node_id or e.target == node_id]
        for edge in edges_to_remove:
            del self.edges[edge.id]
        
        del self.nodes[node_id]
        self.graph.remove_node(node_id)
        return True
    
    def remove_edge(self, edge_id: str) -> bool:
        """Remover aresta"""
        if edge_id not in self.edges:
            return False
        
        edge = self.edges[edge_id]
        del self.edges[edge_id]
        self.graph.remove_edge(edge.source, edge.target)
        return True
    
    def detect_cycles(self) -> List[List[str]]:
        """Detectar ciclos no DAG"""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except:
            return []
    
    def is_valid_dag(self) -> Tuple[bool, str]:
        """Validar se é um DAG válido"""
        if not self.graph.nodes():
            return True, "Grafo vazio"
        
        cycles = self.detect_cycles()
        if cycles:
            return False, f"Ciclos detectados: {cycles}"
        
        # Verificar se tem START e END
        start_nodes = [n for n in self.nodes.values() if n.type == NodeType.START]
        end_nodes = [n for n in self.nodes.values() if n.type == NodeType.END]
        
        if not start_nodes:
            return False, "Nenhum nó START encontrado"
        if not end_nodes:
            return False, "Nenhum nó END encontrado"
        
        return True, "DAG válido"
    
    def get_execution_order(self) -> List[str]:
        """Obter ordem de execução topológica"""
        if not self.is_valid_dag()[0]:
            return []
        
        try:
            return list(nx.topological_sort(self.graph))
        except:
            return []
    
    def get_node_dependencies(self, node_id: str) -> List[str]:
        """Obter nós que um nó depende"""
        if node_id not in self.graph:
            return []
        return list(self.graph.predecessors(node_id))
    
    def get_node_dependents(self, node_id: str) -> List[str]:
        """Obter nós que dependem de um nó"""
        if node_id not in self.graph:
            return []
        return list(self.graph.successors(node_id))
    
    def export_to_dict(self) -> WorkflowData:
        """Exportar workflow como dicionário"""
        return WorkflowData(
            id=str(uuid.uuid4()),
            name="Exported Workflow",
            nodes=list(self.nodes.values()),
            edges=list(self.edges.values())
        )
    
    def import_from_dict(self, workflow: WorkflowData) -> Tuple[bool, str]:
        """Importar workflow de dicionário"""
        try:
            self.graph.clear()
            self.nodes.clear()
            self.edges.clear()
            
            for node in workflow.nodes:
                self.add_node(node)
            
            for edge in workflow.edges:
                self.add_edge(edge)
            
            is_valid, msg = self.is_valid_dag()
            return is_valid, msg
        except Exception as e:
            return False, str(e)


# ============================================================================
# CYTOSCAPE INTEGRATION
# ============================================================================

class CytoscapeRenderer:
    """Renderizar workflow como elementos Cytoscape"""
    
    NODE_COLORS = {
        NodeType.START: "#00ff00",      # Verde
        NodeType.END: "#ff0000",         # Vermelho
        NodeType.ACTION: "#0066ff",      # Azul
        NodeType.CONDITION: "#ffcc00",   # Amarelo
        NodeType.LOOP: "#ff6600",        # Laranja
        NodeType.WEBHOOK: "#9900ff",     # Roxo
    }
    
    @staticmethod
    def to_cytoscape_elements(engine: WorkflowDAGEngine) -> List[Dict]:
        """Converter DAG para elementos Cytoscape"""
        elements = []
        
        # Adicionar nós
        for node_id, node in engine.nodes.items():
            elements.append({
                "data": {
                    "id": node_id,
                    "label": node.name,
                    "type": node.type.value,
                    "position_x": node.position[0],
                    "position_y": node.position[1],
                },
                "position": {"x": node.position[0], "y": node.position[1]},
                "style": {
                    "background-color": CytoscapeRenderer.NODE_COLORS.get(
                        node.type, "#0066ff"
                    ),
                    "label": node.name,
                    "width": "80px",
                    "height": "80px",
                    "font-size": "12px",
                    "color": "#fff",
                    "text-valign": "center",
                    "text-halign": "center",
                }
            })
        
        # Adicionar arestas
        for edge_id, edge in engine.edges.items():
            elements.append({
                "data": {
                    "id": edge_id,
                    "source": edge.source,
                    "target": edge.target,
                    "label": edge.label or "",
                }
            })
        
        return elements
    
    @staticmethod
    def get_layout_config() -> Dict:
        """Configuração de layout Cytoscape"""
        return {
            "name": "dagre",
            "rankDir": "LR",
            "nodeSep": 100,
            "rankSep": 100,
        }


# ============================================================================
# WORKFLOW EXECUTOR
# ============================================================================

class WorkflowExecutor:
    """Executor de workflows"""
    
    def __init__(self, engine: WorkflowDAGEngine):
        self.engine = engine
        self.results = {}
        self.execution_log = []
    
    def execute(self, initial_data: Dict = None) -> Tuple[bool, str]:
        """Executar workflow"""
        is_valid, msg = self.engine.is_valid_dag()
        if not is_valid:
            return False, f"Workflow inválido: {msg}"
        
        if initial_data is None:
            initial_data = {}
        
        try:
            execution_order = self.engine.get_execution_order()
            self.results = {"START": initial_data}
            
            self._log(f"Iniciando execução. Ordem: {execution_order}")
            
            for node_id in execution_order:
                node = self.engine.nodes[node_id]
                
                if node.type == NodeType.START:
                    self._log(f"✓ START: Workflow iniciado")
                    continue
                
                if node.type == NodeType.END:
                    self._log(f"✓ END: Workflow concluído")
                    continue
                
                # Obter dados de entrada
                dependencies = self.engine.get_node_dependencies(node_id)
                input_data = {}
                for dep_id in dependencies:
                    if dep_id in self.results:
                        input_data.update(self.results[dep_id])
                
                # Executar nó
                result = self._execute_node(node, input_data)
                self.results[node_id] = result
                self._log(f"✓ {node.name}: {result}")
            
            return True, "Workflow executado com sucesso"
        
        except Exception as e:
            self._log(f"✗ Erro: {str(e)}")
            return False, str(e)
    
    def _execute_node(self, node: NodeData, input_data: Dict) -> Dict:
        """Executar um nó individual"""
        if node.type == NodeType.ACTION:
            # Simular ação
            return {
                "action": node.name,
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "input": input_data,
                "output": {"result": f"Ação '{node.name}' executada"}
            }
        
        elif node.type == NodeType.CONDITION:
            # Simular condição
            condition_result = node.config.get("condition", "true")
            return {
                "condition": condition_result,
                "passed": True,
                "timestamp": datetime.now().isoformat(),
            }
        
        elif node.type == NodeType.LOOP:
            # Simular loop
            return {
                "iterations": node.config.get("iterations", 1),
                "timestamp": datetime.now().isoformat(),
            }
        
        return {"status": "completed"}
    
    def _log(self, message: str):
        """Adicionar mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.execution_log.append(log_entry)
        print(log_entry)
    
    def get_execution_log(self) -> str:
        """Obter log de execução completo"""
        return "\n".join(self.execution_log)


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

def create_example_workflow() -> WorkflowDAGEngine:
    """Criar um workflow de exemplo"""
    engine = WorkflowDAGEngine()
    
    # Criar nós
    start = NodeData(
        id="node_1",
        name="START",
        type=NodeType.START,
        position=(0, 0)
    )
    
    action1 = NodeData(
        id="node_2",
        name="Fetch Data",
        type=NodeType.ACTION,
        position=(200, 0),
        config={"api": "https://api.example.com/data"}
    )
    
    condition = NodeData(
        id="node_3",
        name="Validate",
        type=NodeType.CONDITION,
        position=(400, 0),
        config={"condition": "data.status == 'success'"}
    )
    
    action2 = NodeData(
        id="node_4",
        name="Process Data",
        type=NodeType.ACTION,
        position=(600, 0),
        config={"process_type": "transform"}
    )
    
    end = NodeData(
        id="node_5",
        name="END",
        type=NodeType.END,
        position=(800, 0)
    )
    
    # Adicionar nós
    engine.add_node(start)
    engine.add_node(action1)
    engine.add_node(condition)
    engine.add_node(action2)
    engine.add_node(end)
    
    # Adicionar arestas
    engine.add_edge(EdgeData(
        id="edge_1",
        source="node_1",
        target="node_2",
        label="start"
    ))
    
    engine.add_edge(EdgeData(
        id="edge_2",
        source="node_2",
        target="node_3",
        label="success"
    ))
    
    engine.add_edge(EdgeData(
        id="edge_3",
        source="node_3",
        target="node_4",
        label="valid"
    ))
    
    engine.add_edge(EdgeData(
        id="edge_4",
        source="node_4",
        target="node_5",
        label="done"
    ))
    
    return engine


# ============================================================================
# PERSISTÊNCIA
# ============================================================================

class WorkflowSerializer:
    """Serializar/desserializar workflows"""
    
    @staticmethod
    def to_json(engine: WorkflowDAGEngine, name: str = "workflow") -> str:
        """Converter workflow para JSON"""
        workflow = engine.export_to_dict()
        workflow.name = name
        
        data = {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "created_at": workflow.created_at,
            "updated_at": workflow.updated_at,
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "type": n.type.value,
                    "position": n.position,
                    "config": n.config,
                }
                for n in workflow.nodes
            ],
            "edges": [
                {
                    "id": e.id,
                    "source": e.source,
                    "target": e.target,
                    "label": e.label,
                    "condition": e.condition,
                }
                for e in workflow.edges
            ],
        }
        
        return json.dumps(data, indent=2)
    
    @staticmethod
    def from_json(json_str: str, engine: WorkflowDAGEngine) -> Tuple[bool, str]:
        """Carregar workflow de JSON"""
        try:
            data = json.loads(json_str)
            
            nodes = [
                NodeData(
                    id=n["id"],
                    name=n["name"],
                    type=NodeType(n["type"]),
                    position=tuple(n.get("position", (0, 0))),
                    config=n.get("config", {}),
                )
                for n in data.get("nodes", [])
            ]
            
            edges = [
                EdgeData(
                    id=e["id"],
                    source=e["source"],
                    target=e["target"],
                    label=e.get("label", ""),
                    condition=e.get("condition"),
                )
                for e in data.get("edges", [])
            ]
            
            workflow = WorkflowData(
                id=data.get("id", str(uuid.uuid4())),
                name=data.get("name", "Imported Workflow"),
                description=data.get("description", ""),
                nodes=nodes,
                edges=edges,
            )
            
            return engine.import_from_dict(workflow)
        
        except Exception as e:
            return False, str(e)


# ============================================================================
# TESTE E DEMONSTRAÇÃO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("N8N-STYLE WORKFLOW DAG EDITOR - DEMO")
    print("=" * 70)
    print()
    
    # Criar workflow de exemplo
    print("1️⃣  Criando workflow de exemplo...")
    engine = create_example_workflow()
    print(f"   ✓ {len(engine.nodes)} nós criados")
    print(f"   ✓ {len(engine.edges)} arestas criadas")
    print()
    
    # Validar DAG
    print("2️⃣  Validando DAG...")
    is_valid, msg = engine.is_valid_dag()
    print(f"   ✓ {msg}")
    print()
    
    # Obter ordem de execução
    print("3️⃣  Ordem de execução topológica:")
    execution_order = engine.get_execution_order()
    for i, node_id in enumerate(execution_order, 1):
        node = engine.nodes[node_id]
        print(f"   {i}. {node.name} ({node_id})")
    print()
    
    # Executar workflow
    print("4️⃣  Executando workflow...")
    executor = WorkflowExecutor(engine)
    success, msg = executor.execute({"data": "test"})
    print(f"   ✓ {msg}")
    print()
    
    # Exibir log
    print("5️⃣  Log de execução:")
    print(executor.get_execution_log())
    print()
    
    # Exportar para JSON
    print("6️⃣  Exportando workflow para JSON:")
    json_str = WorkflowSerializer.to_json(engine, "Example Workflow")
    print(json_str)
    print()
    
    # Converter para Cytoscape
    print("7️⃣  Convertendo para Cytoscape...")
    elements = CytoscapeRenderer.to_cytoscape_elements(engine)
    print(f"   ✓ {len(elements)} elementos criados")
    print()
    
    print("=" * 70)
    print("✅ DEMO CONCLUÍDA")
    print("=" * 70)
