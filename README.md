AI-Based Cryptocurrency Fraud Detection System:

This project is a machine learning–based system designed to detect fraudulent cryptocurrency transactions before they are executed.
It analyzes transaction behavior and user patterns to generate a risk score and determine whether a transaction should be approved or blocked.

The system is deployed using Streamlit, allowing users to interact with the model through a web interface.

Features:

1.Real-time cryptocurrency fraud detection
2.Machine learning–based risk scoring
3.Fraud classification using Random Forest
4.Interactive web interface using Streamlit
5.Visual display of transaction risk and status

🧠 Technologies Used:

1.Python
2.Pandas, NumPy
3.Scikit-learn
4.Machine Learning (Random Forest, Logistic Regression)
5.Streamlit

📊 Machine Learning Workflow

1.Data Collection
  •Transaction and user behavior data
2.Data Preprocessing
  •Data cleaning
  •Feature scaling
  •Handling missing values
  •Handling imbalanced data
3.Model Training
  •Logistic Regression
  •Random Forest
4.Model Evaluation
  •Accuracy
  •Precision
  •Recall
  •F1-Score
  •ROC-AUC
5.Deployment
  •Model integrated into a Streamlit application for real-time prediction

How the System Works:

1.User enters transaction details such as amount, time, and wallet behavior.
2.The system applies fraud detection rules and passes the data to the trained ML model.
3.The model calculates a fraud risk score.
4.The transaction is either approved or blocked based on the risk score.

How to Run the Project:

1.Clone the repository:
    git clone https://github.com/nandakumaranand23/crypto-fraud-streamlit.git

2.Install required packages:
    pip install -r requirements.txt

3.Run the Streamlit app
    streamlit run app.py

Project Objective:
    To build an intelligent system that helps prevent financial fraud in cryptocurrency platforms by using machine learning and data analysis.

Author:
  Nanda Kumar A
  BCA (AI & Data Science) | Data Analyst
  GitHub: https://github.com/nandakumaranand23
