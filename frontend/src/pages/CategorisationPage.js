import React, { useState, useEffect } from 'react';
import axios from 'axios';
import CategorisationComponent from '../components/CategorisationComponent';
import BaseWorkflowSelector from '../components/BaseWorkflowSelector';
import GroupTimestampSelector from '../components/GroupTimestampSelector';

const CategorisationPage = () => {
    const [baseWorkflows, setBaseWorkflows] = useState([]);
    const [selectedBaseWorkflow, setSelectedBaseWorkflow] = useState(null);
    const [runWorkflows, setRunWorkflows] = useState([]);
    const [selectedGroupTimestamp, setSelectedGroupTimestamp] = useState('');
    const [selectedRunWorkflow, setSelectedRunWorkflow] = useState(null);
    const [outputs, setOutputs] = useState([]);
    const [resetImageSelection, setResetImageSelection] = useState(false);

    useEffect(() => {
        axios.get('http://127.0.0.1:5000/api/getBaseWorkflows')
            .then(response => {
                setBaseWorkflows(response.data.workflows);
            })
            .catch(error => {
                console.error('Error fetching base workflows:', error);
                alert('Error fetching base workflows');
            });
    }, []);

    const handleBaseWorkflowSelect = (event) => {
        const baseWorkflowId = event.target.value;
        const selectedWorkflow = baseWorkflows.find(wf => wf._id === baseWorkflowId);
        setSelectedBaseWorkflow(selectedWorkflow);
        setRunWorkflows([]);
        setSelectedGroupTimestamp('');
        setOutputs([]);
        setSelectedRunWorkflow(null);

        axios.post('http://127.0.0.1:5000/api/getRunWorkflowsByBaseID', { base_workflow_id: baseWorkflowId })
            .then(response => {
                setRunWorkflows(response.data.run_workflows);
            })
            .catch(error => {
                console.error('Error fetching run workflows:', error);
                alert('Error fetching run workflows');
            });
    };

    const handleGroupTimestampSelect = (event) => {
        const timestamp = event.target.value;
        setSelectedGroupTimestamp(timestamp);
        setOutputs([]);
        setSelectedRunWorkflow(null); // Ensure no default selection

        const matchingWorkflows = runWorkflows.filter(workflow => Number(workflow.group_timestamp) === Number(timestamp));
        if (matchingWorkflows.length === 1) {
            // Automatically select the only workflow if there's only one
            setSelectedRunWorkflow(matchingWorkflows[0]._id);
            fetchOutputs(matchingWorkflows[0]._id);
        }
    };

    const handleRunWorkflowSelect = (event) => {
        const workflowId = event.target.value;
        setSelectedRunWorkflow(workflowId);
        setResetImageSelection(true);

        fetchOutputs(workflowId);
    };

    const fetchOutputs = (workflowId) => {
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

            <BaseWorkflowSelector 
                baseWorkflows={baseWorkflows}
                selectedBaseWorkflow={selectedBaseWorkflow}
                onSelect={handleBaseWorkflowSelect}
            />

            {runWorkflows.length > 0 && (
                <GroupTimestampSelector 
                    runWorkflows={runWorkflows}
                    selectedGroupTimestamp={selectedGroupTimestamp}
                    onSelect={handleGroupTimestampSelect}
                />
            )}

            {selectedGroupTimestamp && runWorkflows.length > 0 && (
                <div>
                    <label>Select Run Workflow</label>
                    <select onChange={handleRunWorkflowSelect} value={selectedRunWorkflow || ''}>
                        <option value="" disabled>Select a run workflow</option>
                        {runWorkflows
                            .filter(workflow => Number(workflow.group_timestamp) === Number(selectedGroupTimestamp))
                            .map(workflow => (
                                <option key={workflow._id} value={workflow._id}>
                                    {workflow._id}
                                </option>
                            ))}
                    </select>
                </div>
            )}

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
