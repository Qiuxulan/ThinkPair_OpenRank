SELECT repo_name AS n, COUNT(*) AS c
FROM opensource.events
WHERE (type = 'PullRequestReviewCommentEvent' AND pull_review_comment_updated_at >= now() - INTERVAL 1 MONTH) 
    AND platform = 'GitHub'
    AND action = 'created'
GROUP BY n
ORDER BY c DESC
LIMIT 300
