import json


def getIssueCommentEvent(record):

    actor_id = record['actor']['id']
    issue_id = record['payload']['issue']['id']
    comment = record['payload']['comment']

    return (
        comment["id"],
        actor_id,
        issue_id,
        comment["created_at"],
        comment["updated_at"],
        comment["body"].replace(
            "\x00", "\uFFFD") if comment["body"] else None,
        json.dumps(comment['reactions']),
    )


def getIssuesEvent(record):
    rep_id = record['repo']['id']
    actor_id = record['actor']['id']
    issue = record['payload']['issue']

    return (
        issue['id'],
        actor_id,
        rep_id,
        issue['created_at'],
        issue['updated_at'],
        issue['closed_at'],
        issue['number'],
        issue['title'].replace(
            "\x00", "\uFFFD") if issue["title"] else None,
        issue['body'].replace(
            "\x00", "\uFFFD") if issue["body"] else None,
        json.dumps(issue['reactions']),
        issue['state'][:50],
        [label["name"][:50].replace(
            "\x00", "\uFFFD") if label["name"] else None for label in issue['labels']],
    )
