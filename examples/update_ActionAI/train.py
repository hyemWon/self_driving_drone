
# pipeline: 여러 변환기를 연결 

import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from transformer import PoseExtractor

def actionModel(classifier):
    pipeline = Pipeline([
               ('pose_extractor', PoseExtractor()),
               ('classifier', classifier)]) # LogisticRegression
    return pipeline

def trainModel(csv_path, pipeline):
    df = pd.read_csv(csv_path)
    X = df['image'].values
    y = df['label']
    
    train_x, test_x, train_y, test_y = train_test_split(X, y, test_size=0.2, random_state=11)
    print(len(train_x), len(train_y))
    print(len(test_x), len(test_y)) 
    pipeline = pipeline.fit(train_x, train_y)
    
    pred = pipeline.predict(test_x)
    print(accuracy_score(test_y, pred))
    
    return pipeline.get_params()['steps'][1][1]  

if __name__ == '__main__':
    import pickle
    import argparse
    import importlib

    parser = argparse.ArgumentParser(description='Train pose classifier')
    parser.add_argument('--config', type=str, default='conf',
                        help="name of config .py file inside config/ directory, default: 'conf'")
    args = parser.parse_args()
    config = importlib.import_module('config.' + args.config)
    
#     print(config.classifier())
    pipeline = actionModel(config.classifier(solver='lbfgs', max_iter=1300))
    model = trainModel(config.csv_path, pipeline)
    

    # Dump the model to file
    pickle.dump(model, open(config.classifier_model, 'wb'), protocol=2)
