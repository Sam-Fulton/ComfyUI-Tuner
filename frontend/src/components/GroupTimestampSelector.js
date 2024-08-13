import React from 'react';

const GroupTimestampSelector = ({ runWorkflows, selectedGroupTimestamp, onSelect }) => {
    return (
        <div>
            <h2>Select a Group Timestamp</h2>
            {runWorkflows.length > 0 && (
                <select value={selectedGroupTimestamp} onChange={onSelect}>
                    <option value="" disabled>Select a Group Timestamp</option>
                    {[...new Set(runWorkflows.map(workflow => workflow.group_timestamp))].map(timestamp => (
                        <option key={timestamp} value={timestamp}>
                            {new Date(timestamp * 1000).toLocaleString()}
                        </option>
                    ))}
                </select>
            )}
        </div>
    );
};

export default GroupTimestampSelector;
