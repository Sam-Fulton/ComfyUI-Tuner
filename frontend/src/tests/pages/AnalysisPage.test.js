import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import AnalysisPage from '../../pages/AnalysisPage';
import axios from 'axios';

jest.mock('axios');

jest.mock('../../components/BaseWorkflowSelector', () => (props) => (
  <select
    data-testid="base-workflow-selector"
    value={props.selectedBaseWorkflow ? props.selectedBaseWorkflow._id : ""}
    onChange={props.onSelect}
  >
    {props.baseWorkflows &&
      props.baseWorkflows.map((wf) => (
        <option key={wf._id} value={wf._id}>
          {wf._id}
        </option>
      ))}
  </select>
));

jest.mock('../../components/GroupTimestampSelector', () => (props) => (
  <select data-testid="group-timestamp-selector" onChange={props.onSelect}>
    <option value="123456">123456</option>
  </select>
));

jest.mock('../../components/QualityAssessmentChart', () => () => (
  <div data-testid="quality-chart">Quality Chart</div>
));

jest.mock('../../components/ParameterChart', () => () => (
  <div data-testid="parameter-chart">Parameter Chart</div>
));

jest.mock('../../components/WorkflowEditorComponent', () => (props) => (
  <div data-testid="workflow-editor">
    <button onClick={() => props.onSave({ value: { edited: true } })}>
      Save Workflow
    </button>
  </div>
));

describe('AnalysisPage', () => {
  const sampleBaseWorkflows = [
    { _id: 'workflow1', value: { key: 'initial' } },
    { _id: 'workflow2', value: { key: 'initial2' } },
  ];
  const sampleRunWorkflows = [
    { _id: 'run1', group_timestamp: '123456', value: {} },
    { _id: 'run2', group_timestamp: '123456', value: {} },
  ];
  const sampleQualityAssessments = [
    { run_workflow_id: 'run1', quality_assessment: 'good' },
    { run_workflow_id: 'run2', quality_assessment: 'bad' },
  ];

  beforeEach(() => {
    axios.get.mockResolvedValue({
      data: { workflows: sampleBaseWorkflows },
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('fetches base workflows on mount and renders BaseWorkflowSelector', async () => {
    render(<AnalysisPage />);

    await waitFor(() => {
      expect(screen.getByTestId('base-workflow-selector')).toBeInTheDocument();
    });

    await waitFor(() => {
      sampleBaseWorkflows.forEach((wf) => {
        expect(screen.getByRole('option', { name: wf._id })).toBeInTheDocument();
      });
    });
  });

  test('selecting a base workflow triggers fetching run workflows', async () => {
    axios.post.mockResolvedValueOnce({
      data: { run_workflows: sampleRunWorkflows },
    });

    render(<AnalysisPage />);

    await waitFor(() => {
      expect(screen.getByRole('option', { name: 'workflow1' })).toBeInTheDocument();
    });

    const baseSelect = screen.getByTestId('base-workflow-selector');
    fireEvent.change(baseSelect, { target: { value: 'workflow1' } });

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        'http://127.0.0.1:5000/api/getRunWorkflowsByBaseID',
        { base_workflow_id: 'workflow1' }
      );
    });
  });

  test('clicking "Start Run" sends payload to start run endpoint', async () => {
    axios.post.mockResolvedValueOnce({
      data: { run_workflows: sampleRunWorkflows },
    });
    axios.post.mockResolvedValueOnce({
      data: { message: 'Run Executed' },
    });

    render(<AnalysisPage />);

    await waitFor(() => {
      expect(screen.getByTestId('base-workflow-selector')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByRole('option', { name: 'workflow1' })).toBeInTheDocument();
    });

    const baseSelect = screen.getByTestId('base-workflow-selector');
    fireEvent.change(baseSelect, { target: { value: 'workflow1' } });

    const startRunButton = screen.getByRole('button', { name: /Start Run/i });
    fireEvent.click(startRunButton);

    await waitFor(() => {
        expect(axios.post).toHaveBeenCalledWith(
          'http://127.0.0.1:5000/api/startRun',
          expect.objectContaining({
            base_workflow: expect.anything(),
            base_workflow_id: 'workflow1',
            num_runs: expect.any(Number)
          })
        );
      });      
  });

  test('WorkflowEditorComponent onSave updates the edited workflow', async () => {
    axios.post.mockResolvedValueOnce({
      data: { run_workflows: sampleRunWorkflows },
    });

    render(<AnalysisPage />);

    await waitFor(() => {
      expect(screen.getByRole('option', { name: 'workflow1' })).toBeInTheDocument();
    });

    const baseSelect = screen.getByTestId('base-workflow-selector');
    fireEvent.change(baseSelect, { target: { value: 'workflow1' } });

    await waitFor(() => {
      expect(screen.getByTestId('workflow-editor')).toBeInTheDocument();
    });
    
    const saveWorkflowButton = screen.getByRole('button', { name: /Save Workflow/i });
    fireEvent.click(saveWorkflowButton);

    expect(screen.getByTestId('workflow-editor')).toBeInTheDocument();
  });
});
