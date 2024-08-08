from pymongo import MongoClient
from bson import ObjectId
import os

import os
from pymongo import MongoClient
from bson import ObjectId

def get_db():
    try:
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        client = MongoClient(mongo_uri)
        db = client['workflow_db']
        return db
    except Exception as e:
        print(f"An error occurred while connection to mongo: {e}")
        return None

def insert_run_workflow(db, workflow_data):
    workflow_collection = db['run_workflows']
    workflow_document = {'value': workflow_data}
    result = workflow_collection.insert_one(workflow_document)
    return str(result.inserted_id)

def find_run_workflow(db, run_workflow_id):
    workflow_collection = db['run_workflows']
    workflow_document = workflow_collection.find_one({'_id': ObjectId(run_workflow_id)})
    if workflow_document:
        return workflow_document.get('value')
    return None

def insert_base_workflow(db, workflow_data):
    workflow_collection = db['base_workflows']
    workflow_document = {'value': workflow_data}
    result = workflow_collection.insert_one(workflow_document)
    return str(result.inserted_id)

def find_base_workflow(db, base_workflow_id):
    workflow_collection = db['base_workflows']
    workflow_document = workflow_collection.find_one({'_id': ObjectId(base_workflow_id)})
    if workflow_document:
        return workflow_document.get('value')
    return None

def fetch_base_workflows(db):
    try:
        workflow_collection = db['base_workflows']
        workflows = []
        for workflow_document in workflow_collection.find():
            workflows.append(workflow_document)
        return workflows
    except Exception as e:
        print(f"An error occurred while fetching workflows: {e}")
        return []

def fetch_run_workflows(db):
    workflow_collection = db['run_workflows']
    workflows = []
    for workflow_document in workflow_collection.find():
        workflows.append(workflow_document)
    return workflows

def insert_quality_review(db, quality_assessment):
    quality_assessment_collection = db['quality_assessment']
    result = quality_assessment_collection.insert_one({
        "run_workflow_id": quality_assessment.run_workflow_id,
        "quality_assessment": quality_assessment.quality_assessment,
        "path": quality_assessment.path
    })
    return str(result.inserted_id)

def find_quality_assessment(db, quality_assessment_id):
    quality_assessment_collection = db['quality_assessment']
    quality_assessment = quality_assessment_collection.find_one({'_id': ObjectId(quality_assessment_id)})
    if quality_assessment:
        quality_assessment['_id'] = str(quality_assessment['_id'])
    return quality_assessment

def find_quality_assessments_by_run_workflow_id(db, run_workflow_id):
    quality_assessment_collection = db['quality_assessment']
    quality_assessments = list(quality_assessment_collection.find({'run_workflow_id': run_workflow_id}))
    for qa in quality_assessments:
        qa['_id'] = str(qa['_id'])
    return quality_assessments

def insert_outputs(db, outputs):
    outputs_collection = db['outputs']
    result = outputs_collection.insert_one({
        "run_workflow_id": outputs.run_workflow_id,
        "paths": outputs.paths
    })
    return str(result.inserted_id)

def find_outputs(db, outputs_id):
    outputs_collection = db['outputs']
    outputs = outputs_collection.find_one({'_id': ObjectId(outputs_id)})
    if outputs:
        outputs['_id'] = str(outputs['_id'])
    return outputs

def find_outputs_by_run_workflow_id(db, run_workflow_id):
    outputs_collection = db['outputs']
    outputs_cursor = outputs_collection.find({'run_workflow_id': run_workflow_id})
    outputs = []
    for output in outputs_cursor:
        output['_id'] = str(output['_id'])
        outputs.append(output)
    return outputs
