import React, { useState } from 'react';
import WorkflowViewerComponent from '../components/WorkflowViewerComponent';
import WorkflowEditorComponent from '../components/WorkflowEditorComponent';
import axios from 'axios';

const UploadWorkflowPage = () => {
    const [selectedWorkflow, setSelectedWorkflow] = useState(null);
    const [isCreatingNewWorkflow, setIsCreatingNewWorkflow] = useState(false);
    const [resetSelection, setResetSelection] = useState(false);

    const handleNewWorkflow = () => {
        setIsCreatingNewWorkflow(true);
        setSelectedWorkflow(null);
        setResetSelection(true);
        setTimeout(() => setResetSelection(false), 0);
    };

    const handleSaveWorkflow = (workflow) => {
        const url = workflow._id
            ? `http://localhost:5000/api/updateWorkflow/${workflow._id}`
            : 'http://localhost:5000/api/uploadWorkflow';

        axios.post(url, workflow)
            .then(response => {
                alert('Workflow saved successfully');
                setIsCreatingNewWorkflow(false);
                setSelectedWorkflow(null);
                setResetSelection(true);
                setTimeout(() => setResetSelection(false), 0);
            })
            .catch(error => {
                console.error('Error saving workflow:', error);
                alert('Error saving workflow');
            });
    };

    const handleSelectWorkflow = (workflow) => {
        setIsCreatingNewWorkflow(false);
        setSelectedWorkflow(workflow);
    };

    return (
        <div>
            <h1>Home Page</h1>
            <button onClick={handleNewWorkflow}>Create New Workflow</button>
            <WorkflowViewerComponent onSelect={handleSelectWorkflow} resetSelection={resetSelection} apiUrl='http://127.0.0.1:8188/api/getWorkflows' />
            {(isCreatingNewWorkflow || selectedWorkflow) && (
                <WorkflowEditorComponent 
                    workflow={isCreatingNewWorkflow ? null : selectedWorkflow} 
                    onSave={handleSaveWorkflow} 
                />
            )}
        </div>
    );
};

export default UploadWorkflowPage;
