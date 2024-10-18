import streamlit as st
from streamlit_flow import streamlit_flow
from streamlit_flow.elements import StreamlitFlowNode, StreamlitFlowEdge
from streamlit_flow.state import StreamlitFlowState
from streamlit_flow.layouts import TreeLayout
from uuid import uuid4

st.set_page_config("Power BI Model Simulator", layout="wide")

# Initialize session state
if 'curr_state' not in st.session_state:
    st.session_state.curr_state = StreamlitFlowState([], [])

st.title("Power BI Model Simulator")

# Sidebar for adding tables and columns
with st.sidebar:
    st.header("Add Table")
    table_name = st.text_input("Table Name")
    columns = st.text_area("Columns (one per line)")
    
    if st.button("Add Table"):
        if table_name and columns:
            new_node = StreamlitFlowNode(
                str(uuid4()),
                (0, 0),
                {'content': f"{table_name}\n{columns}"},
                'default',
                'right',
                'left'
            )
            st.session_state.curr_state.nodes.append(new_node)
            st.success(f"Table '{table_name}' added successfully!")
            st.rerun()

# Main area
col1, col2 = st.columns(2)

with col1:
    if st.button("Add Relationship"):
        if len(st.session_state.curr_state.nodes) > 1:
            source = st.selectbox("From Table", [node.data['content'].split('\n')[0] for node in st.session_state.curr_state.nodes], key="from_table")
            target = st.selectbox("To Table", [node.data['content'].split('\n')[0] for node in st.session_state.curr_state.nodes if node.data['content'].split('\n')[0] != source], key="to_table")
            
            source_node = next(node for node in st.session_state.curr_state.nodes if node.data['content'].split('\n')[0] == source)
            target_node = next(node for node in st.session_state.curr_state.nodes if node.data['content'].split('\n')[0] == target)
            
            new_edge = StreamlitFlowEdge(f"{source_node.id}-{target_node.id}", source_node.id, target_node.id, animated=True, label="Relationship")
            st.session_state.curr_state.edges.append(new_edge)
            st.success("Relationship created successfully!")
            st.rerun()

with col2:
    if st.button("Clear All"):
        st.session_state.curr_state = StreamlitFlowState([], [])
        st.rerun()

# Render the flow diagram
st.session_state.curr_state = streamlit_flow(
    'power_bi_model_simulator',
    st.session_state.curr_state,
    layout=TreeLayout(direction='right'),
    fit_view=True,
    height=600,
    enable_node_menu=True,
    enable_edge_menu=True,
    enable_pane_menu=True,
    get_edge_on_click=True,
    get_node_on_click=True,
    show_minimap=True,
    hide_watermark=True,
    allow_new_edges=True,
    min_zoom=0.1
)

# Display selected node or edge information
if st.session_state.curr_state.selected_id:
    st.subheader("Selected Item")
    selected_node = next((node for node in st.session_state.curr_state.nodes if node.id == st.session_state.curr_state.selected_id), None)
    selected_edge = next((edge for edge in st.session_state.curr_state.edges if edge.id == st.session_state.curr_state.selected_id), None)
    
    if selected_node:
        st.write("Selected Table:")
        st.write(selected_node.data['content'])
    elif selected_edge:
        st.write("Selected Relationship:")
        source_node = next(node for node in st.session_state.curr_state.nodes if node.id == selected_edge.source)
        target_node = next(node for node in st.session_state.curr_state.nodes if node.id == selected_edge.target)
        st.write(f"From: {source_node.data['content'].split('\n')[0]}")
        st.write(f"To: {target_node.data['content'].split('\n')[0]}")
