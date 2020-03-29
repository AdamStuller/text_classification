from app.machine_learning.preprocessing import NLP4SKPreprocesser, TFIDFTransformer, LDATransformer, OneHotTransformer
from sklearn.pipeline import Pipeline
import pandas as pd
from joblib import dump, load
from os import path, listdir
from os.path import isfile, splitext
from app.config import config
from sklearn.ensemble import RandomForestClassifier
from datetime import date
from app.constants import DATASET_ARG, PIPELINE_ARG, DEFAULT_DATASET, BANKS_COLUMNS, UPDATED_BANKS_COLUMNS

import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-path", "-dp", dest="dataset_path",
                        default=path.join(config['path_to_datasets'], f'{DEFAULT_DATASET}'))
    return parser.parse_args()


def preprocess_banks(banks: pd.DataFrame):
    banks = banks[banks.sentence.notna()]
    banks['class'] = banks['class'].apply(
        lambda x: x if x != 'Problémy s produktov' else 'Problémy s produktom')
    banks = banks.drop_duplicates(subset='sentence')
    banks.index = range(len(banks))
    return banks


def preprocess_updated_banks(updated_banks: pd.DataFrame):
    return updated_banks[updated_banks.updated_sentence.notna()]


def get_data(data=None, dataset_name=DEFAULT_DATASET, head_n=None, preprocess=None, column_names=UPDATED_BANKS_COLUMNS):

    path_to_dataset = path.join(
        config['path_to_datasets'],
        f'{dataset_name}.csv'
    )

    if not isfile(path_to_dataset):
        raise FileNotFoundError(
            f'Dataset {dataset_name}.csv does not exists in dataset directory'
        )

    if head_n != None and not type(head_n) is int:
        raise TypeError('Head must be integer or None')

    if data == None:
        banks = pd.read_csv(path_to_dataset, names=column_names)
        if preprocess != None and callable(preprocess):
            banks = preprocess(banks)
    else:
        banks = data

    return banks if head_n == None else banks.head(head_n)


def train_pipeline(dataset_name=DEFAULT_DATASET, column_names=UPDATED_BANKS_COLUMNS, preprocess=None, pipeline_name=None, head_n=None):

    print(dataset_name)
    path_to_pipeline = path.join(
        config['path_to_models'],
        f'{pipeline_name}.joblib' if pipeline_name != None
        else f'pipeline-{str(date.today())}.joblib')

    pipe = Pipeline(
        steps=[
            # ('nlp4sk', NLP4SKPreprocesser('sentence')),
            ('tf-idf', TFIDFTransformer('updated_sentence')),
            ('one-hot', OneHotTransformer(['parent_class'])),
            ('random_forest', RandomForestClassifier(n_estimators=200,
                                                     max_depth=50,
                                                     criterion='gini',
                                                     bootstrap=True,
                                                     random_state=42))
        ],
        verbose=True
    )

    X = get_data(head_n=head_n, dataset_name=dataset_name, column_names=column_names, preprocess=preprocess)\
        .drop(columns=['class'])
    Y = get_data(head_n=head_n,
                 dataset_name=dataset_name,
                 column_names=column_names,
                 preprocess=preprocess
                 )['class']

    pipe.fit(X, Y)

    dump(pipe, path_to_pipeline)


def get_all(folder_type):

    if folder_type == DATASET_ARG:
        path_to_pipelines = config['path_to_datasets']
    elif folder_type == PIPELINE_ARG:
        path_to_pipelines = config['path_to_models']
    else:
        raise KeyError(
            f'folder_type argument is either "{DATASET_ARG}" or "{PIPELINE_ARG}"'
        )

    files_in_model_dir = list(
        filter(
            lambda f: isfile(path.join(path_to_pipelines, f)),
            listdir(path_to_pipelines)
        )
    )
    return list(
        map(
            lambda f: splitext(f)[0],
            files_in_model_dir
        )
    )


def nlp4sk_preprocess(data=None, input_dataset_name='banks', output_dataset_name='updated_banks',  head_n=None):
    if data == None:
        data = get_data(
            dataset_name=input_dataset_name,
            head_n=head_n,
            preprocess=preprocess_banks,
            column_names=BANKS_COLUMNS
        )

    path_to_output_dataset = path.join(
        config['path_to_datasets'],
        f'{output_dataset_name}.csv'
    )

    nlp4sk_processer = NLP4SKPreprocesser('sentence')
    updated_data = nlp4sk_processer.transform(data)
    updated_data.to_csv(path_to_output_dataset, header=False)


if __name__ == "__main__":
    args = parse_arguments()
    # print(get_all('pipeline'))
    train_pipeline(preprocess=preprocess_updated_banks)
    # nlp4sk_preprocess()