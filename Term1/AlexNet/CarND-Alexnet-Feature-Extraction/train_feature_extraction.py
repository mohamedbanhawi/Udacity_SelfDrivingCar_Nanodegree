import pickle
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from alexnet import AlexNet
import numpy as np

#Load traffic signs data.
with open('train.p', mode='rb') as f:
    data = pickle.load(f)

X, y = data['features'], data['labels']

classes = np.unique(y)
n_classes = classes.size
#Split data into training and validation sets.
X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2)

# Define placeholders and resize operation.
x = tf.placeholder(tf.float32, (None, 32, 32, 3))
y = tf.placeholder(tf.int32, (None))
one_hot_y = tf.one_hot(y, n_classes)

resized = tf.image.resize_images(x, (227, 227))

# NOTE: By setting `feature_extract` to `True` we return
# pass placeholder as first argument to `AlexNet`.
fc7 = AlexNet(resized, feature_extract=True)

# NOTE: `tf.stop_gradient` prevents the gradient from flowing backwards
# past this point, keeping the weights before and up to `fc7` frozen.
# This also makes training faster, less work to do!
fc7 = tf.stop_gradient(fc7)

# Add the final layer for traffic sign classification.
shape = (fc7.get_shape().as_list()[-1], n_classes)  # use this shape for the weight matrix
 
fc8W = tf.Variable(tf.truncated_normal(shape=(shape), mean = 0, stddev = 0.1))
fc8b = tf.Variable(tf.zeros(shape[1]))

logits = tf.matmul(fc7, fc8W) + fc8b
probs = tf.nn.softmax(logits)

init = tf.global_variables_initializer()
sess = tf.Session()

# Define loss, training, accuracy operations.
rate = 0.001

EPOCHS = 15
BATCH_SIZE = 128

cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=one_hot_y, logits=logits)
loss_operation = tf.reduce_mean(cross_entropy)

# Adam optimiser is a modified SGD algorithm with modified training rate
optimizer = tf.train.AdamOptimizer()

training_operation = optimizer.minimize(loss_operation)

### Calculate and report the accuracy on the training and validation set.
correct_prediction = tf.equal(tf.argmax(logits, 1), tf.argmax(one_hot_y, 1))
accuracy_operation = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

def evaluate(X_data, y_data):
    num_examples = len(X_data)
    total_accuracy = 0
    sess = tf.get_default_session()
    for offset in range(0, num_examples, BATCH_SIZE):
        batch_x, batch_y = X_data[offset:offset+BATCH_SIZE], y_data[offset:offset+BATCH_SIZE]
        accuracy = sess.run(accuracy_operation, feed_dict={x: batch_x, y: batch_y, keepprob: 1.0})
        total_accuracy += (accuracy * len(batch_x))
    return total_accuracy / num_examples

# Train and evaluate the feature extraction model.
sess.run(init)
num_examples = len(X_train)

print("Training...")
for i in range(EPOCHS):
    X_train, y_train = shuffle(X_train, y_train)
    for offset in range(0, num_examples, BATCH_SIZE):
        end = offset + BATCH_SIZE
        batch_x, batch_y = X_train[offset:end], y_train[offset:end]
        sess.run(training_operation, feed_dict={x: batch_x, y: batch_y})
        
    validation_accuracy = evaluate(X_valid, y_valid)
    print("EPOCH {} ...".format(i+1))
    print("Validation Accuracy = {:.3f}".format(validation_accuracy))
    print()
    
print("Model saved")