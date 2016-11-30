import os
from sklearn.svm import LinearSVC
from random import shuffle
from preprocessor import *
import pickle

class SVM(object):

    def __init__(self, train_img_dir):
        # class_weights = {0: 0.5, 1: 0.5}
        #self.model = LinearSVC(class_weight=class_weights)
        with open('weights.pkl', 'rb') as clf_pkl:
            self.model = pickle.load(clf_pkl)
        #self.x, self.y = self.get_x_and_y(train_img_dir)
    
    def get_x_and_y(self, train_img_dir):
        '''
        Given a directory of training images, return a list
        containing features for each image as well as a list
        containing the labels of each image
        '''
        train_img_names = os.listdir(train_img_dir)
        shuffle(train_img_names)
        x = []
        y = []
        for train_img_name in train_img_names:
            train_img = cv2.imread(train_img_dir + train_img_name)
            train_img = cv2.resize(train_img, (125, 125), cv2.INTER_CUBIC)
            train_img = self.otsu_threshold(train_img)
            x.append(self.get_features(train_img))
            # if it's a character
            if len(train_img_name) > 7:
                y.append(1)
            else:
                y.append(0)
        return x, y

    def train(self):
        '''
        Train the linear support vector machine and put in pickle file
        '''
        self.model.fit(self.x, self.y)
        with open('weights.pkl', 'wb') as clf_pkl:
            pickle.dump(self.model, clf_pkl)

    # not really needed
    def train_and_score(self, train_img_dir):
        train_img_names = os.listdir(train_img_dir)
        shuffle(train_img_names)
        x = []
        y = []
        for train_img_name in train_img_names[:615]:
            train_img = cv2.imread(train_img_dir + train_img_name)
            train_img = cv2.resize(train_img, (125, 125), cv2.INTER_CUBIC)
            train_img = self.otsu_threshold(train_img)
            x.append(self.get_features(train_img))
            # if it's a character
            if len(train_img_name) > 7:
                y.append(1)
            else:
                y.append(0)
        self.model.fit(x, y)

        # testing
        labels = []
        features = []
        for img_name in train_img_names[615:]:
            if len(img_name) > 7:
                labels.append(1)
            else:
                labels.append(0)
            img = cv2.imread(train_img_dir + img_name)
            img = cv2.resize(img, (125, 125), cv2.INTER_CUBIC)
            img = self.otsu_threshold(img)
            features.append(self.get_features(img))
        print(self.model.score(features, labels))

    def extract_characters(self, img_name):
        '''
        Given an image, write sub images likely to contain
        characters to a directory and return a list containing
        the coordinates of these sub images
        '''
        preprocessor = Preprocessor(img_name)
        # for drawing boxes around suspected characters
        box_img = preprocessor.get_img()
        # image number
        num = 0
        sub_imgs = preprocessor.get_contours()
        for sub_img in sub_imgs:
            features = self.get_features(sub_img[0])
            prediction = self.model.decision_function([features])
            # if it's a character
            if prediction > 0:
                char_img = cv2.resize(sub_img[0], (32, 32), cv2.INTER_CUBIC)
                cv2.imwrite('characters/' + str(num) + '.png', char_img)
                num += 1
                x, y = sub_img[1], sub_img[2]
                w, h = sub_img[3], sub_img[4]
                cv2.rectangle(box_img, (x, y), (x + w, y + h), (0, 255, 0), 1)
        cv2.imwrite('boxes.png', box_img)

    def get_features(self, img):
        '''
        Given an image, return its features
        (histogram of oriented gradients)
        '''
        hog = cv2.HOGDescriptor()
        # flatten column vector into row vector
        h = hog.compute(img)
        np_array = np.array(h)
        h = np_array.T
        return np.array(h)[0].tolist()

    def otsu_threshold(self, img):
        '''
        Given an image, apply otsu's threshold to the image
        and return the image
        '''
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # gray_img = cv2.fastNlMeansDenoising(gray_img, None, 10)
        ret, gray_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY +
                                   cv2.THRESH_OTSU)
        return gray_img

