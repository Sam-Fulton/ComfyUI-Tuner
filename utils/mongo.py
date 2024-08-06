from pymongo import MongoClient
from bson import ObjectId
import os
from outputs import Outputs
from qualityAssessment import QualityAssessment

def get_db():
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_uri)
    db = client['workflow_db']
    return db

def insert_workflow(db, workflow_data):
    workflow_collection = db['workflows']
    result = workflow_collection.insert_one(workflow_data)
    return result.inserted_id

def find_workflow(db, workflow_id):
    workflow_collection = db['workflows']
    workflow = workflow_collection.find_one({'_id': workflow_id})
    return workflow

def insert_quality_review(db, quality_assessment: QualityAssessment):
    quality_assessment_collection = db['quality_assessment']
    result = quality_assessment_collection.insert_one({
        "workflow_id": quality_assessment.workflow_id,
        "quality_assessment": quality_assessment.quality_assessment,
        "path": quality_assessment.path
    })
    return result.inserted_id

def find_quality_assessment(db, quality_assessment_id):
    quality_assessment_collection = db['quality_assessment']
    quality_assessment = quality_assessment_collection.find_one({'_id': ObjectId(quality_assessment_id)})
    return quality_assessment

def insert_outputs(db, outputs:Outputs):
    outputs_collection = db['outputs']
    result = outputs_collection.insert_one({
        "workflow_id": outputs.workflow_id,
        "paths": outputs.paths
    })
    return result

def find_outputs(db, outputs_id):
    outputs_collection = db['outputs']
    outputs = outputs_collection.find_one({'_id': ObjectId(outputs_id)})
    return outputs

def find_outputs_by_workflow_id(db, workflow_id):
    outputs_collection = db['outputs']
    outputs_cursor = outputs_collection.find({'workflow_id': workflow_id})
    return [Outputs(workflow_id=output['workflow_id'], paths=output['paths']) for output in outputs_cursor]