import React, { useEffect, useState } from 'react';
import axios from 'axios';

const WorkflowViewerComponent = ({ onSelect, resetSelection }) => {
    const [workflows, setWorkflows] = useState([]);
    const [selectedWorkflowId, setSelectedWorkflowId] = useState('');

    useEffect(() => {
        axios.get('http://127.0.0.1:5000/api/getBaseWorkflows')
            .then(response => {
                console.log('Workflows fetched successfully:', response.data);
                setWorkflows(response.data.workflows);
            })
            .catch(error => {
                console.error('Error fetching workflows:', error);
                alert('Error fetching workflows');
            });
    }, []);

    useEffect(() => {
        if (resetSelection) {
            setSelectedWorkflowId('');
        }
    }, [resetSelection]);

    const handleSelectChange = (event) => {
        const workflowId = event.target.value;
        const workflow = workflows.find(wf => wf._id === workflowId);
        setSelectedWorkflowId(workflowId);
        onSelect(workflow);
    };

    return (
        <div>
            <h1>Select a Workflow</h1>
            <select onChange={handleSelectChange} value={selectedWorkflowId}>
                <option value="" disabled>Select a workflow</option>
                {workflows.map(workflow => (
                    <option key={workflow._id} value={workflow._id}>
                        {workflow._id}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default WorkflowViewerComponent;
