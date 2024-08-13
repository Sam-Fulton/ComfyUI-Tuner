import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import './App.css';
import UploadWorkflowPage from './pages/UploadWorkflowPage';
import CategorisationPage from './pages/CategorisationPage';
import RunPage from './pages/RunPage';
import AnalysisPage from './pages/AnalysisPage';

const App = () => {
    return (
        <Router>
            <div>
                <nav>
                    <Link to="/">Upload Workflow</Link>
                    <Link to="/categorisation" style={{ marginLeft: '10px' }}>Categorisation Page</Link>
                    <Link to="/run" style={{ marginLeft: '10px' }}>Run Page</Link>
                    <Link to="/analysis" style={{ marginLeft: '10px' }}>analysis Page</Link>
                </nav>
                <Routes>
                    <Route path="/" element={<UploadWorkflowPage />} />
                    <Route path="/categorisation" element={<CategorisationPage />} />
                    <Route path="/run" element={<RunPage />} />
                    <Route path="/analysis" element={<AnalysisPage />} />
                </Routes>
            </div>
        </Router>
    );
};

export default App;
