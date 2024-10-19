import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
import random
import json
import os
from streamlit.runtime.state import SessionState

st.set_page_config(page_title="Power BI Model Simulator - Streamlit Flow", layout="wide")



# with st.echo('below'):
import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout
import random
from uuid import uuid4

def create_node_from_schema(table_name, columns, position):
    content = f"**{table_name}**"
    return StreamlitFlowNode(
        str(f"st-flow-node_{uuid4()}"),
        position,
        {
            'content': content,
            'columns': columns,
            'id': str(f"st-flow-node_{uuid4()}")
        },
        'default',
        'right',
        'left',
        deletable=True  # Add this line to make all nodes deletable
    )

def validate_json_structure(json_data):
    with open('example_json_structure.json', 'r') as f:
        example_structure = json.load(f)
    
    if not isinstance(json_data, dict):
        return False
    
    # Check for required top-level keys
    if set(json_data.keys()) != set(example_structure.keys()):
        return False
    
    # Validate tables
    if not isinstance(json_data.get('tables'), list):
        return False
    
    for table in json_data['tables']:
        if not isinstance(table, dict) or set(table.keys()) != {'table_name', 'columns'}:
            return False
        if not isinstance(table['columns'], list):
            return False
        for column in table['columns']:
            if not isinstance(column, dict) or not set(column.keys()).issubset({'column_name', 'type', 'isPrimaryKey', 'isForeignKey', 'references', 'calculatedColumn', 'formula'}):
                return False
    
    # Validate relationships
    if not isinstance(json_data.get('relationships'), list):
        return False
    
    for relationship in json_data['relationships']:
        if not isinstance(relationship, dict) or set(relationship.keys()) != {'from_table', 'from_column', 'to_table', 'to_column', 'relationship_type'}:
            return False
    
    return True

def get_edge_style(relationship_type):
    if relationship_type == 'OneToOne':
        return {'label': '1:1', 'markerEnd': {'type': 'arrow'}, 'markerStart': {'type': 'arrow'}}
    elif relationship_type == 'OneToMany':
        return {'label': '1:N', 'markerEnd': {'type': 'arrowclosed'}}
    elif relationship_type == 'ManyToOne':
        return {'label': 'N:1', 'markerStart': {'type': 'arrowclosed'}}
    elif relationship_type == 'ManyToMany':
        return {'label': 'N:N', 'markerEnd': {'type': 'arrowclosed'}, 'markerStart': {'type': 'arrowclosed'}}
    else:
        return {}

if 'curr_state' not in st.session_state:
    nodes = [StreamlitFlowNode("1", (0, 0), {'content': 'Node 1'}, 'input', 'right'),
            StreamlitFlowNode("2", (1, 0), {'content': 'Node 2'}, 'default', 'right', 'left'),
            StreamlitFlowNode("3", (2, 0), {'content': 'Node 3'}, 'default', 'right', 'left'),
            ]

    edges = [StreamlitFlowEdge("1-2", "1", "2", animated=True),
            StreamlitFlowEdge("1-3", "1", "3", animated=True),
            ]
    
    st.session_state.curr_state = StreamlitFlowState(nodes, edges)

if 'validation_result' not in st.session_state:
    st.session_state.validation_result = None

if 'validated_schema' not in st.session_state:
    st.session_state.validated_schema = None

