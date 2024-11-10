import React, { useState, useEffect } from 'react';
import axios from 'axios';
import BaseWorkflowSelector from '../components/BaseWorkflowSelector';
import ComparisonComponent from '../components/ComparisonComponent';

const RoundComparisonPage = () => {
    const [baseWorkflows, setBaseWorkflows] = useState([]);
    const [selectedBaseWorkflow, setSelectedBaseWorkflow] = useState(null);
    const [runWorkflows, setRunWorkflows] = useState([]);
    const [outputs, setOutputs] = useState([]);
    const [comparisonQueue, setComparisonQueue] = useState([]);
    const [currentComparison, setCurrentComparison] = useState(null);
    const [round, setRound] = useState(0);
    const [comparisonResults, setComparisonResults] = useState([]);

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
        setOutputs([]);
        setComparisonQueue([]);
        setCurrentComparison(null);

        axios.post('http://127.0.0.1:5000/api/getRunWorkflowsByBaseID', { base_workflow_id: baseWorkflowId })
            .then(response => {
                const workflows = response.data.run_workflows;
                setRunWorkflows(workflows);
                const workflowIds = workflows.map(wf => wf._id);
                return axios.post('http://127.0.0.1:5000/api/getOutputs', { workflow_ids: workflowIds });
            })
            .then(response => {
                setOutputs(response.data.outputs);
                createComparisonQueue(response.data.outputs);
            })
            .catch(error => {
                console.error('Error fetching run workflows or outputs:', error);
                alert('Error fetching run workflows or outputs');
            });
    };

    const createComparisonQueue = (outputs) => {
        let queue = [];
        for (let i = 0; i < outputs.length; i++) {
            for (let j = i + 1; j < outputs.length; j++) {
                queue.push({ image1: outputs[i], image2: outputs[j] });
            }
        }
        setComparisonQueue(queue);
        setCurrentComparison(queue[0]);
    };

    const handleComparison = (winner) => {
        setComparisonResults([...comparisonResults, { ...currentComparison, winner }]);

        const nextIndex = comparisonQueue.indexOf(currentComparison) + 1;
        if (nextIndex < comparisonQueue.length) {
            setCurrentComparison(comparisonQueue[nextIndex]);
        } else {
            alert('All comparisons are done!');
        }
    };

    return (
        <div>
            <h1>Round Comparison Page</h1>

            <BaseWorkflowSelector
                baseWorkflows={baseWorkflows}
                selectedBaseWorkflow={selectedBaseWorkflow}
                onSelect={handleBaseWorkflowSelect}
            />

            {currentComparison && (
                <ComparisonComponent
                    image1={currentComparison.image1}
                    image2={currentComparison.image2}
                    onCompare={(winner) => handleComparison(winner)}
                />
            )}
        </div>
    );
};

export default RoundComparisonPage;
