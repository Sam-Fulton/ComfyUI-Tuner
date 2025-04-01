import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import BaseWorkflowSelector from '../../components/BaseWorkflowSelector';

describe('BaseWorkflowSelector', () => {
  const sampleWorkflows = [
    { _id: 'wf1', name: 'Workflow 1' },
    { _id: 'wf2', name: 'Workflow 2' },
  ];

  test('renders heading and placeholder option', () => {
    render(
      <BaseWorkflowSelector
        baseWorkflows={sampleWorkflows}
        selectedBaseWorkflow={null}
        onSelect={jest.fn()}
      />
    );

    const heading = screen.getByRole('heading', { name: /Select a Base Workflow/i });
    expect(heading).toBeInTheDocument();

    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();

    const placeholderOption = screen.getByRole('option', { name: 'Select a Base Workflow' });
    expect(placeholderOption).toBeInTheDocument();
  });

  test('renders options from baseWorkflows', () => {
    render(
      <BaseWorkflowSelector
        baseWorkflows={sampleWorkflows}
        selectedBaseWorkflow={null}
        onSelect={jest.fn()}
      />
    );

    sampleWorkflows.forEach(workflow => {
      expect(screen.getByRole('option', { name: workflow.name })).toBeInTheDocument();
    });
  });

  test('calls onSelect when option is changed', () => {
    const onSelectMock = jest.fn();
    render(
      <BaseWorkflowSelector
        baseWorkflows={sampleWorkflows}
        selectedBaseWorkflow={null}
        onSelect={onSelectMock}
      />
    );

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: sampleWorkflows[0]._id } });
    expect(onSelectMock).toHaveBeenCalled();
  });
});
