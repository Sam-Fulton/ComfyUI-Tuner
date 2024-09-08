# ComfyUI-Tuner

**ComfyUI-Tuner** is a full-stack application designed to interface with **ComfyUI**, a powerful tool for Stable Diffusion image generation. The tool automates hyperparameter tuning by providing random sampling of parameters and allows users to manage workflows, review, categorise, and re-run them efficiently. It streamlines the process of finding optimal parameters for high-quality image generation.

## Features

### 1. Workflow Management
- **Upload Workflows**: Easily upload Stable Diffusion workflows (in API format) through the app. These workflows can be downloaded from ComfyUI when in developer mode.
- **Run Workflows**: Execute workflows with random sampling of key hyperparameters such as guidance scale, steps, and seed.
- **Base and Run Workflows**: Base workflows act as templates, while run workflows represent executions with randomly sampled parameters.

### 2. Output Management
- **Save Outputs**: Each workflow run generates outputs that are saved and linked to a specific run ID.
- **Categorise Outputs**: Organise generated outputs for easier comparison and analysis.

### 3. Auto-Tuning
- **Hyperparameter Sampling**: Automatically sample and adjust parameters across multiple runs to optimise image generation.
- **Re-run Workflows**: Refine parameter ranges based on previous results and re-run workflows for improved outcomes.

### 4. Quality Assessment
- **Manual Image Rating**: Users can manually rate image outputs based on quality, helping to track and analyse the best-performing parameter sets.

### 5. Categorisation and Comparison of Images
- **Categorisation Component**: Allows users to organise, sort, and categorise image outputs based on specific workflows.

### 6. User Interface
- **React Frontend**: A modern, user-friendly interface built using React.js for seamless interaction with workflow uploads, output analysis, and more.
- **Workflow Selection**: Users can select workflows by timestamp, view run histories, and analyse outputs across multiple runs.

## Getting Started

### Clone The Repository


`git clone https://github.com/Sam-Fulton/ComfyUI-Tuner.git`


### Docker Approach (Recommended)

Ensure that ComfyUI is properly set up on your machine. Adjust the ComfyUI volume location so it can bind correctly with the backend container.

To start the app, simply run:

 `docker-compose up --build`

This assumes Docker is already installed on your machine.

### Manual Launching

1. Install the backend requirements in the 'app' directory:

`pip install -r ./app/requirements.txt`


2. Install npm dependencies for the frontend:

`cd ./frontend`

`npm install --legacy-peer-deps`


3. In a terminal, start the frontend server:

`npm start`

4. In a separate terminal, start the Flask backend server:

`python ./app/app.py`


#### MongoDB Setup

You will also need to run your own MongoDB server and pass the MongoDB address to the backend application for proper data storage.