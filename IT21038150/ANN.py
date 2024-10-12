import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import confusion_matrix
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

# Reading training data
testData = pd.read_csv('../dataProcessing/processedData/testDataProcessed.csv')
trainData = pd.read_csv('../dataProcessing/processedData/trainDataProcessed.csv')

# Selecting columns for binary classification
df = pd.concat([testData, trainData], ignore_index=True, sort=False)
numeric_col = df.select_dtypes(include='number').columns
numericCols = numeric_col[:len(numeric_col)-1]
numericBinaryData = df[numericCols]
numericBinaryData['alert'] = df['alert']

# Finding attributes which have more than 0.5 pearson correlation coefficient
corr = numericBinaryData.corr()
corr_y = abs(corr['alert'])
highest_corr = corr_y[corr_y > 0.4]
highest_corr.sort_values(ascending=True)

# Selecting the attributes found through the pearson correlation from the dataset
processed = numericBinaryData[[
  "frame_len",
  "frame_cap_len",
  "frame_protocols",
  "ip_dsfield_dscp",
  "ip_flags_df",
  "ip_proto",
  "ip_checksum",
  "ip_flags",
  "ip_ttl",
  "tcp_len",
  "tcp_flags_push",
  "tcp_window_size",
  "tcp_window_size_scalefactor",
  "udp_length",
  "udp_checksum",
  "udp_checksum_status",
  "udp_stream",
  "dns_count_add_rr",
  "dns_qry_name_len",
  "dns_count_labels"
]]

processed['alert'] = numericBinaryData['alert']
X = processed.iloc[:,0:processed.shape[1]-1]
Y = processed[['alert']].values

# Dividing the train test datasets
X_train, X_test, y_train, y_test = train_test_split(X,Y, test_size=0.50, random_state=42)

# Model Infomation
modelVersion = "ID_ANN_V7"
input_dim = X_train.shape[1]
neurons = 256
epochs = 1500
batch = 25
lr = 0.00025
model = Sequential()

# Model architecture
model.add(Dense(neurons, input_dim=input_dim, activation='relu'))
model.add(Dense(64, activation='relu'))
# model.add(Dense(64, activation='relu'))
# model.add(Dense(64, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.summary()
model.compile(Adam(learning_rate=lr), loss='binary_crossentropy', metrics=['accuracy'])

# Training the ANN Model
history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch, verbose=1, validation_split=0.3, shuffle=True)
loc = "models/" + str(modelVersion) + ".h5"
model.save(loc)

# Making predictions on the test dataset
predictions = model.predict(X_test)
predictions = (predictions > 0.5)*1

scores = model.evaluate(X_test, y_test, verbose=0),
print(scores)

# Confusion Matrix
cfm = confusion_matrix(y_test, predictions)
disp = ConfusionMatrixDisplay(cfm)
disp.plot()
pltTitle = str(modelVersion) + " Confusion Matrix"
plt.title(pltTitle)
plt.gca().invert_yaxis()
pltLoc = "models/" + str(modelVersion) + "_confusionMatrix.jpg"
plt.savefig(pltLoc)
plt.close()

# Model Accuracy
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
pltTitle = str(modelVersion) + " Model Accuracy"
plt.title(pltTitle)
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='lower right')
pltLoc = "models/" + str(modelVersion) + "_model_accuracy.jpg"
plt.savefig(pltLoc)
plt.close()

# Model Loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
pltTitle = str(modelVersion) + " Model Loss"
plt.title(pltTitle)
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='lower right')
pltLoc = "models/" + str(modelVersion) + "_model_loss.jpg"
plt.savefig(pltLoc)
plt.close()







































