import React, { useState, useEffect } from 'react';
import ReactJson from 'react-json-view';
import './styles/WorkflowEditorComponent.css';

const WorkflowEditorComponent = ({ workflow, onSave }) => {
  const [jsonData, setJsonData] = useState({});

  useEffect(() => {
    if (workflow) {
      setJsonData(workflow.value);
    } else {
      setJsonData({});
    }
  }, [workflow]);

  const handleEdit = (edit) => {
    setJsonData(edit.updated_src);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target.result);
        setJsonData(json);
      } catch (error) {
        console.error('Invalid JSON file');
        alert('Invalid JSON file');
      }
    };

    if (file) {
      reader.readAsText(file);
    }
  };

  const handleSave = () => {
    try {
      onSave({ ...workflow, value: jsonData });
      alert('JSON updated locally; save to database via your existing mechanism if needed.');
    } catch (error) {
      console.error('Error saving JSON');
      alert('Error saving JSON');
    }
  };

  return (
    <div className="editor-container">
      <h2>{workflow ? 'Edit Workflow' : 'Create Workflow'}</h2>
      <div className="editor-toolbar">
        <input type="file" accept=".json" onChange={handleFileUpload} />
        <button onClick={handleSave}>Save</button>
      </div>
      <div className="json-editor">
        <ReactJson 
            key={JSON.stringify(jsonData)}
            src={jsonData}
            onEdit={handleEdit}
            onAdd={handleEdit}
            onDelete={handleEdit}
            name={null}
            displayDataTypes={false}
            displayObjectSize={false}
            indentWidth={2}
            collapsed={false}
        />
      </div>
    </div>
  );
};

export default WorkflowEditorComponent;
