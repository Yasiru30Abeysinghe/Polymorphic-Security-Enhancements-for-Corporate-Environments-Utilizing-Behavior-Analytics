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

testData = pd.read_csv('../dataProcessing/processedData/testDataProcessed.csv')
trainData = pd.read_csv('../dataProcessing/processedData/trainDataProcessed.csv')

df = pd.concat([testData, trainData], ignore_index=True, sort=False)
numeric_col = df.select_dtypes(include='number').columns

numericCols = numeric_col[:len(numeric_col)-1]
numericBinaryData = df[numericCols]
numericBinaryData['alert'] = df['alert']
corr = numericBinaryData.corr()
corr_y = abs(corr['alert'])
highest_corr = corr_y[corr_y > 0.4]
highest_corr.sort_values(ascending=True)
print(highest_corr)

# processed = numericBinaryData[[
#   "frame_len",
#   "frame_cap_len",
#   "frame_protocols",
#   "ip_dsfield_dscp",
#   "ip_flags_df",
#   "ip_proto",
#   "ip_checksum",
#   "ip_flags",
#   "ip_ttl",
#   "tcp_stream",
#   "tcp_len",
#   "tcp_flags_push",
#   "tcp_window_size",
#   "tcp_window_size_scalefactor",
#   "udp_length",
#   "udp_checksum",
#   "udp_checksum_status",
#   "udp_stream",
#   "dns_count_add_rr",
#   "dns_qry_name_len",
#   "dns_count_labels"
# ]]

processed = numericBinaryData[[
  "frame_time_relative",
  "frame_protocols",
  "eth_type",
  "ip_flags",
  "ip_ttl",
  "ip_proto",
  "tcp_completeness",
  "tcp_completeness_data",
  "tcp_completeness_ack",
  "tcp_completeness_syn-ack",
  "tcp_completeness_syn",
  "tcp_window_size_value",
  "tcp_window_size",
  "tcp_analysis_push_bytes_sent",
  "dtls_record_content_type",
  "dtls_record_version",
  "dtls_record_length",
  "dtls_handshake_type",
  "udp_time_relative",
  "udp_checksum",
  "udp_stream",
  "dns_count_add_rr",
  "dns_qry_name_len",
  "dns_count_labels",
  "quic_fixed_bit",
  "quic_long_packet_type",
  "quic_version",
  "quic_length",
  "stun_type",
  "stun_type_class",
  "stun_type_method",
  "stun_length",
  "stun_network_version",
  "stun_attribute",
  "stun_att_type",
  "stun_att_length",
  "stun_att_crc32",
  "stun_att_crc32_status"
]]

modelVersion = "ID_ANN_V6"

processed['alert'] = numericBinaryData['alert']
processed.to_csv("binaryClassificationData", index=False)
X = processed.iloc[:,0:processed.shape[1]-1]
Y = processed[['alert']].values

X_train, X_test, y_train, y_test = train_test_split(X,Y, test_size=0.50, random_state=42)

input_dim = len(X_train.columns)
neurons = 256
epochs = 500
model = Sequential()

print(X_train.shape[1])
model.add(Dense(neurons, input_dim=X_train.shape[1], activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(64, activation='relu'))
# model.add(Dense(128, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.summary()
model.compile(Adam(learning_rate=.0001), loss='binary_crossentropy', metrics=['accuracy'])


history = model.fit(X_train, y_train, epochs=epochs, batch_size=50, verbose=1, validation_split=0.3, shuffle=True)
loc = "models/" + str(modelVersion) + ".h5"
model.save(loc)

predictions = model.predict(X_test)
predictions = (predictions > 0.5)*1

# output = pd.DataFrame({
#   'predicted_alert': predictions.flatten()
# })
# output.to_csv('output.csv', index=None)
scores = model.evaluate(X_test, y_test, verbose=0),
print(scores)

cfm = confusion_matrix(y_test, predictions)
disp = ConfusionMatrixDisplay(cfm)
disp.plot()
pltTitle = str(modelVersion) + " Confusion Matrix"
plt.title(pltTitle)
plt.gca().invert_yaxis()
pltLoc = "models/" + str(modelVersion) + "_confusionMatrix.jpg"
plt.savefig(pltLoc)
plt.close()

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







































