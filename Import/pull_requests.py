import psycopg2
import json


def getPullRequestMembers(record):
    actor_id = record['actor']['id']
    pull_request = record['payload']['pull_request']

    return (
        str(pull_request["id"]) + ':' + record['actor']['login'],
        actor_id,
        pull_request["id"],
        pull_request["author_association"]
    )

    # else:
    #     update_issue_comment = """
    #         UPDATE pull_request_members
    #         SET member_type = %s
    #         WHERE actor_id = %s AND pull_request_id = %s
    #     """


def getPullRequestReviewComment(record):

    actor_id = record['actor']['id']
    pull_request_comment = record['payload']['comment']

    return (
        pull_request_comment['id'],
        actor_id,
        pull_request_comment['pull_request_review_id'],
        pull_request_comment["created_at"],
        pull_request_comment["updated_at"],
        pull_request_comment["body"].replace(
            "\x00", "\uFFFD") if pull_request_comment["body"] else None,
        pull_request_comment["path"],
        json.dumps(pull_request_comment['reactions']),
    )


def getPullRequestReview(record):

    actor_id = record['actor']['id']
    # print(json.dumps(record['payload'], indent=4))
    pull_request_review = record['payload']['review']
    pull_request_id = record['payload']['pull_request']['id']

    return (
        pull_request_review['id'],
        actor_id,
        pull_request_id,
        pull_request_review["submitted_at"],
        pull_request_review["body"].replace(
            "\x00", "\uFFFD") if pull_request_review["body"] else None,
        pull_request_review["state"][:50]
    )


def getPullRequest(record):

    rep_id = record['repo']['id']
    actor_id = record['actor']['id']

    pull_request = record['payload']['pull_request']

    return (

        pull_request["id"],
        actor_id,
        rep_id,
        pull_request["created_at"],
        pull_request["updated_at"],
        pull_request["closed_at"],
        pull_request["merged_at"],
        pull_request["title"].replace(
            "\x00", "\uFFFD") if pull_request["title"] else None,
        pull_request["number"],
        pull_request["body"].replace(
            "\x00", "\uFFFD") if pull_request["body"] else None,
        pull_request["additions"],
        pull_request["deletions"],
        pull_request["changed_files"],
        pull_request["state"][:50].replace(
            "\x00", "\uFFFD") if pull_request["state"] else None,
        [label["name"][:50].replace(
            "\x00", "\uFFFD") if label["name"] else None for label in pull_request['labels']]
    )
