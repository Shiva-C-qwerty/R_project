import subprocess
import streamlit as st
from PIL import Image

st.title(' R x BERT Web App')

st.sidebar.markdown('''
# About
This web-app can be used to convert digital image to text.
We can also use this app to get answers to any questions about the extracted text.
The main technologies used in this app are:
- `Tessaract OCR`
- `BERT Question Answering Model`
''')

st.subheader('Give your image as input')
file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

process1 = subprocess.Popen(["Rscript", "helloWorld.R"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
result1 = process1.communicate()
st.write(result1)
