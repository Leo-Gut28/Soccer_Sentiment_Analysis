import config
import praw
import pandas as pd
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import csv

user_agent = 'Testing PRAW and Reddit API'
reddit = praw.Reddit(client_id=config.ID,
                     client_secret=config.SECRET,
                     user_agent=user_agent)
    
# Specify the subreddit and keywords
subreddit_name = 'soccer'
keywords = ['Real Madrid', 'Barcelona', 'Spanish Supercopa']

# Search for posts containing the specified keywords in the title
search_query = ' '.join(keywords)
subreddit = reddit.subreddit(subreddit_name)
search_results = subreddit.search(search_query, sort='revelance', limit=1)

for post in search_results:
    post_id = post.id
    print(f"Found post: {post.title} (ID: {post_id})")

    # Create a CSV file and write header
    csv_file_path = 'comments_data_3.csv'
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Comment Body'])

        def process_comments(comments, csv_writer):
            for comment in comments:
                if isinstance(comment, praw.models.MoreComments):
                    # Recursively process more comments
                    process_comments(comment.comments(), csv_writer)
                else:
                    csv_writer.writerow([comment.body])

        # Extract comments and write to CSV
        submission = reddit.submission(id=post_id)
        process_comments(submission.comments.list(), csv_writer)

    print(f"Comments saved to {csv_file_path}")
