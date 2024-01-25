import config
import praw
import matplotlib
matplotlib.use('Agg')  # Set the Matplotlib backend to 'Agg'
import matplotlib.pyplot as plt
import os
import seaborn as sns
import csv
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import string
import nltk
nltk.download('stopwords')
from multiprocessing.pool import ThreadPool
from functools import partial
from nltk.corpus import stopwords

def analyze_sentiment(comment, model, tokenizer):
    encoded_comment = tokenizer(comment, return_tensors='pt', max_length=512, truncation=True)
    output = model(**encoded_comment)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    labels = ['Negative', 'Neutral', 'Positive']

    scores_labels = {}
    
    for i in range(len(scores)):
        l = labels[i]
        s = scores[i]
        scores_labels[l] = s

    max_label = max(scores_labels, key=scores_labels.get)
    
    return max_label

def process_comments(comments, csv_writer):
    for comment in comments:
        if isinstance(comment, praw.models.MoreComments):
            # Recursively process more comments
            process_comments(comment.comments(), csv_writer)
        else:
            cleaned_comment = comment_cleaning(comment.body)
            csv_writer.writerow([' '.join(cleaned_comment)])

def comment_cleaning(comment):
    punc_removed = [char for char in comment if char not in string.punctuation]
    punc_removed_join = ''.join(punc_removed)
    punc_removed_join_clean = [word for word in punc_removed_join.split() if word.lower() not in stopwords.words('english')]
    
    return punc_removed_join_clean

def save_plots(first_team, second_team, first_positive_length, first_negative_length,
               second_positive_length, second_negative_length):
    categories = ['Positive', 'Negative']
    first_lengths = [first_positive_length, first_negative_length]
    second_lengths = [second_positive_length, second_negative_length]

    os.makedirs('static', exist_ok=True)
    
    # Generate bar chart for the first team
    first_plot_path = os.path.join('static', 'first_team_sentiment_plot.png')
    plt.bar(categories, first_lengths, color=['green', 'red'])
    plt.xlabel('Sentiment')
    plt.yticks([])
    plt.savefig(first_plot_path)
    plt.clf()

    # Generate bar chart for the second team
    second_plot_path = os.path.join('static', 'second_team_sentiment_plot.png')
    plt.bar(categories, second_lengths, color=['green', 'red'])
    plt.xlabel('Sentiment')
    plt.yticks([])
    plt.savefig(second_plot_path)
    plt.clf()

def get_reddit_data(first_team, second_team, competition, first_players_filter, second_players_filter):
    user_agent = 'PRAW and Reddit API'
    reddit = praw.Reddit(client_id=config.ID,
                     client_secret=config.SECRET,
                     user_agent=user_agent)

    # Specify the subreddit and keywords
    subreddit_name = 'soccer'
    keywords = [first_team, second_team, competition]

    # Search for posts containing the specified keywords in the title
    search_query = ' '.join(keywords)
    subreddit = reddit.subreddit(subreddit_name)
    search_results = subreddit.search(search_query, sort='relevance', limit=1)

    csv_file_path = 'data/comments_data.csv'
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Comment Body'])

        for post in search_results:
            post_id = post.id
            print(f"Found post: {post.title} (ID: {post_id})")

            # Extract comments and write to CSV
            submission = reddit.submission(id=post_id)
            comments = submission.comments.list()
            process_comments(comments, csv_writer)

        print(f"Comments saved to {csv_file_path}")


    csv_file_path = 'data/comments_data.csv'
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)

        # Skip the header row
        next(csv_reader)

        comments = []
        for index, row in enumerate(csv_reader):
            comments.append(row[0])

    print(len(comments))

    first_team_comments, second_team_comments, neutrals = classify_comments(
        comments, first_players_filter, second_players_filter, first_team, second_team
    )

    roberta = "cardiffnlp/twitter-roberta-base-sentiment"

    model = AutoModelForSequenceClassification.from_pretrained(roberta)
    tokenizer = AutoTokenizer.from_pretrained(roberta)

    analyze_sentiment_partial = partial(analyze_sentiment, model=model, tokenizer=tokenizer)

    first_team_sentiment = analyze_comments_sentiment(first_team_comments, analyze_sentiment_partial)
    second_team_sentiment = analyze_comments_sentiment(second_team_comments, analyze_sentiment_partial)

    first_positive_length = first_team_sentiment.count('Positive')
    first_negative_length = first_team_sentiment.count('Negative')
    first_neutral_length = first_team_sentiment.count('Neutral')

    second_positive_length = second_team_sentiment.count('Positive')
    second_negative_length = second_team_sentiment.count('Negative')
    second_neutral_length = second_team_sentiment.count('Neutral')

    # Generate and save plots
    save_plots(first_team, second_team, first_positive_length, first_negative_length,
               second_positive_length, second_negative_length)

    # Return sentiment lengths
    #return (
     #   (first_positive_length, first_negative_length, first_neutral_length),
      #  (second_positive_length, second_negative_length, second_neutral_length)
    #)

# ... (rest of the code)

def classify_comments(comments, first_players_filter, second_players_filter, first_team, second_team):
    first_team_comments = []
    second_team_comments = []
    neutrals = []

    for comment in comments:
        comment_split = comment.split(' ')
        added_comment = False
        for word in comment_split:
            if word in first_players_filter or word == first_team:
                first_team_comments.append(comment)
                added_comment = True
                break
            elif word in second_players_filter or word == second_team:
                second_team_comments.append(comment)
                added_comment = True
                break

        if not added_comment:
            neutrals.append(comment)

    return first_team_comments, second_team_comments, neutrals

def analyze_comments_sentiment(comments, analyze_sentiment_partial):
    pool = ThreadPool()
    sentiment = pool.map(analyze_sentiment_partial, comments)
    pool.close()
    pool.join()

    return sentiment
