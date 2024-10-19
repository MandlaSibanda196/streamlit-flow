import { useState } from 'react';
import Button from 'react-bootstrap/Button';
import ButtonGroup from 'react-bootstrap/esm/ButtonGroup';
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import FloatingLabel from 'react-bootstrap/FloatingLabel';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import ListGroup from 'react-bootstrap/ListGroup';

const EditNodeModal = ({show, node, handleClose, theme, setNodeContextMenu, setModalClosing, setNodes, nodes, edges, handleDataReturnToStreamlit}) => {

    const [editedNode, setEditedNode] = useState(node);
    const [columns, setColumns] = useState(editedNode.data.columns || []);
    const [newColumnName, setNewColumnName] = useState('');
    const [newColumnType, setNewColumnType] = useState('string');
    const allowTypeChange = edges.filter(edge => edge.source === editedNode.id || edge.target === editedNode.id).length === 0;
    
    const onExited = (e) => {
        setModalClosing(true);
        setNodeContextMenu(null);
    }

    const onNodeContentChange = (e) => {
        setEditedNode((editedNode) => ({...editedNode, data: {...editedNode.data, content: e.target.value}}));
    };

    const onNodeWidthChange = (e) => {
        const currStyle = editedNode.data.style;
        setEditedNode((editedNode) => ({...editedNode, width: e.target.value, style: {...currStyle, width: e.target.value + 'px'}}));
    };

    const onNodeTypeChange = (e) => {
        setEditedNode((editedNode) => ({...editedNode, type: e.target.value}));
    };

    const onNodeSourcePositionChange = (e) => {
        setEditedNode((editedNode) => ({...editedNode, sourcePosition: e.target.value}));
    };

    const onNodeTargetPositionChange = (e) => {
        setEditedNode((editedNode) => ({...editedNode, targetPosition: e.target.value}));
    };

    const onNodeDraggableChange = (e) => {
        setEditedNode((editedNode) => ({...editedNode, draggable: e.target.checked}));
    };

    const onNodeConnectableChange = (e) => {
        setEditedNode((editedNode) => ({...editedNode, connectable: e.target.checked}));
    };

    const onNodeDeletableChange = (e) => {
        setEditedNode((editedNode) => ({...editedNode, deletable: e.target.checked}));
    };

    const handleAddColumn = () => {
        if (newColumnName && newColumnType) {
            setColumns([...columns, { column_name: newColumnName, type: newColumnType }]);
            setNewColumnName('');
            setNewColumnType('string');
        }
    };

    const handleRemoveColumn = (index) => {
        setColumns(columns.filter((_, i) => i !== index));
    };

    const handleSave = () => {
        const updatedNode = {...editedNode, data: {...editedNode.data, columns: columns}};
        setNodes(nodes.map(n => n.id === updatedNode.id ? updatedNode : n));
        handleDataReturnToStreamlit(nodes.map(n => n.id === updatedNode.id ? updatedNode : n), edges, updatedNode.id);
        handleClose();
    };

    return (
        <Modal show={show} onHide={handleClose} data-bs-theme={theme} onExited={onExited}>
            <Modal.Header closeButton>
                <Modal.Title>Edit Node</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Form>
                    <Form.Group className="mb-3">
                        <Form.Label>Node Content</Form.Label>
                        <Form.Control as="textarea" rows={3} value={editedNode.data.content} onChange={onNodeContentChange} />
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Form.Label>Columns</Form.Label>
                        <ListGroup>
                            {columns.map((column, index) => (
                                <ListGroup.Item key={index} className="d-flex justify-content-between align-items-center">
                                    {column.column_name} ({column.type})
                                    <Button variant="outline-danger" size="sm" onClick={() => handleRemoveColumn(index)}>Remove</Button>
                                </ListGroup.Item>
                            ))}
                        </ListGroup>
                    </Form.Group>
                    <Form.Group className="mb-3">
                        <Row>
                            <Col>
                                <Form.Control 
                                    type="text" 
                                    placeholder="New Column Name" 
                                    value={newColumnName}
                                    onChange={(e) => setNewColumnName(e.target.value)}
                                />
                            </Col>
                            <Col>
                                <Form.Select 
                                    value={newColumnType}
                                    onChange={(e) => setNewColumnType(e.target.value)}
                                >
                                    <option value="string">String</option>
                                    <option value="number">Number</option>
                                    <option value="boolean">Boolean</option>
                                    <option value="date">Date</option>
                                </Form.Select>
                            </Col>
                            <Col>
                                <Button variant="outline-primary" onClick={handleAddColumn}>Add Column</Button>
                            </Col>
                        </Row>
                    </Form.Group>
                    {/* Keep other form fields for node properties */}
                </Form>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={handleClose}>Close</Button>
                <Button variant="primary" onClick={handleSave}>Save Changes</Button>
            </Modal.Footer>
        </Modal>
    );
};

const NodeContextMenu = ({nodeContextMenu, nodes, edges, setNodeContextMenu, setNodes, setEdges, theme, handleDataReturnToStreamlit}) => {
    
    const [showModal, setShowModal] = useState(false);
    const [modalClosing, setModalClosing] = useState(false);

    const handleClose = () => {
        setShowModal(false);
        setModalClosing(true);
    };

    const handleShow = () => setShowModal(true);

    const handleEditNode = (e) => {
        handleShow();
    }

    const handleDeleteNode = (e) => {
        const updatedNodes = nodes.filter(node => node.id !== nodeContextMenu.node.id)
        const updatedEdges = edges.filter(edge => edge.source !== nodeContextMenu.node.id && edge.target !== nodeContextMenu.node.id)
        setNodes(updatedNodes);
        setEdges(updatedEdges);
        handleDataReturnToStreamlit(updatedNodes, updatedEdges, null);
        setNodeContextMenu(null);
    }

    return (
        <>
            <div style={{position: 'absolute', 
                            top: nodeContextMenu.top, 
                            left: nodeContextMenu.left, 
                            right: nodeContextMenu.right, 
                            bottom: nodeContextMenu.bottom,
                            backgroundColor: 'white',
                            borderRadius: '8px',
                            zIndex: 10}}>
                {(!showModal && !modalClosing) && <ButtonGroup vertical>
                    <Button variant="outline-primary" onClick={handleEditNode}><i className="bi bi-tools"></i> Edit Node</Button>
                    <Button variant="outline-danger" onClick={handleDeleteNode}><i className="bi bi-trash3"></i> Delete Node</Button>
                </ButtonGroup>}
            </div>
            <EditNodeModal show={showModal}
                node={nodeContextMenu.node}
                nodes={nodes}
                edges={edges}
                handleClose={handleClose}
                theme={theme.base}
                setNodeContextMenu={setNodeContextMenu}
                setModalClosing={setModalClosing}
                setNodes={setNodes}
                handleDataReturnToStreamlit={handleDataReturnToStreamlit}
                />    
        </>
    );
};

export default NodeContextMenu;
