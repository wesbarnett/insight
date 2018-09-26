
drop table if exists submissions_0;
drop table if exists submissions_1;
drop table if exists submissions_2;
drop table if exists submissions_shuffled;

select t2.index, t1.subreddit, t1.title, t1.selftext, t1.id, t1.is_self into submissions_shuffled
from ( 
    select subreddit, title, selftext, id, is_self, row_number() over () as rn from submissions t1 
) t1
join ( 
    select index, row_number() over (order by random()) as rn from submissions t2
) t2 using (rn);

select title, selftext, subreddit, id, index into submissions_0 from submissions_shuffled
where is_self = 'True'
and selftext <> '[deleted]'
and selftext <> '[removed]'
and subreddit in (select display_name from subreddits where subscribers > 130000);

select title, selftext, subreddit, id, index into submissions_1 from submissions_shuffled
where is_self = 'True'
and selftext <> '[deleted]'
and selftext <> '[removed]'
and subreddit in (select display_name from subreddits where subscribers <= 130000 and subscribers > 55000);

select title, selftext, subreddit, id, index into submissions_2 from submissions_shuffled
where is_self = 'True'
and selftext <> '[deleted]'
and selftext <> '[removed]'
and subreddit in (select display_name from subreddits where subscribers <= 55000 and subscribers > 33000);
