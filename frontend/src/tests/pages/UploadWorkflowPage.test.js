import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import UploadWorkflowPage from '../../pages/UploadWorkflowPage';
import axios from 'axios';

jest.mock('axios');

jest.mock('../../components/WorkflowViewerComponent', () => (props) => {
  return (
    <div data-testid="workflow-viewer">
      <button onClick={() => props.onSelect({ _id: 'wf1', value: { foo: 'bar' } })}>
        Select Workflow
      </button>
    </div>
  );
});

jest.mock('../../components/WorkflowEditorComponent', () => (props) => {
  return (
    <div data-testid="workflow-editor">
      <h2>{props.workflow ? 'Edit Workflow' : 'Create Workflow'}</h2>
      <button onClick={() => props.onSave(props.workflow ? { _id: 'wf1', value: { foo: 'bar' } } : { value: { foo: 'bar' } })}>
        Save Workflow
      </button>
    </div>
  );
});

describe('UploadWorkflowPage', () => {
  beforeEach(() => {
    axios.post.mockResolvedValue({ data: {} });
    window.alert = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders Home Page heading and Create New Workflow button', () => {
    render(<UploadWorkflowPage />);
    expect(screen.getByText(/Home Page/i)).toBeInTheDocument();
    expect(screen.getByText(/Create New Workflow/i)).toBeInTheDocument();
  });

  test('clicking "Create New Workflow" renders the editor for a new workflow', async () => {
    render(<UploadWorkflowPage />);
    
    fireEvent.click(screen.getByText(/Create New Workflow/i));
    
    await waitFor(() => {
      expect(screen.getByTestId('workflow-editor')).toBeInTheDocument();
    });
    
    expect(screen.getByText(/Create Workflow/i)).toBeInTheDocument();

    fireEvent.click(screen.getByText(/Save Workflow/i));
    
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        'http://localhost:5000/api/uploadWorkflow',
        { value: { foo: 'bar' } }
      );
    });
    
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Workflow saved successfully');
    });
  });

  test('selecting an existing workflow renders the editor for editing and saving updates it', async () => {
    render(<UploadWorkflowPage />);
    
    fireEvent.click(screen.getByText(/Select Workflow/i));
    
    await waitFor(() => {
      expect(screen.getByTestId('workflow-editor')).toBeInTheDocument();
    });
    
    expect(screen.getByText(/Edit Workflow/i)).toBeInTheDocument();
    
    fireEvent.click(screen.getByText(/Save Workflow/i));
    
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        'http://localhost:5000/api/updateWorkflow/wf1',
        { _id: 'wf1', value: { foo: 'bar' } }
      );
    });
    
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Workflow saved successfully');
    });
  });
});
