import React, { useState, useEffect } from 'react';
import axios from 'axios';
import BaseWorkflowSelector from '../components/BaseWorkflowSelector';
import GroupTimestampSelector from '../components/GroupTimestampSelector';
import QualityAssessmentChart from '../components/QualityAssessmentChart';
import ParameterChart from '../components/ParameterChart';
import WorkflowEditorComponent from '../components/WorkflowEditorComponent';

const AnalysisPage = () => {
    const [baseWorkflows, setBaseWorkflows] = useState([]);
    const [selectedBaseWorkflow, setSelectedBaseWorkflow] = useState(null);
    const [runWorkflows, setRunWorkflows] = useState([]);
    const [selectedGroupTimestamp, setSelectedGroupTimestamp] = useState('');
    const [qualityAssessments, setQualityAssessments] = useState([]);
    const [threshold, setThreshold] = useState(0.5);
    const [editedWorkflow, setEditedWorkflow] = useState(null);
    const [numRuns, setNumRuns] = useState(1); 

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
        setEditedWorkflow(selectedWorkflow?.value || null);
        setRunWorkflows([]);
        setSelectedGroupTimestamp('');
        setQualityAssessments([]);

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
        setQualityAssessments([]);

        const matchingWorkflows = runWorkflows.filter(workflow => Number(workflow.group_timestamp) === Number(timestamp));
        const runWorkflowIds = matchingWorkflows.map(workflow => workflow._id);

        axios.post('http://127.0.0.1:5000/api/getQualityAssessmentByRunWorkflow', { run_workflow_ids: runWorkflowIds })
            .then(response => {
                setQualityAssessments(response.data.quality_assessments);
            })
            .catch(error => {
                console.error('Error fetching quality assessments:', error);
                alert('Error fetching quality assessments');
            });
    };

    const getGoodBadCounts = () => {
        const counts = {};
        qualityAssessments.forEach((qa) => {
            const runId = qa.run_workflow_id;
            const quality = qa.quality_assessment.toLowerCase();
            if (!counts[runId]) counts[runId] = { good: 0, bad: 0 };
            if (quality === 'good' || quality === 'bad') {
                counts[runId][quality]++;
            }
        });
        return counts;
    };

    const getInputValues = (inputValue) => {
        if (Array.isArray(inputValue)) {
            return inputValue;
        } else if (inputValue && typeof inputValue === 'object' && 'values' in inputValue) {
            return inputValue.values;
        }
        return null;
    };

    const getRunInputValue = (runInput) => {
        if (Array.isArray(runInput)) {
            return runInput.join(', ');
        } else if (runInput && typeof runInput === 'object' && 'values' in runInput) {
            return runInput.values.join(', ');
        }
        return String(runInput);
    };

    const processQualityAssessments = (paramCounts, paramLabel, runValue, runId, qualityAssessments) => {
        const qaResults = qualityAssessments.filter(qa => qa.run_workflow_id === runId);
        qaResults.forEach((qa) => {
            const quality = qa.quality_assessment.toLowerCase();
            if (quality === 'good' || quality === 'bad') {
                if (!paramCounts[paramLabel][runValue]) {
                    paramCounts[paramLabel][runValue] = { good: 0, bad: 0 };
                }
                paramCounts[paramLabel][runValue][quality]++;
            }
        });
    };

    const processNodeInput = (inputs, classType, paramCounts, runWorkflows, qualityAssessments) => {
        for (const inputKey in inputs) {
            if (inputs.hasOwnProperty(inputKey)) {
                const inputValue = inputs[inputKey];
                const valuesArray = getInputValues(inputValue);
                if (valuesArray && valuesArray.length > 0) {
                    const valueTypes = new Set(valuesArray.map(val => typeof val));
                    if (valueTypes.size === 1) {
                        const paramLabel = `${classType}.${inputKey}`;
                        if (!paramCounts[paramLabel]) paramCounts[paramLabel] = {};
                        runWorkflows.forEach((workflow) => {
                            const runId = workflow._id;
                            if (workflow.value?.[classType] && workflow.value[classType]?.inputs?.[inputKey]) {
                                const runValue = getRunInputValue(workflow.value[classType]?.inputs?.[inputKey]);
                                processQualityAssessments(paramCounts, paramLabel, runValue, runId, qualityAssessments);
                            }
                        });
                    }
                }
            }
        }
    };

    const getParameterCounts = () => {
        const paramCounts = {};
        if (!selectedBaseWorkflow) {
            console.log("No base workflow selected.");
            return paramCounts;
        }

        const nodes = selectedBaseWorkflow.value;

        for (const k in nodes) {
            if (nodes.hasOwnProperty(k)) {
                const classType = nodes[k]?.class_type;
                const inputs = nodes[k]?.inputs;
                processNodeInput(inputs, k, paramCounts, runWorkflows, qualityAssessments);
            }
        }
        
        
        return paramCounts;
    };

    const handleSaveWorkflow = (updatedWorkflow) => {
        setEditedWorkflow(updatedWorkflow.value);
    };

    const handleStartRun = () => {
        const payload = {
            base_workflow: editedWorkflow,
            num_runs: numRuns,
        };

        if (selectedBaseWorkflow && selectedBaseWorkflow._id) {
            payload.base_workflow_id = selectedBaseWorkflow._id;
        }

        console.log('Payload being sent:', payload);
        
        axios.post('http://127.0.0.1:5000/api/startRun', payload)
            .then(response => {
                alert('Run Executed');
            })
            .catch(error => {
                console.error('Error starting run:', error);
                alert('Error starting run');
            });
    };

    const handleUpdateWorkflow = () => {
        if (!selectedBaseWorkflow || !editedWorkflow) {
            alert('Please select a base workflow and ensure there are run workflows available.');
            return;
        }
    
        const runWorkflowIds = runWorkflows.map(workflow => workflow._id);
    
        const payload = {
            base_workflow_id: selectedBaseWorkflow._id,
            run_workflow_ids: runWorkflowIds,
            threshold: threshold,
        };
    
        axios.post('http://127.0.0.1:5000/api/rerun_workflow', payload)
            .then(response => {
                console.log("Rerun response received:", response.data.updated_workflow);
                setEditedWorkflow(prevWorkflow => ({
                    ...prevWorkflow,
                    value: response.data.updated_workflow
                }));
                alert('Parameter ranges updated, please check the suggested workflow.');
            })
            .catch(error => {
                console.error('Error starting rerun:', error);
                alert('Error starting rerun');
            });
    };
    

    return (
        <div>
            <h1>Analysis Page</h1>

            <BaseWorkflowSelector 
                baseWorkflows={baseWorkflows}
                selectedBaseWorkflow={selectedBaseWorkflow}
                onSelect={handleBaseWorkflowSelect}
            />

            <GroupTimestampSelector 
                runWorkflows={runWorkflows}
                selectedGroupTimestamp={selectedGroupTimestamp}
                onSelect={handleGroupTimestampSelect}
            />

            <h2>Good vs Bad per Run</h2>
            <QualityAssessmentChart 
                qualityAssessments={qualityAssessments}
                getGoodBadCounts={getGoodBadCounts}
            />

            <h2>Good vs Bad per Parameter</h2>
            <ParameterChart 
                getParameterCounts={getParameterCounts}
            />

            {selectedBaseWorkflow && (
                <div>
                    <WorkflowEditorComponent 
                        workflow={editedWorkflow}
                        onSave={handleSaveWorkflow}
                    />
                </div>
            )}

            <div>
                <label>Number of Runs</label>
                <input
                    type="number"
                    value={numRuns}
                    onChange={e => setNumRuns(e.target.value)}
                    min="1"
                    style={{ marginLeft: '10px', marginTop:'10px' }}
                />
            </div>
            <div style={{ marginTop: '20px' }}>
                <label>Set Threshold for good outputs / total outputs</label>
                    <input 
                        type="number" 
                        value={threshold} 
                        onChange={(e) => setThreshold(parseFloat(e.target.value))}
                        step="0.01" 
                        min="0" 
                        max="1" 
                        style={{ marginLeft: '10px' }}
                    />
                <button onClick={handleStartRun} style={{ marginLeft: '20px' }}>Start Run</button>
                <button onClick={handleUpdateWorkflow} style={{ marginLeft: '20px' }}>Adjust sampling values</button>
            </div>
        </div>
    );
};

export default AnalysisPage;
