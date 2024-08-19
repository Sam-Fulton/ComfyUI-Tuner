import pytest
from unittest.mock import patch, MagicMock
from pymongo import errors
from bson import ObjectId

from app.utils import mongo

@pytest.fixture
def mock_db():
    with patch('app.utils.mongo.MongoClient') as mock_mongo_client:
        db = mock_mongo_client.return_value
        yield db

def test_get_db_success(mock_db):
    db = mongo.get_db()
    assert db is not None

def test_get_db_failure():
    with patch('app.utils.mongo.MongoClient', side_effect=Exception("Connection error")):
        db = mongo.get_db()
        assert db is None

def test_insert_run_workflow_success(mock_db):
    mock_db['run_workflows'].insert_one.return_value.inserted_id = ObjectId()
    workflow_id = mongo.insert_run_workflow(mock_db, {}, "base_id", "timestamp")
    assert workflow_id is not None

def test_insert_run_workflow_failure(mock_db):
    mock_db['run_workflows'].insert_one.side_effect = errors.PyMongoError("Insert error")
    workflow_id = mongo.insert_run_workflow(mock_db, {}, "base_id", "timestamp")
    assert workflow_id is None

def test_find_run_workflow_success(mock_db):
    valid_id = ObjectId()
    mock_db['run_workflows'].find_one.return_value = {'value': 'workflow_data'}
    workflow = mongo.find_run_workflow(mock_db, str(valid_id))
    assert workflow == 'workflow_data'

def test_find_run_workflow_failure(mock_db):
    mock_db['run_workflows'].find_one.side_effect = errors.PyMongoError("Find error")
    valid_id = ObjectId()
    workflow = mongo.find_run_workflow(mock_db, str(valid_id))
    assert workflow is None
    
def test_update_base_workflow_success(mock_db):
    mock_db['base_workflows'].update_one.return_value.matched_count = 1
    valid_id = ObjectId()
    result = mongo.update_base_workflow(mock_db, str(valid_id), {})
    assert result is True

def test_update_base_workflow_failure(mock_db):
    mock_db['base_workflows'].update_one.side_effect = errors.PyMongoError("Update error")
    valid_id = ObjectId()
    result = mongo.update_base_workflow(mock_db, str(valid_id), {})
    assert result is False

def test_fetch_base_workflows_success(mock_db):
    mock_db['base_workflows'].find.return_value = [{"workflow": "data"}]
    workflows = mongo.fetch_base_workflows(mock_db)
    assert len(workflows) == 1

def test_fetch_base_workflows_failure(mock_db):
    mock_db['base_workflows'].find.side_effect = errors.PyMongoError("Fetch error")
    workflows = mongo.fetch_base_workflows(mock_db)
    assert workflows == []

def test_insert_quality_review_success(mock_db):
    mock_db['quality_assessment'].insert_one.return_value.inserted_id = ObjectId()
    quality_assessment = MagicMock(run_workflow_id="run_id", quality_assessment="good", path="path")
    review_id = mongo.insert_quality_review(mock_db, quality_assessment)
    assert review_id is not None

def test_insert_quality_review_failure(mock_db):
    mock_db['quality_assessment'].insert_one.side_effect = errors.PyMongoError("Insert error")
    quality_assessment = MagicMock(run_workflow_id="run_id", quality_assessment="good", path="path")
    review_id = mongo.insert_quality_review(mock_db, quality_assessment)
    assert review_id is None

def test_find_quality_assessment_success(mock_db):
    valid_id = ObjectId()
    mock_db['quality_assessment'].find_one.return_value = {'_id': valid_id, 'quality_assessment': 'good'}
    
    assessment = mongo.find_quality_assessment(mock_db, str(valid_id))
    
    assert assessment is not None
    assert assessment['_id'] == str(valid_id)

def test_find_quality_assessment_failure(mock_db):
    mock_db['quality_assessment'].find_one.side_effect = errors.PyMongoError("Find error")
    valid_id = ObjectId()
    assessment = mongo.find_quality_assessment(mock_db, str(valid_id))
    assert assessment is None

def test_find_quality_assessments_by_run_workflow_id_success(mock_db):
    mock_db['quality_assessment'].find.return_value = [{'_id': ObjectId(), 'quality_assessment': 'good'}]
    assessments = mongo.find_quality_assessments_by_run_workflow_id(mock_db, "run_workflow_id")
    assert len(assessments) > 0
    assert '_id' in assessments[0]

