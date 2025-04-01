import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CategorisationPage from '../../pages/CategorisationPage';
import axios from 'axios';

jest.mock('axios');

describe('CategorisationPage', () => {
  const sampleBaseWorkflows = [
    { _id: 'b1', name: 'Base Workflow 1' },
    { _id: 'b2', name: 'Base Workflow 2' },
  ];

  const sampleRunWorkflows = [
    { _id: 'r1', group_timestamp: '1633046400' },
    { _id: 'r2', group_timestamp: '1633046400' },
  ];

  beforeEach(() => {
    axios.get.mockResolvedValue({ data: { workflows: sampleBaseWorkflows } });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('selecting a base workflow triggers fetching run workflows and renders GroupTimestampSelector', async () => {
    axios.post.mockResolvedValueOnce({ data: { run_workflows: sampleRunWorkflows } });

    render(<CategorisationPage />);

    await waitFor(() => {
      const baseSelect = screen.getByRole('combobox');
      expect(baseSelect.options.length).toBeGreaterThan(1);
    });

    const baseSelect = screen.getByRole('combobox');
    userEvent.selectOptions(
      baseSelect,
      screen.getByRole('option', { name: /Base Workflow 1/i })
    );

    expect(baseSelect.value).toBe('b1');

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        'http://127.0.0.1:5000/api/getRunWorkflowsByBaseID',
        { base_workflow_id: 'b1' }
      );
    });
  });
});
