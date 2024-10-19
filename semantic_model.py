import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout
import random
import json
import os
from streamlit.runtime.state import SessionState
from uuid import uuid4

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
        deletable=True,
        handles=[
            {
                'id': f"{table_name}-{col['column_name']}-source",
                'type': 'source',
                'position': 'right'
            } for col in columns
        ] + [
            {
                'id': f"{table_name}-{col['column_name']}-target",
                'type': 'target',
                'position': 'left'
            } for col in columns
        ]
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

def on_edge_create(new_edge, nodes, edges):
    source_node = next((node for node in nodes if node.id == new_edge.source), None)
    target_node = next((node for node in nodes if node.id == new_edge.target), None)
    
    if source_node and target_node:
        source_column = new_edge.source_handle.split('-')[-2] if new_edge.source_handle else 'Unknown'
        target_column = new_edge.target_handle.split('-')[-2] if new_edge.target_handle else 'Unknown'
        
        new_edge.data = {
            'relationship_type': 'OneToMany',  # Default type, can be changed later
            'from_table': source_node.data['content'].strip('*'),
            'from_column': source_column,
            'to_table': target_node.data['content'].strip('*'),
            'to_column': target_column,
            'label': f'1:N'  # Default label, can be changed later
        }
    
    return new_edge

def update_edge_data(edge, nodes):
    source_node = next((node for node in nodes if node.id == edge.source), None)
    target_node = next((node for node in nodes if node.id == edge.target), None)
    
    if source_node and target_node:
        # Parse the edge ID to extract column names
        edge_parts = edge.id.split('_')
        source_column = edge_parts[-3] if len(edge_parts) > 3 else 'Unknown'
        target_column = edge_parts[-2] if len(edge_parts) > 2 else 'Unknown'
        
        edge.data = {
            'relationship_type': 'OneToMany',  # Default type, can be changed later
            'from_table': source_node.data['content'].strip('*'),
            'from_column': source_column,
            'to_table': target_node.data['content'].strip('*'),
            'to_column': target_column,
            'label': f'1:N'  # Default label, can be changed later
        }
    
    return edge

def parse_handle_id(handle_id):
    parts = handle_id.split('-')
    if len(parts) >= 3:
        return parts[-2]
    return 'Unknown'

def parse_edge_id(edge_id):
    parts = edge_id.split('_')
    if len(parts) >= 4:
        return parts[-3], parts[-2]
    return 'Unknown', 'Unknown'

def get_column_name(handle_id):
    parts = handle_id.split('-')
    return parts[-2] if len(parts) >= 2 else 'Unknown'

if 'curr_state' not in st.session_state:
    # Initialize with an empty state (no nodes or edges)
    st.session_state.curr_state = StreamlitFlowState([], [])

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

# Keep the button to add tables
if st.button("Add Table"):
    new_node = StreamlitFlowNode(
        str(f"st-flow-node_{uuid4()}"),
        (len(st.session_state.curr_state.nodes) * 200, 0),
        {
            'content': f'New Table {len(st.session_state.curr_state.nodes) + 1}',
            'columns': []
        },
        'default',
        'right',
        'left',
        deletable=True
    )
    st.session_state.curr_state.nodes.append(new_node)
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

# Update edge data for any new edges
for edge in st.session_state.curr_state.edges:
    if not hasattr(edge, 'data') or not edge.data:
        edge = update_edge_data(edge, st.session_state.curr_state.nodes)

# Display information about the selected element
st.subheader("Current Selected Element")
selected_id = st.session_state.curr_state.selected_id

if selected_id:
    selected_node = next((node for node in st.session_state.curr_state.nodes if node.id == selected_id), None)
    selected_edge = next((edge for edge in st.session_state.curr_state.edges if edge.id == selected_id), None)

    if selected_node:
        st.write(f"Table: {selected_node.data['content']}")
        if 'columns' in selected_node.data:
            st.write("Columns:")
            for column in selected_node.data['columns']:
                st.write(f"- {column['column_name']} ({column['type']})")
        else:
            st.write("No columns defined for this table.")

    elif selected_edge:
        st.write("Relationship:")
        if hasattr(selected_edge, 'data') and selected_edge.data:
            st.write(f"Type: {selected_edge.data.get('relationship_type', 'Not specified')}")
            st.write(f"From: {selected_edge.data.get('from_table', 'Unknown')} ({selected_edge.data.get('from_column', 'Unknown')})")
            st.write(f"To: {selected_edge.data.get('to_table', 'Unknown')} ({selected_edge.data.get('to_column', 'Unknown')})")
            st.write(f"Label: {selected_edge.data.get('label', 'Not specified')}")
        else:
            st.write("Edge data not available.")
        st.write(f"Animated: {getattr(selected_edge, 'animated', False)}")
        
        # Debug information
        st.write("Edge attributes:")
        for attr in dir(selected_edge):
            if not attr.startswith('__'):
                st.write(f"{attr}: {getattr(selected_edge, attr)}")

else:
    st.write("No element selected")

# col1, col2, col3 = st.columns(3)

# with col1:
#     st.subheader("Current Nodes")
#     for node in st.session_state.curr_state.nodes:
#         st.write(node)

# with col2:
#     st.subheader("Current Edges")
#     for edge in st.session_state.curr_state.edges:
#         st.write(edge)

# with col3:
#     st.subheader("Current Selected Element")
#     st.write(st.session_state.curr_state.selected_id)












