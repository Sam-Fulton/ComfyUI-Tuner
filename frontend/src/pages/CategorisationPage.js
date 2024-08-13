import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CategorisationComponent from '../components/CategorisationComponent';

const CategorisationPage = () => {
    const [workflows, setWorkflows] = useState([]);
    const [selectedWorkflow, setSelectedWorkflow] = useState(null);
    const [outputs, setOutputs] = useState([]);
    const [resetImageSelection, setResetImageSelection] = useState(false);

    useEffect(() => {
        axios.get('http://127.0.0.1:5000/api/getRunWorkflows')
            .then(response => {
                if (response.data && response.data.workflows) {
                    setWorkflows(response.data.workflows);
                } else {
                    alert('No workflows found.');
                }
            })
            .catch(error => {
                console.error('Error fetching workflows:', error);
                alert('Error fetching workflows');
            });
    }, []);

    const handleWorkflowSelect = (event) => {
        const workflowId = event.target.value;
        setSelectedWorkflow(workflowId);
        setResetImageSelection(true);

        axios.post('http://127.0.0.1:5000/api/getOutputs', { run_workflow_id: workflowId })
            .then(response => {
                if (response.data && response.data.outputs) {
                    setOutputs(response.data.outputs);
                } else {
                    alert('No outputs found for the selected workflow.');
                }
            })
            .catch(error => {
                console.error('Error fetching outputs:', error);
                alert('Error fetching outputs');
            });
    };

    useEffect(() => {
        if (resetImageSelection) {
            setResetImageSelection(false);
        }
    }, [resetImageSelection]);

    return (
        <div>
            <h1>Categorisation Page</h1>
            <select onChange={handleWorkflowSelect} value={selectedWorkflow || ''}>
                <option value="" disabled>Select a workflow</option>
                {workflows.map(workflow => (
                    <option key={workflow._id} value={workflow._id}>
                        {workflow.value.name || workflow._id}
                    </option>
                ))}
            </select>
            {outputs.length > 0 && (
                <CategorisationComponent 
                    outputs={outputs} 
                    resetImageSelection={resetImageSelection} 
                />
            )}
        </div>
    );
};

export default CategorisationPage;
