
def most_frequent(pred):
    count_list = []
    for x in pred:
        count_list.append(pred.count(x))
        
    max_idx = count_list.index(max(count_list))
    return pred[max_idx]

if __name__ == '__main__':
    import cv2
    import pickle
    import argparse
    import importlib
    from transformer import PoseExtractor

    parser = argparse.ArgumentParser(description='Run inference on webcam video')
    parser.add_argument('--config', type=str, default='conf',
                        help="name of config .py file inside config/ directory, default: 'conf'")
    args = parser.parse_args()
    config = importlib.import_module('config.' + args.config)

    model = pickle.load(open(config.classifier_model, 'rb'))

    extractor = PoseExtractor()
    cap = cv2.VideoCapture(config.stream)
    

    
    count = 0
    pred = []
    while(cap.isOpened()):
        ret, image = cap.read()
      
        if ret == True:
            count += 1
            
            cv2.imshow('Crime Detection', image)
            sample = extractor.transform([image])
            prediction = model.predict(sample.reshape(1, -1))
#             print(prediction[0])
            pred.append(prediction[0])
            
            if count == 16:
#                 print(pred)
                print(most_frequent(pred))
                count = 0
                pred=[]
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    cap.release()
    cv2.destroyAllWindows()



