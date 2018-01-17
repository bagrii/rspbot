# rspbot.py
# Reddit bot for related reddit posts suggestions.

import praw
import json
import os
import glob

import learn
import reddit_scrape as rs

try:
    # authentication is a module located in the same direcotry as current script.
    # You need to add credentials in order to make request to Reddit.
    # To get credentials go to your account preference in Reddit => select apps tab
    # => click 'create another app' button and fill all info there, then get secret and
    # client id (random string under application name in left top corner)
    # User agent is a brief description of your bot, like: "joebot"
    # !!! Keep this file out of repository on your local machine as this is your private
    # information and must be not shared with others.
    import authentication as auth
except ImportError:
    auth = {'user_agent': "<YOUR USER AGENT NAME HERE>",
            'secret_id': "<YOUR SECRET ID HERE>",
            'client_id': "<YOUR CLIENT ID HERE>"}

def create_token_vector(data_path, tok_vector_file):
    """trying to load token vector from current directory,
    if not found - create new one from submissions history"""
    if os.path.exists(tok_vector_file):
        tok_vector = learn.load_token_vector(tok_vector_file)
    else:
        index = list()
        corpus = list()
        for file_name in glob.glob(os.path.join(data_path, "*.json")):
            with open(file_name, "r") as fp:
                submission = json.load(fp)
                corpus.append(submission['title'])
                index.append(os.path.basename(file_name).split('.')[0])
        tok_vector = {'vector': learn.get_tokens_vector(corpus), 'index': index}
    return tok_vector

def get_recommended_items(token_vector, data_path):
    index = token_vector['index']
    for submission_id in learn.get_similar_items(index, len(index) - 1,
        token_vector['vector']):
        submission_file = os.path.join(data_path, submission_id + ".json")
        with open(submission_file, "r") as fp:
            submission = json.load(fp)
            yield submission['title'], submission['url']

if __name__ == "__main__":
    # directory with scraped subreddit posts
    submissions_data_path = "/tmp/smallbusiness/"
    reddit = praw.Reddit(user_agent=auth['user_agent'], client_id=auth['client_id'],
                         client_secret=auth['secret_id'])
    subreddit = reddit.subreddit('smallbusiness')
    # chached matrix of tokens occurrences
    cache_vector_file = "vector.bin"
    print("rspbot: Creating vector tokens...")
    token_vector = create_token_vector(submissions_data_path, cache_vector_file)
    # how often to save cache?
    flush_rate = 5
    print("rspbot: Monitoring new submissions...")
    for n, submission in enumerate(subreddit.stream.submissions()):
        # when starting check if submission is present in index as
        # as oldest submissions are yielded first.
        if submission.id in token_vector['index']:
            continue
        rs.save_submission(rs.get_submission_output(submission),
            submission.id, submissions_data_path)
        token_vector['index'].append(submission.id)
        token_vector['vector'] = learn.update_token_vector(token_vector['vector'],
            learn.get_tokens_vector([submission.title]))
        if n % flush_rate == 0:
            # update vector with new submissions
            learn.save_token_vector(cache_vector_file, token_vector)
        recommended_items = list(get_recommended_items(token_vector,
            submissions_data_path))
        if len(recommended_items) > 0:
            print("rspbot: Related posts for \"{}\" :".format(submission.title))
            for item in recommended_items:
                print("TITLE: \"{}\"".format(item[0]))
                print("URL: \"{}\"".format(item[1]))
            print()
