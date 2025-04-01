import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import CategorisationComponent from '../../components/CategorisationComponent';
import axios from 'axios';

jest.mock('axios');

describe('CategorisationComponent', () => {
  const sampleOutputs = [
    {
      paths: ['path/to/image1.png', 'path/to/image2.png'],
      run_workflow_id: 'rw1',
    },
  ];

  const fakeBlob = new Blob(['dummy content'], { type: 'image/png' });
  const fakeUrl = 'blob:http://localhost/fake';

  beforeEach(() => {
    axios.post.mockResolvedValue({ data: fakeBlob });
    URL.createObjectURL = jest.fn(() => fakeUrl);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders Outputs heading', () => {
    render(<CategorisationComponent outputs={[]} resetImageSelection={false} />);
    expect(screen.getByText(/Outputs/i)).toBeInTheDocument();
  });

  test('fetches output URLs and displays images', async () => {
    render(<CategorisationComponent outputs={sampleOutputs} resetImageSelection={false} />);

    await waitFor(() => {
      const imgs = screen.getAllByRole('img');
      expect(imgs.length).toBeGreaterThan(0);
    });

    const imgs = screen.getAllByRole('img');
    imgs.forEach((img) => {
      expect(img).toHaveAttribute('src', fakeUrl);
    });
  });

  test('resets selected image when resetImageSelection changes', async () => {
    const { rerender } = render(
      <CategorisationComponent outputs={sampleOutputs} resetImageSelection={false} />
    );

    await waitFor(() => {
      const imgs = screen.getAllByRole('img');
      expect(imgs.length).toBeGreaterThan(0);
    });

    const imgs = screen.getAllByRole('img');
    fireEvent.click(imgs[0]);

    expect(screen.getByText(/Selected Image/i)).toBeInTheDocument();

    rerender(<CategorisationComponent outputs={sampleOutputs} resetImageSelection={true} />);
    await waitFor(() => {
      expect(screen.queryByText(/Selected Image/i)).toBeNull();
    });
  });

  test('does not render quality buttons if no image is selected', async () => {
    render(<CategorisationComponent outputs={sampleOutputs} resetImageSelection={false} />);

    await waitFor(() => {
      const imgs = screen.getAllByRole('img');
      expect(imgs.length).toBeGreaterThan(0);
    });

    expect(screen.queryByRole('button', { name: /Good/i })).toBeNull();
    expect(screen.queryByRole('button', { name: /Bad/i })).toBeNull();
  });

  test('calls axios.post on quality assessment when an image is selected', async () => {
    window.alert = jest.fn();
    render(<CategorisationComponent outputs={sampleOutputs} resetImageSelection={false} />);

    await waitFor(() => {
      const imgs = screen.getAllByRole('img');
      expect(imgs.length).toBeGreaterThan(0);
    });

    const imgs = screen.getAllByRole('img');
    fireEvent.click(imgs[0]);

    const goodButton = screen.getByRole('button', { name: /Good/i });
    fireEvent.click(goodButton);

    await waitFor(() => {
      expect(axios.post).toHaveBeenCalledWith(
        'http://127.0.0.1:5000/api/qualityCheck',
        {
          run_workflow_id: 'rw1',
          path: 'path/to/image1.png',
          quality_assessment: 'good',
        }
      );
    });
    expect(window.alert).toHaveBeenCalledWith('Image has been rated as good');
  });
});
