import streamlit as st
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
import tempfile
import os
import pandas as pd
from transformers import pipeline
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter

# function to remove non-alphanumeric characters, convert to lowercase, remove stopwords, and remove whitespace
def clean_text(text):
    text = re.sub('[^a-zA-Z0-9\s]', '', text)
    text = text.lower()
    stopwords = ['the', 'and', 'of', 'to', 'in', 'a', 'for', 'is']
    text = ' '.join([word for word in text.split() if word not in stopwords])
    text = text.strip()
    return text

# for images
def ocr_img(file):
    _, file_ext = os.path.splitext(file.name)
    
    if file_ext == '.pdf':
        with tempfile.TemporaryDirectory() as path:
            pages = convert_from_path(file, 500, output_folder=path)
            text = ''
            for page in pages:
                with tempfile.NamedTemporaryFile(suffix='.jpeg') as image_file:
                    page.save(image_file.name, 'JPEG')
                    img = Image.open(image_file.name)
                    text += pytesseract.image_to_string(img)
    else:
        with Image.open(file) as img:
            text = pytesseract.image_to_string(img)
    
    text_clean = clean_text(text)
    with open('output.txt', 'w') as f:
        f.write(text_clean)
    return text_clean

st.title(' OCR x BERT Web App')

st.sidebar.markdown('''
# About
This web-app can be used to convert digital image to text.
We can also use this app to get answers to any questions about the extracted text.

The main technologies used in this app are:
- `Tessaract OCR`
- `BERT Question Answering Model`
''')

st.subheader('Give your image as input')
file = st.file_uploader("Choose an image or PDF file", type=["jpg", "jpeg", "png", "pdf"])

if file is not None:
    st.image(file,caption = "Uploaded Image/PDF")

    options = ["OCR", "Question Answering","Exploratory Analysis"]
    selected_options = st.multiselect("Select options", options)

    text = ""
    if "OCR" in selected_options:
        text = ocr_img(file)
        st.write("Extracted Text:")
        st.write(text)
    
    if "Question Answering" in selected_options and not text:
        st.write("Perform OCR first !!")
    if "Question Answering" in selected_options and text:
        question_answerer = pipeline("question-answering", model='distilbert-base-cased-distilled-squad')
        
        st.subheader("Question Answering")
        question = st.text_input("Give your question")
        
        if question:
            context = text

            result = question_answerer(question = question,context = context)

            st.write("Result:", result['answer'])
            
    if "Exploratory Analysis" in selected_options and not text:
        st.write("Perform OCR first !!")
    
    if "Exploratory Analysis" in selected_options and text:
        # tokenize the text into words
        words = text.lower().split()

        # count the frequency of each word
        word_freq = Counter(words)

        # create a DataFrame with word frequencies
        df_word_freq = pd.DataFrame(list(word_freq.items()), columns=['word', 'count'])

        # sort the DataFrame by word frequency
        df_word_freq.sort_values(by=['count'], ascending=False, inplace=True)

        # create a bar chart of the most common words
        fig, ax = plt.subplots()
        sns.barplot(data=df_word_freq.head(10), x='word', y='count', ax=ax)
        ax.set_title('Top 10 Most Common Words')
        ax.set_xlabel('Word')
        ax.set_ylabel('Count')
        st.pyplot(fig)

        wordcloud = WordCloud(background_color='white').generate_from_frequencies(word_freq)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
        
        # create a histogram of word frequencies
        fig, ax = plt.subplots()
        sns.histplot(df_word_freq['count'], bins=20, ax=ax)
        ax.set_title('Distribution of Word Frequencies')
        ax.set_xlabel('Frequency')
        ax.set_ylabel('Count')
        st.pyplot(fig)