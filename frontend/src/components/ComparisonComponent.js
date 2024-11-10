import React from 'react';

const ComparisonComponent = ({ image1, image2, onCompare }) => {
    return (
        <div>
            <h2>Compare the Images</h2>
            <div style={{ display: 'flex', justifyContent: 'space-around' }}>
                {/* Image 1 */}
                <div style={{ textAlign: 'center' }}>
                    <img src={image1.path} alt="Image 1" style={{ maxWidth: '300px', maxHeight: '300px' }} />
                    <div>
                        <button onClick={() => onCompare('image1')}>Select Image 1</button>
                    </div>
                </div>

                {/* Image 2 */}
                <div style={{ textAlign: 'center' }}>
                    <img src={image2.path} alt="Image 2" style={{ maxWidth: '300px', maxHeight: '300px' }} />
                    <div>
                        <button onClick={() => onCompare('image2')}>Select Image 2</button>
                    </div>
                </div>
            </div>

            <div style={{ textAlign: 'center', marginTop: '20px' }}>
                <button onClick={() => onCompare('draw')}>Both are Equal</button>
            </div>
        </div>
    );
};

export default ComparisonComponent;
