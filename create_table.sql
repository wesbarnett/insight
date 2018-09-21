
drop table if exists submissions_0;
drop table if exists submissions_1;
drop table if exists submissions_2;

select title, selftext, subreddit into submissions_0 from submissions
where is_self = 'True'
and selftext <> '[deleted]'
and selftext <> '[removed]'
and subreddit in (select display_name from subreddits where subscribers > 130000)
order by random();

select title, selftext, subreddit into submissions_1 from submissions
where is_self = 'True'
and selftext <> '[deleted]'
and selftext <> '[removed]'
and subreddit in (select display_name from subreddits where subscribers <= 130000 and subscribers > 55000)
order by random();

select title, selftext, subreddit into submissions_2 from submissions
where is_self = 'True'
and selftext <> '[deleted]'
and selftext <> '[removed]'
and subreddit in (select display_name from subreddits where subscribers <= 55000 and subscribers > 33000)
order by random();
