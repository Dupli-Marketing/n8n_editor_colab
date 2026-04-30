"""
N8N Editor Dashboard para Google Colab
Interface completa com Dash + Cytoscape

Instalação no Colab:
!pip install dash plotly cytoscape networkx pydantic

Uso:
python colab_dashboard.py

Acesse: http://localhost:8050
"""

import json
import dash
from dash import dcc, html, callback, Input, Output, State, ctx
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from n8n_editor_colab import (
    WorkflowDAGEngine, NodeData, EdgeData, NodeType,
    CytoscapeRenderer, WorkflowExecutor, WorkflowSerializer,
    create_example_workflow
)


# ============================================================================
# INICIALIZAR APP
# ============================================================================

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "N8N Workflow Editor"

# Store para armazenar engine e state
engine = create_example_workflow()


# ============================================================================
# CSS CUSTOMIZADO
# ============================================================================

CUSTOM_CSS = """
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    background: #f5f5f5;
}

.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn {
    background: #667eea;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    margin-right: 10px;
    transition: background 0.3s;
}

.btn:hover {
    background: #5568d3;
}

.btn-danger {
    background: #e74c3c;
}

.btn-danger:hover {
    background: #c0392b;
}

.btn-success {
    background: #27ae60;
}

.btn-success:hover {
    background: #229954;
}

.section-title {
    font-size: 18px;
    font-weight: bold;
    color: #333;
    margin-bottom: 15px;
    border-bottom: 2px solid #667eea;
    padding-bottom: 10px;
}

.info-box {
    background: #e8f4f8;
    border-left: 4px solid #3498db;
    padding: 12px;
    margin-bottom: 10px;
    border-radius: 4px;
}

.error-box {
    background: #fadbd8;
    border-left: 4px solid #e74c3c;
    padding: 12px;
    margin-bottom: 10px;
    border-radius: 4px;
    color: #c0392b;
}

.success-box {
    background: #d5f4e6;
    border-left: 4px solid #27ae60;
    padding: 12px;
    margin-bottom: 10px;
    border-radius: 4px;
    color: #229954;
}

.log-box {
    background: #2c3e50;
    color: #ecf0f1;
    padding: 12px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    height: 300px;
    overflow-y: auto;
    white-space: pre-wrap;
}

.stat-box {
    background: white;
    border: 1px solid #ddd;
    padding: 15px;
    text-align: center;
    border-radius: 4px;
    margin-bottom: 10px;
}

.stat-number {
    font-size: 24px;
    font-weight: bold;
    color: #667eea;
}

.stat-label {
    font-size: 12px;
    color: #666;
    margin-top: 5px;
}
"""


# ============================================================================
# LAYOUT
# ============================================================================

