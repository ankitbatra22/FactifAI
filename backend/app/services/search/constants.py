# Bad domains to exclude
EXCLUDED_DOMAINS = {
    'reddit.com', 'quora.com', 'pinterest.com', 
    'facebook.com', 'twitter.com', 'instagram.com',
    'tiktok.com', 'youtube.com', 'medium.com', 'linkedin.com',
    'towardsdatascience.com', 'wikihow.com', 'wikipedia.org',
    'yahoo.answers.com', 'answers.com', 'answers.yahoo.com',
    'buzzfeed.com', 'boredpanda.com', 'huffpost.com'
}

# URL patterns to exclude
EXCLUDED_URL_PATTERNS = [
    # Discussion/Forum indicators
    'forum', 'thread', 'discussion', 'community', 'comments',
    'board', 'topic', 'message', 'chat', 'conversation', 'talk',
    
    # Social/Q&A
    'reddit', 'quora', 'answers', 'ask', 'stackexchange', 'wikipedia', 'wiki', 
    
    # User-generated content
    'blog', 'post', 'question', 'responses', 'replies', 'talk', 'kids',
]
