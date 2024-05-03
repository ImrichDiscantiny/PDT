
def create_tables():
    return """
  DROP SCHEMA public CASCADE;
    CREATE SCHEMA public;

    CREATE TABLE "actors" (
      "gravatar" text,
      "url" text,
      "avatar_url" text,
      "id" bigint PRIMARY KEY,
      "login" varchar(255),
      "display_login" varchar(255)
    );


    CREATE TABLE "repositories" (
      "url" text,
      "id" bigint PRIMARY KEY,
      "name" varchar(255)
    );

    CREATE TABLE "branches" (
      "repository_id" bigint,
      "id" text PRIMARY KEY,
      "name" varchar(255)
    );


    CREATE TABLE "pushes" (
      "branch_id" text,
      "actor_id" bigint,
      "size" integer,
      "distinct_size" integer,
      "created_at" timestamp,
      "id" bigint PRIMARY KEY
    );


    CREATE TABLE "commits" (
      "push_id" bigint,
      "message" text,
      "id" BIGSERIAL PRIMARY KEY,
      "author_name" varchar(255),
      "author_email" varchar(255),
      "sha" varchar(100)
    );


    CREATE TABLE "watch_events" (
      "actor_id" bigint,
      "repository_id" bigint,
      "id" BIGSERIAL PRIMARY KEY
    );

    CREATE TABLE "contributors" (
      "id" text PRIMARY KEY,
      "actor_id" bigint,
      "repository_id" bigint
    );

    CREATE TABLE "releases" (
      "actor_id" bigint,
      "repository_id" bigint,
      "is_prerelease" boolean,
      "is_draft" boolean,
      "published_at" timestamp,
      "created_at" timestamp,
      "body" text,
      "id" bigint PRIMARY KEY,
      "tag_name" varchar(50),
      "release_name" varchar(50)
    );

    CREATE TABLE "issues" (
      "actor_id" bigint,
      "repository_id" bigint,
      "title" text,
      "number" integer,
      "created_at" timestamp,
      "updated_at" timestamp,
      "closed_at" timestamp,
      "body" text,
      "reactions" jsonb,
      "id" bigint PRIMARY KEY,
      "labels" varchar[],
      "state" varchar(50)
    );

    CREATE TABLE "issue_comments" (
      "issue_id" bigint,
      "actor_id" bigint,
      "body" text,
      "reactions" jsonb,
      "created_at" timestamp,
      "updated_at" timestamp,
      "id" bigint PRIMARY KEY
    );


    CREATE TABLE "pull_requests" (
      "actor_id" bigint,
      "repository_id" bigint,
      "title" text,
      "number" integer,
      "body" text,
      "created_at" timestamp,
      "updated_at" timestamp,
      "closed_at" timestamp,
      "merged_at" timestamp,
      "additions" integer,
      "deletions" integer,
      "changed_files" integer,
      "id" bigint PRIMARY KEY,
      "state" varchar(50),
      "labels" varchar []
    );


  CREATE TABLE "pull_request_reviews" (
    "actor_id" bigint,
    "pull_request_id" bigint,
    "body" text,
    "submitted_at" timestamp,
    "id" bigint PRIMARY KEY,
    "state" varchar(50)
  );

  CREATE TABLE "pull_request_review_comments" (
    "actor_id" bigint,
    "pull_request_review_id" bigint,
    "body" text,
    "path" text,
    "reactions" jsonb,
    "created_at" timestamp,
    "updated_at" timestamp,
    "id" bigint PRIMARY KEY
  );

  CREATE TYPE memberType AS ENUM ('OWNER','CONTRIBUTOR', 'COLLABORATOR', 'NONE', 'MEMBER' );

  CREATE TABLE "pull_request_members" (
    "member_type" memberType,
    "actor_id" bigint,
    "pull_request_id" bigint,
    "id" text PRIMARY KEY
  );

  CREATE TABLE "pages" (
    "url" text,
    "id" bigint PRIMARY KEY,
    "name" varchar(255)
  );

  CREATE TABLE "page_changes" (
    "page_id" bigint,
    "actor_id" bigint,
    "summary" text,
    "created_at" timestamp,
    "id" bigint PRIMARY KEY,
    "action" varchar(50),
    "sha" varchar(100)
  );
  
  """