app.layout = html.Div([
    # CSS
    html.Style(CUSTOM_CSS),
    
    # Stores
    dcc.Store(id='workflow-store', data={}),
    dcc.Store(id='selected-node-store', data=None),
    
    # Título
    html.Div([
        html.H1("🎨 N8N Workflow DAG Editor", style={"margin": "0"}),
        html.P("Construtor visual de workflows com validação de DAG", style={"margin": "5px 0 0 0", "opacity": "0.9"}),
    ], className="header"),
    
    # Container principal
    html.Div([
        # Esquerda - Controles
        html.Div([
            # ====== SEÇÃO: Nós ======
            html.Div([
                html.Div("🔧 Adicionar Nós", className="section-title"),
                
                html.Label("Nome do Nó:", style={"font-weight": "bold"}),
                dcc.Input(id="node-name-input", placeholder="Ex: Fetch Data", type="text", 
                         style={"width": "100%", "padding": "8px", "border": "1px solid #ddd", "border-radius": "4px"}),
                
                html.Label("Tipo:", style={"font-weight": "bold", "margin-top": "10px"}),
                dcc.Dropdown(
                    id="node-type-dropdown",
                    options=[
                        {"label": "🟢 START", "value": "start"},
                        {"label": "🔵 ACTION", "value": "action"},
                        {"label": "🟡 CONDITION", "value": "condition"},
                        {"label": "🟠 LOOP", "value": "loop"},
                        {"label": "🟣 WEBHOOK", "value": "webhook"},
                        {"label": "🔴 END", "value": "end"},
                    ],
                    value="action",
                    style={"width": "100%"}
                ),
                
                html.Button("➕ Adicionar Nó", id="add-node-btn", className="btn", 
                           style={"width": "100%", "margin-top": "10px"}),
                
                html.Div(id="node-feedback", style={"margin-top": "10px"}),
            ], className="card"),
            
            # ====== SEÇÃO: Arestas ======
            html.Div([
                html.Div("🔗 Conectar Nós", className="section-title"),
                
                html.Label("Nó Origem:", style={"font-weight": "bold"}),
                dcc.Dropdown(id="edge-source-dropdown", placeholder="Selecione...", 
                           style={"width": "100%"}),
                
                html.Label("Nó Destino:", style={"font-weight": "bold", "margin-top": "10px"}),
                dcc.Dropdown(id="edge-target-dropdown", placeholder="Selecione...", 
                           style={"width": "100%"}),
                
                html.Label("Rótulo (opcional):", style={"font-weight": "bold", "margin-top": "10px"}),
                dcc.Input(id="edge-label-input", placeholder="Ex: success, error", type="text",
                         style={"width": "100%", "padding": "8px", "border": "1px solid #ddd", "border-radius": "4px"}),
                
                html.Button("🔗 Conectar", id="add-edge-btn", className="btn",
                           style={"width": "100%", "margin-top": "10px"}),
                
                html.Div(id="edge-feedback", style={"margin-top": "10px"}),
            ], className="card"),
            
            # ====== SEÇÃO: Estatísticas ======
            html.Div([
                html.Div("📊 Estatísticas", className="section-title"),
                
                html.Div([
                    html.Div([
                        html.Div(id="stat-nodes", children="0", className="stat-number"),
                        html.Div("Nós", className="stat-label"),
                    ], className="stat-box"),
                    
                    html.Div([
                        html.Div(id="stat-edges", children="0", className="stat-number"),
                        html.Div("Conexões", className="stat-label"),
                    ], className="stat-box"),
                    
                    html.Div([
                        html.Div(id="stat-valid", children="✓", className="stat-number"),
                        html.Div("Status", className="stat-label"),
                    ], className="stat-box", style={"background": "#d5f4e6"}),
                ], style={"display": "grid", "grid-template-columns": "1fr 1fr", "gap": "10px"}),
                
            ], className="card"),
            
            # ====== SEÇÃO: Ações ======
            html.Div([
                html.Div("⚙️ Ações", className="section-title"),
                
                html.Button("🚀 Executar", id="execute-btn", className="btn btn-success",
                           style={"width": "100%"}),
                html.Button("📥 Importar JSON", id="import-btn", className="btn",
                           style={"width": "100%", "margin-top": "10px"}),
                html.Button("📤 Exportar JSON", id="export-btn", className="btn",
                           style={"width": "100%", "margin-top": "10px"}),
                html.Button("🗑️ Limpar Tudo", id="clear-btn", className="btn btn-danger",
                           style={"width": "100%", "margin-top": "10px"}),
            ], className="card"),
            
        ], style={"width": "23%", "display": "inline-block", "vertical-align": "top", "padding-right": "2%"}),
        
        # Meio - Visualização
        html.Div([
            html.Div([
                html.Div("🎯 Editor Visual", className="section-title"),
                dcc.Loading(
                    id="loading-graph",
                    type="default",
                    children=[
                        dcc.Graph(
                            id="workflow-graph",
                            style={"height": "600px", "border": "1px solid #ddd", "border-radius": "4px"},
                            config={"responsive": True, "displayModeBar": True}
                        ),
                    ]
                ),
                
                html.Div(id="graph-info", style={"margin-top": "10px", "font-size": "12px", "color": "#666"}),
            ], className="card"),
        ], style={"width": "48%", "display": "inline-block", "vertical-align": "top", "padding": "0 2%"}),
        
        # Direita - Logs e Info
        html.Div([
            # Info do nó selecionado
            html.Div([
                html.Div("ℹ️ Informações", className="section-title"),
                html.Div(id="node-info-box", children="Nenhum nó selecionado"),
            ], className="card"),
            
            # Validação
            html.Div([
                html.Div("✅ Validação DAG", className="section-title"),
                html.Div(id="dag-validation-box", children="Validando..."),
                html.Div(id="execution-order-box", children="", style={"margin-top": "10px", "font-size": "12px"}),
            ], className="card"),
            
            # Logs de execução
            html.Div([
                html.Div("📋 Log de Execução", className="section-title"),
                html.Pre(id="execution-log-box", children="Aguardando...", className="log-box"),
            ], className="card"),
            
        ], style={"width": "23%", "display": "inline-block", "vertical-align": "top", "padding-left": "2%"}),
        
    ], style={"display": "flex", "gap": "20px"}),
    
    # Modal para JSON
    html.Div(id="modal-container"),
    
], style={"padding": "20px", "max-width": "1600px", "margin": "0 auto"})


