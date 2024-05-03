

def relations():
    return """ 
   ALTER TABLE "branches" ADD FOREIGN KEY ("repository_id") REFERENCES "repositories" ("id");

    ALTER TABLE "pushes" ADD FOREIGN KEY ("actor_id") REFERENCES "actors" ("id");

    ALTER TABLE "pushes" ADD FOREIGN KEY ("branch_id") REFERENCES "branches" ("id");

    ALTER TABLE "commits" ADD FOREIGN KEY ("push_id") REFERENCES "pushes" ("id");

    ALTER TABLE "watch_events" ADD FOREIGN KEY ("repository_id") REFERENCES "repositories" ("id");

    ALTER TABLE "watch_events" ADD FOREIGN KEY ("actor_id") REFERENCES "actors" ("id");

    ALTER TABLE "releases" ADD FOREIGN KEY ("actor_id") REFERENCES "actors" ("id");

    ALTER TABLE "releases" ADD FOREIGN KEY ("repository_id") REFERENCES "repositories" ("id");

    ALTER TABLE "issues" ADD FOREIGN KEY ("repository_id") REFERENCES "repositories" ("id");

    ALTER TABLE "issues" ADD FOREIGN KEY ("actor_id") REFERENCES "actors" ("id");

    ALTER TABLE "issue_comments" ADD FOREIGN KEY ("actor_id") REFERENCES "actors" ("id");

    ALTER TABLE "issue_comments" ADD FOREIGN KEY ("issue_id") REFERENCES "issues" ("id");

    ALTER TABLE "pull_requests" ADD FOREIGN KEY ("repository_id") REFERENCES "repositories" ("id");

    ALTER TABLE "pull_requests" ADD FOREIGN KEY ("actor_id") REFERENCES "actors" ("id");

    ALTER TABLE "page_changes" ADD FOREIGN KEY ("actor_id") REFERENCES "actors" ("id");

    ALTER TABLE "page_changes" ADD FOREIGN KEY ("page_id") REFERENCES "pages" ("id");

    ALTER TABLE "pull_request_reviews" ADD FOREIGN KEY ("actor_id") REFERENCES "actors" ("id");

    ALTER TABLE "pull_request_reviews" ADD FOREIGN KEY ("pull_request_id") REFERENCES "pull_requests" ("id");

    ALTER TABLE "pull_request_review_comments" ADD FOREIGN KEY ("actor_id") REFERENCES "actors" ("id");

    ALTER TABLE "pull_request_review_comments" ADD FOREIGN KEY ("pull_request_review_id") REFERENCES "pull_request_reviews" ("id");

    ALTER TABLE "pull_request_members" ADD FOREIGN KEY ("actor_id") REFERENCES "actors" ("id");

    ALTER TABLE "pull_request_members" ADD FOREIGN KEY ("pull_request_id") REFERENCES "pull_requests" ("id");

    ALTER TABLE "contributors" ADD FOREIGN KEY ("repository_id") REFERENCES "repositories" ("id");

    ALTER TABLE "contributors" ADD FOREIGN KEY ("actor_id") REFERENCES "actors" ("id");
    """
