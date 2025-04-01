import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import RunPage from '../../pages/RunPage';
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
      <h2>Edit Workflow</h2>
      <button onClick={() => props.onSave({ _id: 'wf1', value: { foo: 'baz' } })}>
        Save Workflow
      </button>
    </div>
  );
});

describe('RunPage', () => {
  beforeEach(() => {
    axios.post.mockResolvedValue({ data: {} });
    window.alert = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders Run Page heading and initial components', () => {
    render(<RunPage />);
    expect(screen.getByText(/Run Page/i)).toBeInTheDocument();
    expect(screen.getByTestId('workflow-viewer')).toBeInTheDocument();
    expect(screen.queryByTestId('workflow-editor')).toBeNull();
  });

  test('selects a workflow and displays the editor', async () => {
    render(<RunPage />);
    fireEvent.click(screen.getByText(/Select Workflow/i));
    await waitFor(() => {
      expect(screen.getByTestId('workflow-editor')).toBeInTheDocument();
    });
  });

  test('updates number of runs and starts a run with the correct payload', async () => {
    render(<RunPage />);
    fireEvent.click(screen.getByText(/Select Workflow/i));
    await waitFor(() => {
      expect(screen.getByTestId('workflow-editor')).toBeInTheDocument();
    });
    
    const numRunsInput = screen.getByRole('spinbutton');
    fireEvent.change(numRunsInput, { target: { value: '3' } });
    expect(numRunsInput.value).toBe('3');
    
    const startRunButton = screen.getByText(/Start Run/i);
    fireEvent.click(startRunButton);
    
    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        'http://127.0.0.1:5000/api/startRun',
        {
          base_workflow: { foo: 'bar' },
          num_runs: '3',
          base_workflow_id: 'wf1'
        }
      );
    });
    
    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Run started successfully');
    });
  });
});