# ============================================================================
# CALLBACKS
# ============================================================================

@callback(
    Output("workflow-store", "data"),
    Input("workflow-store", "data"),
    prevent_initial_call=True
)
def init_store(data):
    """Inicializar store com workflow padrão"""
    if not data:
        return {
            "nodes": [
                {"id": n.id, "name": n.name, "type": n.type.value, "position": n.position}
                for n in engine.nodes.values()
            ],
            "edges": [
                {"id": e.id, "source": e.source, "target": e.target, "label": e.label}
                for e in engine.edges.values()
            ]
        }
    return data


@callback(
    [Output("node-feedback", "children"),
     Output("workflow-store", "data", allow_duplicate=True)],
    Input("add-node-btn", "n_clicks"),
    [State("node-name-input", "value"),
     State("node-type-dropdown", "value"),
     State("workflow-store", "data")],
    prevent_initial_call=True
)
def add_node(n_clicks, name, node_type, store_data):
    """Adicionar novo nó"""
    if not name or not node_type:
        return html.Div("❌ Nome e tipo são obrigatórios", className="error-box"), store_data
    
    try:
        node_id = f"node_{len(store_data.get('nodes', [])) + 1}"
        node = NodeData(
            id=node_id,
            name=name,
            type=NodeType(node_type),
            position=(len(store_data.get('nodes', [])) * 150, 0)
        )
        
        engine.add_node(node)
        
        store_data["nodes"].append({
            "id": node.id,
            "name": node.name,
            "type": node.type.value,
            "position": node.position
        })
        
        feedback = html.Div(f"✅ Nó '{name}' adicionado com sucesso!", className="success-box")
        return feedback, store_data
    
    except Exception as e:
        feedback = html.Div(f"❌ Erro: {str(e)}", className="error-box")
        return feedback, store_data


@callback(
    Output("edge-source-dropdown", "options"),
    Output("edge-target-dropdown", "options"),
    Input("workflow-store", "data")
)
def update_node_dropdowns(store_data):
    """Atualizar dropdowns de nós"""
    options = [{"label": node["name"], "value": node["id"]} 
               for node in store_data.get("nodes", [])]
    return options, options


@callback(
    [Output("edge-feedback", "children"),
     Output("workflow-store", "data", allow_duplicate=True)],
    Input("add-edge-btn", "n_clicks"),
    [State("edge-source-dropdown", "value"),
     State("edge-target-dropdown", "value"),
     State("edge-label-input", "value"),
     State("workflow-store", "data")],
    prevent_initial_call=True
)
def add_edge(n_clicks, source, target, label, store_data):
    """Adicionar aresta"""
    if not source or not target:
        return html.Div("❌ Selecione origem e destino", className="error-box"), store_data
    
    if source == target:
        return html.Div("❌ Origem e destino não podem ser iguais", className="error-box"), store_data
    
    try:
        edge_id = f"edge_{len(store_data.get('edges', [])) + 1}"
        edge = EdgeData(
            id=edge_id,
            source=source,
            target=target,
            label=label or ""
        )
        
        engine.add_edge(edge)
        
        store_data["edges"].append({
            "id": edge.id,
            "source": edge.source,
            "target": edge.target,
            "label": edge.label
        })
        
        feedback = html.Div(f"✅ Conexão criada com sucesso!", className="success-box")
        return feedback, store_data
    
    except Exception as e:
        feedback = html.Div(f"❌ Erro: {str(e)}", className="error-box")
        return feedback, store_data


