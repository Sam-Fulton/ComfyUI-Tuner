import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import GroupTimestampSelector from '../../components/GroupTimestampSelector';

describe('GroupTimestampSelector', () => {
  const sampleWorkflows = [
    { group_timestamp: 1633046400 },
    { group_timestamp: 1633046400 },
    { group_timestamp: 1633132800 }
  ];

  test('renders heading and no select when runWorkflows is empty', () => {
    render(
      <GroupTimestampSelector
        runWorkflows={[]}
        selectedGroupTimestamp=""
        onSelect={jest.fn()}
      />
    );

    expect(screen.getByText(/Select a Group Timestamp/i)).toBeInTheDocument();
    expect(screen.queryByRole('combobox')).toBeNull();
  });

  test('renders a select with correct options when workflows provided', () => {
    render(
      <GroupTimestampSelector
        runWorkflows={sampleWorkflows}
        selectedGroupTimestamp=""
        onSelect={jest.fn()}
      />
    );

    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();

    const options = screen.getAllByRole('option');
    expect(options).toHaveLength(3);

    const formattedDate1 = new Date(sampleWorkflows[0].group_timestamp * 1000).toLocaleString();
    const formattedDate2 = new Date(sampleWorkflows[2].group_timestamp * 1000).toLocaleString();
    expect(screen.getByText(formattedDate1)).toBeInTheDocument();
    expect(screen.getByText(formattedDate2)).toBeInTheDocument();
  });

  test('calls onSelect when a new option is selected', () => {
    const onSelectMock = jest.fn();
    render(
      <GroupTimestampSelector
        runWorkflows={sampleWorkflows}
        selectedGroupTimestamp=""
        onSelect={onSelectMock}
      />
    );

    const select = screen.getByRole('combobox');
    fireEvent.change(select, { target: { value: sampleWorkflows[2].group_timestamp } });
    expect(onSelectMock).toHaveBeenCalled();
  });
});
