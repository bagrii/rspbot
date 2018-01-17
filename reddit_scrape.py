# Scrape subreddit in a set of JSON files which represents one submission
# per file with all comments.

# here is the JSON structure:
# {
#   'permalink': <post URL relative to reddit domain name>,
#   'title': <post title >,
#   'created': <post creation date>,
#   'url': <post URL>,
#   'body': <post text, can be empty>,
#   'ups': <post upvotes>,
#   'comments': [ { 'body': <comment text>, 'ups': <comment upvotes>,
#                   'comments': <comment replies> } ]
# }


import praw
import json
import os

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

def add_comment_tree(root_comment, all_comments):
    comment_prop = {'body': root_comment.body,
                    'ups': root_comment.ups}
    if root_comment.replies:
        comment_prop['comments'] = list()
        for reply in root_comment.replies:
            add_comment_tree(reply, comment_prop['comments'])
    all_comments.append(comment_prop)

def get_submission_output(submission):
    return {
            'permalink': submission.permalink,
            'title': submission.title,
            'created': submission.created,
            'url': submission.url,
            'body': submission.selftext,
            'ups': submission.ups,
            'comments': list()
        }

def save_submission(output, submission_id, output_path):
    # flush to file  with submission id as name
    out_file = os.path.join(output_path, submission_id + ".json")
    with open(out_file, "w") as fp:
        json.dump(output, fp)

def parse_subreddit(subreddit, output_path, include_comments=True):
    reddit = praw.Reddit(user_agent=auth['user_agent'], client_id=auth['client_id'],
        client_secret=auth['secret_id'])
    subreddit = reddit.subreddit(subreddit)
    submissions = subreddit.submissions()
    for submission in submissions:
        print("Working on ... ", submission.title)
        output = get_submission_output(submission)
        if include_comments:
            submission.comments.replace_more(limit=0)
            for comment in submission.comments:
                add_comment_tree(comment, output['comments'])
        # flush to file  with submission id as name
        save_submission(output, submission.id, output_path)

if __name__ == '__main__':
    parse_subreddit("smallbusiness", "/tmp/smallbusiness/", include_comments=False)
