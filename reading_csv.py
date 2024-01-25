from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import csv
from scipy.special import softmax
import seaborn as sns
import matplotlib.pyplot as plt



csv_file_path = 'comments_data_3.csv'
with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file)
    
    # Skip the header row
    next(csv_reader)
    
    
    comments = []
    for index, row in enumerate(csv_reader):
        comments.append(row[0])


print(len(comments))
roberta = "cardiffnlp/twitter-roberta-base-sentiment"

model = AutoModelForSequenceClassification.from_pretrained(roberta)
tokenizer = AutoTokenizer.from_pretrained(roberta)

labels = ['Negative', 'Neutral', 'Positive']

# sentiment analysis
positive_comments = []
negative_comments = []
neutral_comments = []

for comment in comments:

    encoded_comment = tokenizer(comment, return_tensors='pt', max_length=512, truncation=True)
    
    output = model(**encoded_comment)

    scores = output[0][0].detach().numpy()
    scores = softmax(scores)

    scores_labels = {}
    
    for i in range(len(scores)):
        
        l = labels[i]
        s = scores[i]
        scores_labels[l] = s
       # print(l,s)

    max_label = max(scores_labels, key=scores_labels.get)
    
    if max_label == 'Positive':
        positive_comments.append(max_label)
    elif max_label == 'Negative':
        negative_comments.append(max_label)
    else:
        neutral_comments.append(max_label)
    
positive_length = len(positive_comments)
negative_length = len(negative_comments)
neutral_length = len(neutral_comments)

print(positive_length, negative_length, neutral_length)

categories = ['Positive', 'Negative', 'Neutral']
lengths = [positive_length, negative_length, neutral_length]

plt.bar(categories, lengths, color=['green', 'red', 'gray'])
plt.xlabel('Sentiment')
plt.ylabel('Length')
plt.title('Length of Lists by Sentiment')
plt.show()
    #print(max_label)