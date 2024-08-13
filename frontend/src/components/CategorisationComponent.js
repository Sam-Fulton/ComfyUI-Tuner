import React, { useState, useEffect } from 'react';
import axios from 'axios';

const CategorisationComponent = ({ outputs, resetImageSelection }) => {
    const [outputUrls, setOutputUrls] = useState([]);
    const [selectedImage, setSelectedImage] = useState(null);

    useEffect(() => {
        const fetchOutputUrls = async () => {
            const urls = await Promise.all(outputs.flatMap(output => output.paths.map(fetchOutputFile)));
            setOutputUrls(urls);
        };

        if (outputs.length > 0) {
            fetchOutputUrls();
        }
    }, [outputs]);

    useEffect(() => {
        if (resetImageSelection) {
            setSelectedImage(null); // Reset selected image when instructed
        }
    }, [resetImageSelection]);

    const fetchOutputFile = async (path) => {
        try {
            const response = await axios.post('http://127.0.0.1:5000/api/outputs', { path }, { responseType: 'blob' });
            const fileURL = URL.createObjectURL(new Blob([response.data]));
            return { url: fileURL, path: path, runWorkflowId: outputs[0].run_workflow_id };
        } catch (error) {
            console.error('Error fetching output file:', error);
            return null;
        }
    };

    const handleQualityAssessment = (assessment) => {
        if (!selectedImage) {
            alert("Please select an image first.");
            return;
        }

        const payload = {
            run_workflow_id: selectedImage.runWorkflowId,
            path: selectedImage.path,
            quality_assessment: assessment,
        };

        axios.post('http://127.0.0.1:5000/api/qualityCheck', payload)
            .then(response => {
                alert(`Image has been rated as ${assessment}`);
            })
            .catch(error => {
                console.error('Error submitting quality assessment:', error);
                alert('Error submitting quality assessment');
            });
    };

    const handleImageClick = (image) => {
        setSelectedImage(image);
    };

    return (
        <div>
            <h2>Outputs</h2>
            <div style={{ display: 'flex', overflowX: 'auto', gap: '10px', paddingBottom: '10px' }}>
                {outputUrls.map((image, index) => (
                    <img
                        key={index}
                        src={image.url}
                        alt="output"
                        style={{
                            maxWidth: '150px',
                            maxHeight: '150px',
                            cursor: 'pointer',
                            border: selectedImage && selectedImage.path === image.path ? '3px solid blue' : 'none'
                        }}
                        onClick={() => handleImageClick(image)}
                    />
                ))}
            </div>
            {selectedImage && (
                <div>
                    <h3>Selected Image</h3>
                    <img
                        src={selectedImage.url}
                        alt="Selected output"
                        style={{
                            maxWidth: '100%',
                            height: 'auto',
                            marginBottom: '20px'
                        }}
                    />
                    <div>
                        <button onClick={() => handleQualityAssessment('good')} style={{ marginRight: '10px' }}>Good</button>
                        <button onClick={() => handleQualityAssessment('bad')}>Bad</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default CategorisationComponent;
