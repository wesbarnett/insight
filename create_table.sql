select title, selftext, subreddit into submissions_large from submissions
where subreddit_subscribers > 100000
and is_self = 'True'
and selftext <> '[deleted]'
and selftext <> '[removed]'
and subreddit in (select display_name from subreddits where subscribers > 100000)
order by random();
