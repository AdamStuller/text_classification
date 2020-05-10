from .base import workflows_bp
from flask import request, current_app, jsonify
from app.models import Topic, Document, Tag
from jsonschema import validate, ValidationError, SchemaError
import pandas as pd
from app.machine_learning.preprocessing import NLP4SKPreprocesser
from app.machine_learning.predict import predict_tag
from app.config import predict_schema
from app.helpers import DefaultValidatingDraft7Validator
from copy import deepcopy
from werkzeug.exceptions import NotFound,  BadRequest, HTTPException


nlp4sk = NLP4SKPreprocesser('sentence')


@workflows_bp.route('/api/v1/topics/<topic_name>', methods=['GET'])
def handle_single_topic(topic_name):
    
    topic = Topic.query\
        .filter(Topic.name == topic_name)\
        .with_entities(
            Topic.id,
            Topic.name,
            Topic.description,
            Topic.accuracy,
            Topic.f1_macro,
            Topic.f1_weighted,
            Topic.recall,
            Topic.precision,
            Topic.updated
        )\
        .first()

    if topic is None:
        raise NotFound(f'Topic {topic_name} does not exist')

    evaluation = {
        'f1_macro': topic.f1_macro,
        'f1_weighted':  topic.f1_weighted,
        'recall': topic.recall,
        'precision': topic.precision,
        'accuracy':  topic.accuracy,
    }

    from sqlalchemy import func
    from functools import reduce

    tags = Tag.query\
        .filter(topic.id == Tag.topic_id)\
        .join(Document)\
        .with_entities(
            Tag.label,
            func.count(Tag.label)
        )\
        .group_by(Tag.label)\
        .all()
    
    tags = reduce(
        lambda acc, x: { 
            **acc, 
            **{x[0] :  x[1]}
        },
        tags,
        {}
    ) 
    if topic is not None:
        return  { 
            'name': topic.name,
            'description': topic.description ,
            'tags': tags,
            'evaluation': evaluation,
            'updated': topic.updated
        }  
    else:
        raise NotFound(f'Topic {topic_name} does not exist')

@workflows_bp.route('/api/v1/topics/validate/<topic_name>', methods=['GET'])
def validate_topic(topic_name):
    topic = Topic.query\
        .filter(Topic.name == topic_name)\
        .first()

    return {
        "validation": True if topic is not None else False
    }

@workflows_bp.route('/api/v1/topics/<topic_name>/predict', methods=['POST'])
def handle_predict(topic_name):

    data = request.json

    current_app.logger.info(data)

    DefaultValidatingDraft7Validator(predict_schema)\
        .validate(data)

    current_app.logger.info(data)

    dataset = data['dataset']

    pipeline  = Topic.get_pipeline_by_name(topic_name)
    if pipeline is None:
        raise NotFound(f'Topic {topic_name} does not exist')

    try:
        prediction = predict_tag(
            pipeline,
            nlp4sk.transform(dataset)
        )

        current_app.logger.info(prediction)

        return {
            'success': True,
            'payload': prediction
        }

    except KeyError as error: 
        raise BadRequest(repr(error))

    except Exception as e:
        raise HTTPException(repr(e))
