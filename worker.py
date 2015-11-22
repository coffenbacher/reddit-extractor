import rethinkdb as r
import delorean
from bigquery import get_client
from delorean import stops, parse, Delorean, epoch
from datetime import timedelta
from retrying import retry
import itertools
import time
import datetime
import sys
import os
import praw
import logging; logger=logging.getLogger(); logger.setLevel('INFO'); logging.basicConfig()

# Global helpers
c = r.connect(os.getenv('RETHINKDB_HOST', 'rethinkdb.reddit-analyzer'), os.getenv('RETHINKDB_PORT', 28015))
UA = '/r/%s flair analyzer by /u/coffenbacher for https://charlesoffenbacher.com' % sys.argv[1]
pr = praw.Reddit(user_agent=UA)
db = r.db('reddit')

client = get_client(os.getenv('BIGQUERY_PROJECT_ID'), 
                    service_account=os.getenv('BIGQUERY_SERVICEACCOUNT_ID'),
                    private_key_file=os.getenv('BIGQUERY_PRIVATEKEY_FILE'), 
                    readonly=False)

# Helper
def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return ([e for e in t if e != None] for t in itertools.izip_longest(*args))

def get_submissions_between_epochs(start, end, subreddit):
    logger.info('Running search for range %s->%s' % (epoch(start).datetime.strftime('%x'), epoch(end).datetime.strftime('%x')))
    query = 'timestamp:%d..%d' % (start, end)
    return pr.search(query, subreddit=subreddit, sort='new', limit=1000, syntax='cloudsearch')

def get_bq_submission(s):
    return {
            'id': s.id,
            'author': s.author.name,
            'created_utc': s.created_utc,
            'link_flair_text': s.link_flair_text,
            'author_flair_text': s.author_flair_text,
            'num_comments': s.num_comments,
            'score': s.score,
            'ups': s.ups,
            'downs': s.downs,
            'selftext': s.selftext,
            'title': s.title,
            'gilded': s.gilded,
            'subreddit': s.subreddit.name,
            'name': s.name
        }

def get_bq_comment(comment):
    return {
            'id': comment.id,
            'author': comment.author.name,
            'created_utc': comment.created_utc,
            'link_id': comment.link_id,
            'link_flair_text': comment.submission.link_flair_text,
            'author_flair_text': comment.author_flair_text,
            'score': comment.score,
            'ups': comment.ups,
            'downs': comment.downs,
            'body': comment.body,
            'gilded': comment.gilded,
            'subreddit': comment.subreddit.name,
            'name': comment.name
           }

def extract_data(subreddit, epoch_increment=86400):
    current_progress = db.table('progress').get('current_%s' % subreddit).run(c)
    start = current_progress.get('epoch')
    end = start + epoch_increment
    
    submissions = []
    for s in get_submissions_between_epochs(start, end, subreddit):
        logger.info('Inserting submission %s' % s.id)
        submissions.append(get_bq_submission(s))
        
        logger.info('Getting comments for submission %s' % s.id)
        comments = []
        s.replace_more_comments(limit=None)
        for comment in praw.helpers.flatten_tree(s.comments):
            if isinstance(comment, praw.objects.Comment) and comment.author:
                print comment.id, comment.author.name
                comments.append(get_bq_comment(comment))

        for bq_comments in grouper(450, comments):
            logger.info('Inserting %s comments' % len(bq_comments))
            client.push_rows('reddit', '%s_comments' % subreddit, bq_comments, 'id')
    for bq_submissions in grouper(450, submissions):
        logger.info('Inserting %s submissions' % len(bq_submissions))
        client.push_rows('reddit', '%s_submissions' % subreddit, bq_submissions, 'id')
            
    db.table('progress').insert({'id': 'current_%s' % subreddit, 'epoch': end}, conflict="replace").run(c)
    db.table('progress').insert({'subreddit': subreddit, 'epoch': end, 'dt': r.now()}).run(c)
    
    
if __name__ == "__main__":
    logger.info('Extracting data for subreddit %s' % sys.argv[1])
    while 1:
        extract_data(sys.argv[1])
        time.sleep(int(os.getenv('DELAY', 0)))
# while 1:
#     extract_data('cfb')