def test_find_quality_assessments_by_run_workflow_id_failure(mock_db):
    mock_db['quality_assessment'].find.side_effect = errors.PyMongoError("Find error")
    assessments = mongo.find_quality_assessments_by_run_workflow_id(mock_db, "run_workflow_id")
    assert assessments == []

def test_find_quality_assessments_by_run_workflow_ids_success(mock_db):
    mock_db['quality_assessment'].find.return_value = [{'_id': ObjectId(), 'quality_assessment': 'good'}]
    assessments = mongo.find_quality_assessments_by_run_workflow_ids(mock_db, ["run_workflow_id_1", "run_workflow_id_2"])
    assert len(assessments) > 0
    assert '_id' in assessments[0]

def test_find_quality_assessments_by_run_workflow_ids_failure(mock_db):
    mock_db['quality_assessment'].find.side_effect = errors.PyMongoError("Find error")
    assessments = mongo.find_quality_assessments_by_run_workflow_ids(mock_db, ["run_workflow_id_1", "run_workflow_id_2"])
    assert assessments == []

def test_find_quality_assessments_by_run_workflow_id_path_success(mock_db):
    mock_db['quality_assessment'].find.return_value = [{'_id': ObjectId(), 'quality_assessment': 'good'}]
    assessments = mongo.find_quality_assessments_by_run_workflow_id_path(mock_db, "run_workflow_id", "some/path")
    assert len(assessments) > 0
    assert '_id' in assessments[0]

def test_find_quality_assessments_by_run_workflow_id_path_failure(mock_db):
    mock_db['quality_assessment'].find.side_effect = errors.PyMongoError("Find error")
    assessments = mongo.find_quality_assessments_by_run_workflow_id_path(mock_db, "run_workflow_id", "some/path")
    assert assessments == []

def test_update_quality_assessment_success(mock_db):
    mock_db['quality_assessment'].update_one.return_value.modified_count = 1
    result = mongo.update_quality_assessment(mock_db, "run_workflow_id", "some/path", "good")
    assert result is True

def test_update_quality_assessment_failure(mock_db):
    mock_db['quality_assessment'].update_one.side_effect = errors.PyMongoError("Update error")
    result = mongo.update_quality_assessment(mock_db, "run_workflow_id", "some/path", "good")
    assert result is False

def test_insert_outputs_success(mock_db):
    mock_db['outputs'].insert_one.return_value.inserted_id = ObjectId()
    outputs = MagicMock(run_workflow_id="run_workflow_id", paths=["path1", "path2"])
    result_id = mongo.insert_outputs(mock_db, outputs)
    assert result_id is not None

def test_insert_outputs_failure(mock_db):
    mock_db['outputs'].insert_one.side_effect = errors.PyMongoError("Insert error")
    outputs = MagicMock(run_workflow_id="run_workflow_id", paths=["path1", "path2"])
    result_id = mongo.insert_outputs(mock_db, outputs)
    assert result_id is None

def test_find_outputs_success(mock_db):
    valid_id = ObjectId()
    mock_db['outputs'].find_one.return_value = {'_id': valid_id, 'paths': ["path1", "path2"]}
    outputs = mongo.find_outputs(mock_db, str(valid_id))
    assert outputs is not None
    assert outputs['_id'] == str(valid_id)

def test_find_outputs_failure(mock_db):
    mock_db['outputs'].find_one.side_effect = errors.PyMongoError("Find error")
    valid_id = ObjectId()
    outputs = mongo.find_outputs(mock_db, str(valid_id))
    assert outputs is None

def test_find_outputs_by_run_workflow_id_success(mock_db):
    mock_db['outputs'].find.return_value = [{'_id': ObjectId(), 'paths': ["path1", "path2"]}]
    outputs = mongo.find_outputs_by_run_workflow_id(mock_db, "run_workflow_id")
    assert len(outputs) > 0
    assert '_id' in outputs[0]

def test_find_outputs_by_run_workflow_id_failure(mock_db):
    mock_db['outputs'].find.side_effect = errors.PyMongoError("Find error")
    outputs = mongo.find_outputs_by_run_workflow_id(mock_db, "run_workflow_id")
    assert outputs == []