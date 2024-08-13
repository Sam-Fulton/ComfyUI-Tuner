import React, { useState } from 'react';
import axios from 'axios';
import WorkflowViewerComponent from '../components/WorkflowViewerComponent';
import WorkflowEditorComponent from '../components/WorkflowEditorComponent';

const RunPage = () => {
    const [selectedWorkflow, setSelectedWorkflow] = useState(null);
    const [editedWorkflow, setEditedWorkflow] = useState(null);
    const [numRuns, setNumRuns] = useState(1);

    const handleSelectWorkflow = (workflow) => {
        setSelectedWorkflow(workflow);
        setEditedWorkflow(workflow.value);
    };

    const handleSaveWorkflow = (updatedWorkflow) => {
        setEditedWorkflow(updatedWorkflow.value);
    };

    const handleStartRun = () => {
        const payload = {
            base_workflow: editedWorkflow,
            num_runs: numRuns,
        };

        if (selectedWorkflow && selectedWorkflow._id) {
            payload.base_workflow_id = selectedWorkflow._id;
        }

        console.log('Payload being sent:', payload);
        
        axios.post('http://127.0.0.1:5000/api/startRun', payload)
            .then(response => {
                alert('Run started successfully');
            })
            .catch(error => {
                console.error('Error starting run:', error);
                alert('Error starting run');
            });
    };

    return (
        <div>
            <h1>Run Page</h1>
            <WorkflowViewerComponent onSelect={handleSelectWorkflow} />
            {selectedWorkflow && (
                <WorkflowEditorComponent
                    workflow={selectedWorkflow}
                    onSave={handleSaveWorkflow}
                />
            )}
            <div>
                <label>Number of Runs</label>
                <input
                    type="number"
                    value={numRuns}
                    onChange={e => setNumRuns(e.target.value)}
                    min="1"
                />
            </div>
            <button onClick={handleStartRun}>Start Run</button>
        </div>
    );
};

export default RunPage;
