import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import WorkflowViewerComponent from '../../components/WorkflowViewerComponent';
import axios from 'axios';

jest.mock('axios');

describe('WorkflowViewerComponent', () => {
  const sampleWorkflows = [
    { _id: 'workflow1' },
    { _id: 'workflow2' },
  ];

  beforeEach(() => {
    axios.get.mockResolvedValue({ data: { workflows: sampleWorkflows } });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('fetches workflows and renders options', async () => {
    render(<WorkflowViewerComponent onSelect={jest.fn()} resetSelection={false} />);
    
    await waitFor(() => {
      const options = screen.getAllByRole('option');
      expect(options).toHaveLength(3);
    });

    sampleWorkflows.forEach(workflow => {
      expect(screen.getByRole('option', { name: workflow._id })).toBeInTheDocument();
    });
  });

  test('calls onSelect with the selected workflow when selection changes', async () => {
    const onSelectMock = jest.fn();
    render(<WorkflowViewerComponent onSelect={onSelectMock} resetSelection={false} />);
    
    await waitFor(() => {
      const options = screen.getAllByRole('option');
      expect(options).toHaveLength(3);
    });
    
    const select = screen.getByRole('combobox');
    await userEvent.selectOptions(select, 'workflow1');
    
    expect(onSelectMock).toHaveBeenCalledWith({ _id: 'workflow1' });
    expect(select.value).toBe('workflow1');
  });
  test('resets selected workflow when resetSelection becomes true', async () => {
    const onSelectMock = jest.fn();
    const { rerender } = render(
      <WorkflowViewerComponent onSelect={onSelectMock} resetSelection={false} />
    );
  
    await waitFor(() => {
      expect(screen.getAllByRole('option')).toHaveLength(3);
    });
    
    const select = screen.getByRole('combobox');
    await userEvent.selectOptions(select, 'workflow1');
    expect(select.value).toBe('workflow1');
    
    rerender(<WorkflowViewerComponent onSelect={onSelectMock} resetSelection={true} />);
    await waitFor(() => {
      expect(select.value).toBe('');
    });
  });
});
