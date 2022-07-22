# Flask_App

This app contains code to the Flask App which queries to the Firebase storage account related to this account.
The same app is hosted on Pythonanywhere.com till 10/03/2022.

## How to run:

1. Install Python 
2. run pip install -r requirements.txt
3. run python flask_app.py

This app is able to:

1. Query relevant data items suchs as:
  a. Candidate list
  b. PDF Resumes
  c. Pre-computed raw text of PDF Resumes
  d. Stopword list
  e. Job description raw text
  f. Precomputed ranked list of Candidates
2. Implement assorted text distance embedding comparision method over a list of candidates
