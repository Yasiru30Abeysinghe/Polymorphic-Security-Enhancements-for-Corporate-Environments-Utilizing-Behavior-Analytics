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


**Scoring and Mitigating Browser-based Risks through User Behavior Profiling**

The objective of this component is to assess and mitigate browser-based security risks in a corporate environment by profiling user behavior and calculating risk scores. This system employs a comprehensive approach to evaluate the web presence hygiene of each user, considering potential browser-based security vulnerabilities identified through STRIDE threat modeling.

The component consists of several key elements:

1. Telemetry Collection: Endpoint agents collect detailed telemetry data on user browsing behavior and browser configurations. This data is transmitted via Filebeat to an Elasticsearch database for centralized storage and analysis.
2. Risk Scoring Engine: Utilizing Kibana's runtime fields and scripted fields, the system evaluates risk scores based on the collected telemetry data. The scoring algorithm considers various factors such as:
   - Browser version and patch level
   - Enabled security features
   - Installed extensions and their permissions
   - Browsing patterns and accessed websites
   - User interactions with potentially risky content
3. User Behavior Profiling: By analyzing the collected data and risk scores, the system creates detailed profiles for each user. These profiles provide insights into individual browsing habits, risk tendencies, and potential security vulnerabilities.
4. Centralized Management Console: A single-pane management interface displays user profiles, risk scores, and detailed metrics. This allows security teams to quickly identify high-risk users and potential security gaps across the organization.

By leveraging this user behavior profiling and risk scoring approach, organizations can proactively identify and address browser-based security risks, enhancing their overall security posture and reducing the likelihood of successful attacks exploiting web-based vulnerabilities.

###  NLP-based Browser Policy Generation and Enforcement System

Objectives
The key objective of this system is to **automate browser security configurations** based on high-level inputs. This component ensures that enterprises can:

* Prevent browser-based security threats through policy enforcement (e.g., blocking third-party cookies, managing browser extensions).
* Streamline DLP (Data Leakage Prevention) and Threat Prevention policies through NLP-based automation.
* Provide flexibility across multiple Chromium-based browsers by dynamically adjusting configurations.

### Key Components


1. NLP Policy Generation Engine 

    * Translates high-level security requirements into technical configurations.
    * Supports multiple policy categories, such as Threat Prevention and Data Leakage Prevention (DLP).
    * Maps user inputs to specific browser registry settings.


2. Browser Compatibility & Configuration 

    * Configures policies across Chromium-based browsers.
    * Policies are mapped to the appropriate registry paths dynamically during execution.

3. Logging Mechanism

    * Policies are logged only after successful execution on the devices.
    * Logs are saved in the logs folder with detailed information, including policy type, timestamp, and status.
 

