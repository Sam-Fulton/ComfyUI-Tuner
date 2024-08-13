import React from 'react';

const BaseWorkflowSelector = ({ baseWorkflows, selectedBaseWorkflow, onSelect }) => {
    return (
        <div>
            <h2>Select a Base Workflow</h2>
            <select value={selectedBaseWorkflow ? selectedBaseWorkflow._id : ''} onChange={onSelect}>
                <option value="" disabled>Select a Base Workflow</option>
                {baseWorkflows.map(workflow => (
                    <option key={workflow._id} value={workflow._id}>
                        {workflow.name || workflow._id}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default BaseWorkflowSelector;
