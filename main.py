from svm import SVM

if __name__ == '__main__':
    svm = SVM('train_images/')
    svm.extract_characters('images/image9.png')
