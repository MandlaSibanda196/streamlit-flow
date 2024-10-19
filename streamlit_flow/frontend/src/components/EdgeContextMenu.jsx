import { useState } from "react";
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
    
    const onExited = (e) => {
        setModalClosing(true);
        setEdgeContextMenu(null);
    }

    const onRelationshipTypeChange = (e) => {
        setEditedEdge((prev) => ({...prev, data: {...prev.data, relationship_type: e.target.value, label: e.target.value}}));
    }

    const onFromTableChange = (e) => {
        setEditedEdge((prev) => ({...prev, data: {...prev.data, from_table: e.target.value}}));
    }

    const onFromColumnChange = (e) => {
        setEditedEdge((prev) => ({...prev, data: {...prev.data, from_column: e.target.value}}));
    }

    const onToTableChange = (e) => {
        setEditedEdge((prev) => ({...prev, data: {...prev.data, to_table: e.target.value}}));
    }

    const onToColumnChange = (e) => {
        setEditedEdge((prev) => ({...prev, data: {...prev.data, to_column: e.target.value}}));
    }

    const onEdgeTypeChange = (e) => {
        setEditedEdge((prev) => ({...prev, type: e.target.value}));
    }

    const onAnimatedChange = (e) => {
        setEditedEdge((prev) => ({...prev, animated: e.target.checked}));
    }

    const handleSaveChanges = (e) => {
        const updatedEdge = {
            ...editedEdge,
            ...getEdgeStyle(editedEdge.data.relationship_type)
        };
        const updatedEdges = edges.map(ed => ed.id === updatedEdge.id ? updatedEdge : ed);
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
                            <Form.Control type="text" placeholder="From Table" value={editedEdge.data?.from_table || ''} onChange={onFromTableChange}/>
                        </FloatingLabel>
                    </Col>
                    <Col md={6}>
                        <FloatingLabel controlId="floatingInput" label="From Column">
                            <Form.Control type="text" placeholder="From Column" value={editedEdge.data?.from_column || ''} onChange={onFromColumnChange}/>
                        </FloatingLabel>
                    </Col>
                </Row>
                <Row className="g-2 mt-2">
                    <Col md={6}>
                        <FloatingLabel controlId="floatingInput" label="To Table">
                            <Form.Control type="text" placeholder="To Table" value={editedEdge.data?.to_table || ''} onChange={onToTableChange}/>
                        </FloatingLabel>
                    </Col>
                    <Col md={6}>
                        <FloatingLabel controlId="floatingInput" label="To Column">
                            <Form.Control type="text" placeholder="To Column" value={editedEdge.data?.to_column || ''} onChange={onToColumnChange}/>
                        </FloatingLabel>
                    </Col>
                </Row>
                <Row className="g-2 mt-2">
                    <Col md>
                        <FloatingLabel controlId="floatingSelect" label="Edge Type">
                            <Form.Select aria-label="Edge Type" value={editedEdge.type} onChange={onEdgeTypeChange}>
                                <option value="default">Default</option>
                                <option value="straight">Straight</option>
                                <option value="step">Step</option>
                                <option value="smoothstep">Smooth Step</option>
                                <option value="simplebezier">Simple Bezier</option>
                            </Form.Select>
                        </FloatingLabel>
                    </Col>
                </Row>
                <Row className="g-2 mt-2">
                    <Col md>
                        <Form.Check 
                            type="switch"
                            id="animated-switch"
                            label="Animated"
                            checked={editedEdge.animated || false}
                            onChange={onAnimatedChange}
                        />
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
