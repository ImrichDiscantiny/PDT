
from issues import *
from pull_requests import *
from dotenv import load_dotenv

import time

import psycopg2
from psycopg2.extras import execute_batch
import orjson
import sys
import os
import gzip
from models import models, model_relations

sys.path.append('/models')

load_dotenv()


def get_connection():

    return psycopg2.connect(host=os.getenv('HOST'),
                            database=os.getenv('DBNAME'),
                            user=os.getenv('DBUSER'),
                            password=os.getenv('PASSWORD'),
                            port=os.getenv('PORT'))


def getWatchEvent(record):

    rep_id = record['repo']['id']
    actor_id = record['actor']['id']

    return (actor_id, rep_id)


def getReleaseEvent(record):

    rep_id = record['repo']['id']
    actor_id = record['actor']['id']
    release = record['payload']['release']

    return (
        release['id'],
        actor_id,
        rep_id,
        release['created_at'],
        release['published_at'],
        release['draft'],
        release['prerelease'],
        release['tag_name'][:50].replace("\x00", "\uFFFD"),
        release['name'][:50].replace(
            "\x00", "\uFFFD") if release['name'] else None,
        release['body'].replace("\x00", "\uFFFD") if release['body'] else None
    )


def getPages(record):

    rep_id = record['repo']['id']
    actor_id = record['actor']['id']

    return ()