@callback(
    [Output("workflow-graph", "figure"),
     Output("stat-nodes", "children"),
     Output("stat-edges", "children"),
     Output("stat-valid", "children")],
    Input("workflow-store", "data")
)
def update_graph(store_data):
    """Atualizar grafo visual"""
    num_nodes = len(engine.nodes)
    num_edges = len(engine.edges)
    is_valid, _ = engine.is_valid_dag()
    
    # Criar figura com plotly
    fig = go.Figure()
    
    # Adicionar arestas
    for edge in engine.edges.values():
        if edge.source in engine.nodes and edge.target in engine.nodes:
            source_node = engine.nodes[edge.source]
            target_node = engine.nodes[edge.target]
            
            fig.add_trace(go.Scatter(
                x=[source_node.position[0], target_node.position[0]],
                y=[source_node.position[1], target_node.position[1]],
                mode='lines',
                line=dict(color='#ccc', width=2),
                hoverinfo='text',
                text=edge.label or 'connection',
                showlegend=False
            ))
    
    # Adicionar nós
    node_colors = {
        NodeType.START: "#00ff00",
        NodeType.END: "#ff0000",
        NodeType.ACTION: "#0066ff",
        NodeType.CONDITION: "#ffcc00",
        NodeType.LOOP: "#ff6600",
        NodeType.WEBHOOK: "#9900ff",
    }
    
    for node in engine.nodes.values():
        fig.add_trace(go.Scatter(
            x=[node.position[0]],
            y=[node.position[1]],
            mode='markers+text',
            marker=dict(
                size=20,
                color=node_colors.get(node.type, "#0066ff"),
                symbol='circle'
            ),
            text=node.name,
            textposition="bottom center",
            hoverinfo='text',
            hovertext=f"{node.name} ({node.type.value})",
            showlegend=False
        ))
    
    fig.update_layout(
        title="Workflow DAG Visualization",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=True, zeroline=False),
        yaxis=dict(showgrid=True, zeroline=False),
        plot_bgcolor='#fafafa'
    )
    
    status = "✅ Válido" if is_valid else "⚠️ Inválido"
    
    return fig, str(num_nodes), str(num_edges), status


@callback(
    Output("dag-validation-box", "children"),
    Input("workflow-store", "data")
)
def update_validation(store_data):
    """Atualizar validação DAG"""
    is_valid, msg = engine.is_valid_dag()
    
    if is_valid:
        content = html.Div(f"✅ {msg}", className="success-box")
    else:
        content = html.Div(f"❌ {msg}", className="error-box")
    
    # Adicionar ordem de execução
    if is_valid:
        order = engine.get_execution_order()
        order_text = " → ".join([engine.nodes[n].name for n in order if n in engine.nodes])
        content = html.Div([
            content,
            html.Div(f"Execução: {order_text}", style={"margin-top": "10px", "font-size": "11px", "color": "#555"})
        ])
    
    return content


@callback(
    Output("execution-log-box", "children"),
    Input("execute-btn", "n_clicks"),
    prevent_initial_call=True
)
def execute_workflow(n_clicks):
    """Executar workflow"""
    executor = WorkflowExecutor(engine)
    success, msg = executor.execute({"data": "test_input"})
    
    log = executor.get_execution_log()
    return log


@callback(
    Output("modal-container", "children"),
    [Input("export-btn", "n_clicks"),
     Input("import-btn", "n_clicks")],
    prevent_initial_call=True
)
def handle_json_modal(export_clicks, import_clicks):
    """Lidar com modais de JSON"""
    
    if ctx.triggered_id == "export-btn":
        json_str = WorkflowSerializer.to_json(engine, "My Workflow")
        
        return html.Div([
            html.Div([
                html.H3("📤 Exportar Workflow"),
                html.Textarea(
                    value=json_str,
                    readOnly=True,
                    style={
                        "width": "100%",
                        "height": "400px",
                        "font-family": "monospace",
                        "padding": "10px",
                        "border": "1px solid #ddd",
                        "border-radius": "4px"
                    }
                ),
                html.Button("Copiar", id="copy-json-btn", className="btn", style={"margin-top": "10px"}),
                html.Button("Fechar", id="close-export-btn", className="btn", style={"margin-left": "10px"}),
            ], style={
                "position": "fixed",
                "top": "50%",
                "left": "50%",
                "transform": "translate(-50%, -50%)",
                "background": "white",
                "padding": "30px",
                "border-radius": "8px",
                "box-shadow": "0 4px 20px rgba(0,0,0,0.15)",
                "z-index": "1000",
                "width": "80%",
                "max-width": "600px"
            })
        ], style={
            "position": "fixed",
            "top": "0",
            "left": "0",
            "width": "100%",
            "height": "100%",
            "background": "rgba(0,0,0,0.5)",
            "z-index": "999"
        })
    
    raise PreventUpdate


@callback(
    Output("workflow-store", "data", allow_duplicate=True),
    Input("clear-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_workflow(n_clicks):
    """Limpar workflow"""
    engine.graph.clear()
    engine.nodes.clear()
    engine.edges.clear()
    
    return {"nodes": [], "edges": []}


# ============================================================================
# INICIAR SERVIDOR
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("N8N WORKFLOW DAG EDITOR - DASHBOARD")
    print("=" * 70)
    print("\n✅ Iniciando servidor...")
    print("🌐 Acesse: http://localhost:8050")
    print("\n" + "=" * 70 + "\n")
    
    app.run_server(debug=True, port=8050)