with st.sidebar:
    st.title("Power BI Model Simulator")
    
    st.markdown("""
    A visual tool for designing and simulating Power BI data models.

    **Instructions:**
    1. Paste your JSON schema in the text area below.
    2. Click "Validate JSON" to check if your schema is valid.
    3. If valid, click "Import Structure to Canvas" to visualize your model.
    4. Use the canvas to further manipulate and explore your data model.

    Need an example? Click the "Example JSON" button to see the expected format.
    """)
    
    schema_json = st.text_area("Paste JSON Schema", height=300)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.popover("Example JSON"):
            with open('example_json_structure.json', 'r') as f:
                example_json = f.read()
            st.code(example_json, language="json")
    
    with col2:
        if st.button("Validate JSON"):
            try:
                schema = json.loads(schema_json)
                if validate_json_structure(schema):
                    st.session_state.validation_result = "success"
                    st.session_state.validated_schema = schema
                else:
                    st.session_state.validation_result = "error"
                    st.session_state.validated_schema = None
            except json.JSONDecodeError:
                st.session_state.validation_result = "error"
                st.session_state.validated_schema = None
            st.rerun()

    if st.session_state.validation_result == "success":
        st.success("Valid JSON structure!")
        if st.button("Import Structure to Canvas"):
            for table in st.session_state.validated_schema["tables"]:
                new_node = create_node_from_schema(table["table_name"], table["columns"], (len(st.session_state.curr_state.nodes) * 200, 0))
                st.session_state.curr_state.nodes.append(new_node)
            
            # Create edges for relationships
            for relationship in st.session_state.validated_schema["relationships"]:
                from_node = next((node for node in st.session_state.curr_state.nodes if node.data['content'] == f"**{relationship['from_table']}**"), None)
                to_node = next((node for node in st.session_state.curr_state.nodes if node.data['content'] == f"**{relationship['to_table']}**"), None)
                
                if from_node and to_node:
                    edge_style = get_edge_style(relationship['relationship_type'])
                    edge = StreamlitFlowEdge(
                        id=f"edge_{uuid4()}",
                        source=from_node.id,
                        target=to_node.id,
                        source_handle=f"{from_node.id}-{relationship['from_column']}-source",
                        target_handle=f"{to_node.id}-{relationship['to_column']}-target",
                        data={
                            'label': edge_style.get('label', relationship['relationship_type']),
                            'relationship_type': relationship['relationship_type'],
                            'from_table': relationship['from_table'],
                            'from_column': relationship['from_column'],
                            'to_table': relationship['to_table'],
                            'to_column': relationship['to_column']
                        },
                        animated=False,
                        **edge_style
                    )
                    st.session_state.curr_state.edges.append(edge)
            
            st.success("Schema added to canvas successfully!")
            st.session_state.validation_result = None
            st.session_state.validated_schema = None
            st.rerun()
    elif st.session_state.validation_result == "error":
        st.error("Invalid JSON structure. Please check and follow the example structure provided.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Add node"):
        new_node = StreamlitFlowNode(str(f"st-flow-node_{uuid4()}"), (0, 0), {'content': f'Node {len(st.session_state.curr_state.nodes) + 1}'}, 'default', 'right', 'left')
        st.session_state.curr_state.nodes.append(new_node)
        st.rerun()

with col2:
    if st.button("Delete Random Node"):
        if len(st.session_state.curr_state.nodes) > 0:
            node_to_delete = random.choice(st.session_state.curr_state.nodes)
            st.session_state.curr_state.nodes = [node for node in st.session_state.curr_state.nodes if node.id != node_to_delete.id]
            st.session_state.curr_state.edges = [edge for edge in st.session_state.curr_state.edges if edge.source != node_to_delete.id and edge.target != node_to_delete.id]
            st.rerun()

with col3:
    if st.button("Add Random Edge"):
        if len(st.session_state.curr_state.nodes) > 1:
            source = random.choice(st.session_state.curr_state.nodes)
            target = random.choice([node for node in st.session_state.curr_state.nodes if node.id != source.id])
            new_edge = StreamlitFlowEdge(f"{source.id}-{target.id}", source.id, target.id, animated=True)
            st.session_state.curr_state.edges.append(new_edge)
            st.rerun()
    
with col4:
    if st.button("Delete Random Edge"):
        if len(st.session_state.curr_state.edges) > 0:
            edge_to_delete = random.choice(st.session_state.curr_state.edges)
            st.session_state.curr_state.edges = [edge for edge in st.session_state.curr_state.edges if edge.id != edge_to_delete.id]
            st.rerun()

st.session_state.curr_state = streamlit_flow('example_flow', 
                                st.session_state.curr_state, 
                                layout=TreeLayout(direction='right'), 
                                fit_view=True, 
                                height=500, 
                                enable_node_menu=True,
                                enable_edge_menu=True,
                                enable_pane_menu=True,
                                get_edge_on_click=True,
                                get_node_on_click=True, 
                                show_minimap=True, 
                                hide_watermark=True, 
                                allow_new_edges=True,
                                min_zoom=0.1)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Current Nodes")
    for node in st.session_state.curr_state.nodes:
        st.write(node)

with col2:
    st.subheader("Current Edges")
    for edge in st.session_state.curr_state.edges:
        st.write(edge)

with col3:
    st.subheader("Current Selected Element")
    st.write(st.session_state.curr_state.selected_id)




