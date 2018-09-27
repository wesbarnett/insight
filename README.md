# /r/eveal

/r/eveal is a Chrome extension to enhance the user experience on Reddit by helping users
discover new communities based on the content they are submitting or viewing.

Reddit is a social media site where users engage in discussions in communities call
subreddits, often denoted by `/r/*community_name*`. However, it's difficult to weed
through all of the 900,000+ subreddits out there and find new communities other than the
most popular ones.

## Installation and usage

Install the Chrome extension from
[here](https://chrome.google.com/webstore/detail/subreddits-with-content-l/iaepjdnahmaliipimelmheobbdeplhah).

After installing the Chrome extension simply visit Reddit and prepare to submit your
text post from any subreddit or from
[here](https://old.reddit.com/submit?selftext=true). While typing in your new
submission, subreddits with similar content will show up below the input.

[![Screenshot of submissions page](https://raw.githubusercontent.com/wesbarnett/insight/master/screenshots/screenshot4.png | width=100)](https://raw.githubusercontent.com/wesbarnett/insight/master/screenshots/screenshot4.png)

If you want to submit your content to one of those subreddits, click the link indicating
the subreddit and a new window with your post content will popup where you can submit
your content!

Suggestions of similar communities of content you view will also be shown automatically.

**Note:** The extension does not work on the redesigned Reddit interface. Ensure that
the checkbox "Use the redesign as my default experience" is unchecked on your
[preferences page](https://www.reddit.com/prefs).

## About the model

Supervised learning models were trained on subsets of the May 2018 Reddit data corpus
found [here](https://files.pushshift.io/reddit/). I removed all over-18 communities and
posts and only trained on "self text" posts that were not deleted or removed. I used
three models for three different groupings of subreddits based on the number of
subscribers of those subreddits. 

I used a bag-of-words approach using [scikit-learn](http://scikit-learn.org/stable/)'s
HashingVectorizer with 2^(18) features and L1 normalization. The text of the title and
of the post itself were used in this feature vectorization. The subreddit names were
used as the labels. I attempted using out-of-core Naive Bayes, but ran into memory usage
when training, even on the reduced training sets. I also tried Logistic Regression with
Stochastic Gradient Descent (SGD) but the resulting models took up several GB of disk
space. In the end, SGD with Support Vector Machine was used for classifying the posts in
all of the models due to its fast predictions and low disk space.

