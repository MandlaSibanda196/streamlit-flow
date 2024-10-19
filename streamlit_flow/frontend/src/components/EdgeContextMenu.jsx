import { useState, useEffect } from "react";
import Button from "react-bootstrap/esm/Button";
import ButtonGroup from "react-bootstrap/esm/ButtonGroup";
import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import FloatingLabel from 'react-bootstrap/FloatingLabel';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';


const getEdgeStyle = (relationshipType) => {
  switch (relationshipType) {
    case 'OneToOne':
      return { label: '1:1', markerEnd: { type: 'arrow' }, markerStart: { type: 'arrow' } };
    case 'OneToMany':
      return { label: '1:N', markerEnd: { type: 'arrowclosed' } };
    case 'ManyToOne':
      return { label: 'N:1', markerStart: { type: 'arrowclosed' } };
    case 'ManyToMany':
      return { label: 'N:N', markerEnd: { type: 'arrowclosed' }, markerStart: { type: 'arrowclosed' } };
    default:
      return {};
  }
};

const ViewRelationshipModal = ({show, edge, nodes, edges, handleClose, theme, setEdgeContextMenu, setModalClosing, setEdges, handleDataReturnToStreamlit}) => {
    const [editedEdge, setEditedEdge] = useState(edge);
    
    useEffect(() => {
        if (edge && (!edge.data || !edge.data.from_table)) {
            // This is likely a manually created edge, so let's populate its data
            const sourceNode = nodes.find(node => node.id === edge.source);
            const targetNode = nodes.find(node => node.id === edge.target);
            
            // Parse the edge ID to extract column names
            const sourceHandleParts = edge.sourceHandle.split('-');
            const targetHandleParts = edge.targetHandle.split('-');
            const sourceColumn = sourceHandleParts[sourceHandleParts.length - 2] || 'Unknown';
            const targetColumn = targetHandleParts[targetHandleParts.length - 2] || 'Unknown';

            const newEdgeData = {
                relationship_type: 'OneToMany', // Default type
                from_table: sourceNode ? sourceNode.data.content.replace(/^\*\*(.*)\*\*$/, '$1') : 'Unknown',
                from_column: sourceColumn,
                to_table: targetNode ? targetNode.data.content.replace(/^\*\*(.*)\*\*$/, '$1') : 'Unknown',
                to_column: targetColumn,
                label: '1:N' // Default label
            };

            setEditedEdge({...edge, data: newEdgeData});
        } else {
            setEditedEdge(edge);
        }
    }, [edge, nodes]);

    const onExited = (e) => {
        setModalClosing(true);
        setEdgeContextMenu(null);
    }

    const onRelationshipTypeChange = (e) => {
        setEditedEdge((prev) => ({...prev, data: {...prev.data, relationship_type: e.target.value}}));
    }

    const handleSaveChanges = (e) => {
        const updatedEdges = edges.map(ed => ed.id === editedEdge.id ? editedEdge : ed);
        setEdges(updatedEdges);
        handleDataReturnToStreamlit(nodes, updatedEdges, null);
        setEdgeContextMenu(null);
    };

    return (
        <Modal show={show} onHide={handleClose} data-bs-theme={theme} onExited={onExited}>
            <Modal.Header closeButton>
                <Modal.Title>View Relationship</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <Row className="g-2">
                    <Col md>
                        <FloatingLabel controlId="floatingSelect" label="Relationship Type">
                            <Form.Select aria-label="Relationship Type" value={editedEdge.data?.relationship_type || ''} onChange={onRelationshipTypeChange}>
                                <option value="OneToOne">One-to-One</option>
                                <option value="OneToMany">One-to-Many</option>
                                <option value="ManyToOne">Many-to-One</option>
                                <option value="ManyToMany">Many-to-Many</option>
                            </Form.Select>
                        </FloatingLabel>
                    </Col>
                </Row>
                <Row className="g-2 mt-2">
                    <Col md={6}>
                        <FloatingLabel controlId="floatingInput" label="From Table">
                            <Form.Control type="text" placeholder="From Table" value={editedEdge.data?.from_table || ''} readOnly />
                        </FloatingLabel>
                    </Col>
                    <Col md={6}>
                        <FloatingLabel controlId="floatingInput" label="From Column">
                            <Form.Control type="text" placeholder="From Column" value={editedEdge.data?.from_column || ''} readOnly />
                        </FloatingLabel>
                    </Col>
                </Row>
                <Row className="g-2 mt-2">
                    <Col md={6}>
                        <FloatingLabel controlId="floatingInput" label="To Table">
                            <Form.Control type="text" placeholder="To Table" value={editedEdge.data?.to_table || ''} readOnly />
                        </FloatingLabel>
                    </Col>
                    <Col md={6}>
                        <FloatingLabel controlId="floatingInput" label="To Column">
                            <Form.Control type="text" placeholder="To Column" value={editedEdge.data?.to_column || ''} readOnly />
                        </FloatingLabel>
                    </Col>
                </Row>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={handleClose}>Close</Button>
                <Button variant="primary" onClick={handleSaveChanges}>Save Changes</Button>
            </Modal.Footer>
        </Modal>
    );
}

const EdgeContextMenu = ({edgeContextMenu, nodes, edges, setEdgeContextMenu, setEdges, handleDataReturnToStreamlit, theme}) => {
    const [showModal, setShowModal] = useState(false);
    const [modalClosing, setModalClosing] = useState(false);

    const handleClose = () => {
        setShowModal(false);
        setModalClosing(true);
    };

    const handleShow = () => setShowModal(true);

    const handleViewRelationship = (e) => {
        handleShow();
    }

    const handleDeleteEdge = (e) => {
        const updatedEdges = edges.filter(edge => edge.id !== edgeContextMenu.edge.id);
        setEdges(updatedEdges);
        handleDataReturnToStreamlit(nodes, updatedEdges, null);
        setEdgeContextMenu(null);
    }

    return (
        <>
        <div style={{position:'absolute',
                        top: edgeContextMenu.top,
                        left: edgeContextMenu.left,
                        right: edgeContextMenu.right,
                        bottom: edgeContextMenu.bottom,
                        backgroundColor: 'white',
                        borderRadius: '8px',
                        zIndex: 10}}>
            {(!showModal && !modalClosing) && <ButtonGroup vertical>
                <Button variant="outline-primary" onClick={handleViewRelationship}><i className="bi bi-eye"></i> View Relationship</Button>
                <Button variant="outline-danger" onClick={handleDeleteEdge}><i className="bi bi-trash3"></i> Delete Edge</Button>
            </ButtonGroup>}
        </div>
        <ViewRelationshipModal show={showModal}
            edge={edgeContextMenu.edge}
            nodes={nodes}
            edges={edges}
            handleClose={handleClose}
            theme={theme.base}
            setEdgeContextMenu={setEdgeContextMenu}
            setModalClosing={setModalClosing}
            setEdges={setEdges}
            handleDataReturnToStreamlit={handleDataReturnToStreamlit}/>
        </>
    );
};

export default EdgeContextMenu;