def parseQueries(connection, target_file):

    actor_data = []
    repo_data = []

    branch_data = []
    pushes_data = []
    commits_data = []
    contributor_data = []

    release_data = []
    watch_data = []

    issues_data = []
    issues_comment_data = []

    pull_request_data = []
    pull_members_data = []

    pull_request_review_data = []
    pull_request_review_comments_data = []

    f_in = gzip.open(target_file, 'rb')

    for line in f_in:
        record = orjson.loads(line)

        actor = record['actor']
        rep = record['repo']

        actor_tuple = (actor['id'], actor['gravatar_id'], actor['login'],
                       actor['display_login'], actor['url'], actor['avatar_url'])

        actor_data.append(actor_tuple)

        repo_data.append((rep['id'], rep['name'], rep['url']))

        match  record['type']:

            case  "PushEvent":
                rep_id = rep['id']
                actor_id = actor['id']
                payload = record['payload']
                created_at = record['created_at']
                branch_id = str(rep_id) + payload['ref']

                branch_data.append((branch_id, rep_id, payload['ref'][:255]))

                pushes_data.append((payload['push_id'], branch_id, actor_id,
                                    payload['size'], payload['distinct_size'], created_at))

                for commit in payload['commits']:
                    commit_data = (
                        payload['push_id'], commit['author']['name'][:255],
                        commit['author']['email'][:255], commit['message'].replace(
                            "\x00", "\uFFFD") if commit['message'] else None, commit['sha'])
                    commits_data.append(commit_data)

                contributor_id = str(actor_id) + '_' + str(rep_id)
                contributor_data.append(
                    (contributor_id, actor_id, rep_id))

            case "ReleaseEvent":
                release_tuple = getReleaseEvent(record)
                release_data.append(release_tuple)

            case "WatchEvent":
                watch_tuple = getWatchEvent(record)
                watch_data.append(watch_tuple)

            case "IssuesEvent":
                issue_tuple = getIssuesEvent(record)
                issues_data.append(issue_tuple)

            case "IssueCommentEvent":
                if "issue" in record["payload"]:
                    issue_tuple = getIssuesEvent(record)
                    issues_data.append(issue_tuple)

                    comment_tuple = getIssueCommentEvent(record)
                    issues_comment_data.append(comment_tuple)

            case "PullRequestEvent":
                pull_tuple = getPullRequest(record)
                pull_request_data.append(pull_tuple)

                members = getPullRequestMembers(record)
                pull_members_data.append(members)

            case "PullRequestReviewEvent":
                pull_review_tuple = getPullRequestReview(record)
                pull_request_review_data.append(pull_review_tuple)

            case "PullRequestReviewCommentEvent":
                pull_commment_tuple = getPullRequestReviewComment(record)
                pull_request_review_comments_data.append(pull_commment_tuple)

    actor_query = "INSERT INTO actors  (id, gravatar, login, display_login, url, avatar_url) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING"

    repo_query = "INSERT INTO repositories (id, name, url) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING"

    branch_query = "INSERT INTO branches (id, repository_id, name) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING"

    push_query = "INSERT INTO pushes (id, branch_id, actor_id, size, distinct_size, created_at) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING"

    commit_query = "INSERT INTO commits (push_id, author_name, author_email, message, sha) VALUES (%s, %s, %s, %s, %s)"

    contributor_query = """INSERT INTO contributors (id ,actor_id, repository_id) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING"""

    release_query = """
        INSERT INTO releases 
        (id, actor_id, repository_id, created_at, published_at, is_draft, is_prerelease, tag_name, release_name, body)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET published_at = EXCLUDED.published_at, is_draft = EXCLUDED.is_draft, is_prerelease = EXCLUDED.is_prerelease;
        """

    watch_query = "INSERT INTO watch_events (actor_id, repository_id) VALUES (%s, %s)"

    issues_query = """
        INSERT INTO issues 
        (id, actor_id, repository_id, created_at, updated_at, closed_at, number, title, body, reactions, state, labels)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET title = EXCLUDED.title,
            updated_at = EXCLUDED.updated_at,
            closed_at = EXCLUDED.closed_at,
            state = EXCLUDED.state,
            body = EXCLUDED.body,
            reactions = EXCLUDED.reactions::jsonb,
            labels = EXCLUDED.labels
        """

    issue_comment_query = """
        INSERT INTO issue_comments (id, actor_id, issue_id, created_at, updated_at, body, reactions) 
        VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
        ON CONFLICT (id) DO UPDATE
        SET updated_at = EXCLUDED.updated_at, 
            body = EXCLUDED.body, 
            reactions = EXCLUDED.reactions::jsonb;
       
    """

    pull_request_query = """
        INSERT INTO pull_requests (id, actor_id, repository_id, created_at, updated_at, closed_at, merged_at, title, number, body, additions, deletions, changed_files, state, labels) VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET title = EXCLUDED.title,
            updated_at = EXCLUDED.updated_at,
            closed_at = EXCLUDED.closed_at,
            merged_at = EXCLUDED.merged_at,
            body = EXCLUDED.body,
            state = EXCLUDED.state,
            labels = EXCLUDED.labels,
            additions = EXCLUDED.additions,
            deletions = EXCLUDED.deletions,
            changed_files = EXCLUDED.changed_files
        """

    pull_members_query = """
        INSERT INTO pull_request_members (id, actor_id, pull_request_id, member_type) VALUES (%s,%s, %s, %s) ON CONFLICT (id) DO NOTHING
    """

    pull_reviews_query = """
        INSERT INTO pull_request_reviews (id, actor_id, pull_request_id, submitted_at, body, state) 
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET body = EXCLUDED.body, 
            state = EXCLUDED.state;
    """

    pull_comments_query = """
        INSERT INTO pull_request_review_comments (id, actor_id, pull_request_review_id, created_at, updated_at, body, path, reactions)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET updated_at = EXCLUDED.updated_at,
            body = EXCLUDED.body,
            reactions = EXCLUDED.reactions::jsonb;
        """

    with connection.cursor() as cursor:
        execute_batch(cursor, actor_query, actor_data, page_size=2000)
        execute_batch(cursor, repo_query, repo_data, page_size=2000)

        execute_batch(cursor, branch_query, branch_data, page_size=2000)
        execute_batch(cursor, push_query, pushes_data, page_size=2000)

        execute_batch(cursor, commit_query, commits_data, page_size=2000)
        execute_batch(cursor, contributor_query,
                      contributor_data, page_size=2000)

        execute_batch(cursor, watch_query, watch_data, page_size=2000)
        execute_batch(cursor, release_query, release_data, page_size=2000)
        execute_batch(cursor, issues_query, issues_data, page_size=2000)
        execute_batch(cursor, issue_comment_query,
                      issues_comment_data, page_size=2000)
        execute_batch(cursor, pull_request_query,
                      pull_request_data, page_size=2000)
        execute_batch(cursor, pull_members_query,
                      pull_members_data, page_size=2000)
        execute_batch(cursor, pull_reviews_query,
                      pull_request_review_data, page_size=2000)
        execute_batch(cursor, pull_comments_query,
                      pull_request_review_comments_data, page_size=2000)

    connection.commit()
    print('finished')


def getFileNames():

    connection = get_connection()

    start_type = input("Type input where 0 - delete database, else continue ")

    if start_type == '0':
        cursor = connection.cursor()

        cursor.execute(models.create_tables())

        connection.commit()
        cursor.close()

        read = True
    else:
        read = False

    folder_path = "events_raw"

    for data_file in os.listdir(folder_path):

        if read:

            target = folder_path + '/' + data_file
            print(data_file)

            start = time.time()

            parseQueries(connection, target)

            end = time.time()

            print("Elapsed time: ", (end - start))

    cursor = connection.cursor()

    cursor.execute(model_relations.relations())

    connection.commit()
    cursor.close()

    connection.close()


getFileNames()
