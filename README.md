This repository contains the code base and other assets related to the research project components of the four group members.
	1. Wijesinghe WMAJ - IT21038150
	2. Abeysinghe YPP - IT21022142
	3. Rukshana MAF - IT21026416
	4. Adikari AMPS - IT20008314

## Introduction
Our research project title is "Polymorphic Security Enhancements for Corporate Environments Utilizing Behavior Analytics". The project is aimed on building a comprehensive system that can bridge the gap between users in corporate environments and the current threat landscape.

The system is divided into four main components, 
* Scoring and Mitigating Browser-based Risks through User Behavior Profiling​​
* NLP Based Policy Generation​​
* Web Browser-Based Phishing Detection​
* Network Intrusion Detection Utilizing Artificial Neural Networks​

Our system combines all the components to improve the overall security and user awareness of the users and harden the infrastructure of the organization by reducing the risk of human error.

###  Network Intrusion Detection Utilizing Artificial Neural Networks
The objective of this component is to employee artificial neural networks to analyze and detect whether network traffic is malicious or not. The artificial neural network used in the component is very light weight, only containing 4 layers,
* 10 node input layer
* 64 node hidden layer
* 32 node hidden layer
* 1 node output layer
making this ANN model less resource intensive while retaining the accuracy of predictions. After training the model with a labeled training dataset by provided university of Queensland, Australia, the model is embedded into a network traffic interceptor proxy to capture and make predictions upon the network traffic. Also this component consists of a threat intelligence gathering solution. This uses an opensource honeypot solution to gather threat intelligence like, malware IPs, usernames, passwords. These data is correlated with the corporate environments to improve the overall security posture of the organization.
