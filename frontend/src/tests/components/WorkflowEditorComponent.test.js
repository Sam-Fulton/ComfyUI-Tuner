import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import WorkflowEditorComponent from '../../components/WorkflowEditorComponent';

describe('WorkflowEditorComponent', () => {
  const onSaveMock = jest.fn();
  const sampleWorkflow = { _id: 'wf1', value: { foo: 'bar' } };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders heading based on workflow prop', () => {
    const { rerender } = render(
      <WorkflowEditorComponent workflow={sampleWorkflow} onSave={onSaveMock} />
    );
    expect(screen.getByText(/Edit Workflow/i)).toBeInTheDocument();

    rerender(<WorkflowEditorComponent workflow={null} onSave={onSaveMock} />);
    expect(screen.getByText(/Create Workflow/i)).toBeInTheDocument();
  });

  test('handles valid JSON file upload', async () => {
    const fileContent = '{"newKey": "newValue"}';
    const file = new File([fileContent], 'test.json', { type: 'application/json' });
    
    const fileReaderMock = {
      readAsText: jest.fn(),
      onload: null,
      result: fileContent,
    };
    const fileReaderSpy = jest.spyOn(window, 'FileReader').mockImplementation(() => fileReaderMock);

    const { container } = render(
      <WorkflowEditorComponent workflow={sampleWorkflow} onSave={onSaveMock} />
    );
    const fileInput = container.querySelector('input[type="file"]');
    expect(fileInput).toBeInTheDocument();

    fireEvent.change(fileInput, { target: { files: [file] } });
    fileReaderMock.onload({ target: { result: fileContent } });

    await waitFor(() => {
      expect(screen.getByText(/newKey/i)).toBeInTheDocument();
    });

    fileReaderSpy.mockRestore();
  });

  test('calls onSave when Save button is clicked', async () => {
    window.alert = jest.fn();
    render(
      <WorkflowEditorComponent workflow={sampleWorkflow} onSave={onSaveMock} />
    );
    
    const saveButton = screen.getByRole('button', { name: /Save/i });
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(onSaveMock).toHaveBeenCalledWith({ ...sampleWorkflow, value: sampleWorkflow.value });
    });
    expect(window.alert).toHaveBeenCalledWith(
      'JSON updated locally; save to database via your existing mechanism if needed.'
    );
  });

  test('alerts error on invalid JSON file upload', async () => {
    window.alert = jest.fn();
    const invalidContent = 'invalid json';
    const file = new File([invalidContent], 'invalid.json', { type: 'application/json' });
    
    const fileReaderMock = {
      readAsText: jest.fn(),
      onload: null,
      result: invalidContent,
    };
    const fileReaderSpy = jest.spyOn(window, 'FileReader').mockImplementation(() => fileReaderMock);

    const { container } = render(
      <WorkflowEditorComponent workflow={sampleWorkflow} onSave={onSaveMock} />
    );
    const fileInput = container.querySelector('input[type="file"]');
    fireEvent.change(fileInput, { target: { files: [file] } });
    fileReaderMock.onload({ target: { result: invalidContent } });

    await waitFor(() => {
      expect(window.alert).toHaveBeenCalledWith('Invalid JSON file');
    });
    fileReaderSpy.mockRestore();
  });
});
