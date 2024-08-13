import React, { useState, useEffect } from 'react';

const WorkflowEditorComponent = ({ workflow, onSave }) => {
    const [jsonString, setJsonString] = useState('');

    useEffect(() => {
        if (workflow) {
            setJsonString(JSON.stringify(workflow.value, null, 2));
        } else {
            setJsonString('');
        }
    }, [workflow]);

    const handleJsonChange = (event) => {
        setJsonString(event.target.value);
    };

    const handleSave = () => {
        try {
            const json = JSON.parse(jsonString);
            onSave({ ...workflow, value: json });
            alert('JSON saved successfully');
        } catch (error) {
            console.error('Invalid JSON format');
            alert('Invalid JSON format');
        }
    };

    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        const reader = new FileReader();

        reader.onload = (e) => {
            try {
                const json = JSON.parse(e.target.result);
                setJsonString(JSON.stringify(json, null, 2));
            } catch (error) {
                console.error('Invalid JSON file');
                alert('Invalid JSON file');
            }
        };

        if (file) {
            reader.readAsText(file);
        }
    };

    return (
        <div>
            <h1>{workflow ? 'Edit Workflow' : 'Create Workflow'}</h1>
            <input type="file" accept=".json" onChange={handleFileUpload} />
            <textarea
                value={jsonString}
                onChange={handleJsonChange}
                rows="20"
                cols="80"
                style={{ marginTop: '20px', fontFamily: 'monospace' }}
            />
            <br />
            <button onClick={handleSave} style={{ marginTop: '10px' }}>
                Save
            </button>
        </div>
    );
};

export default WorkflowEditorComponent;
