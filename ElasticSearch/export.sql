-- CREATE MATERIALIZED VIEW r1000 as 
-- (
--     SELECT repositories.id
-- 	FROM repositories
-- 	INNER JOIN (
-- 		SELECT r.id, COUNT(c.id) as cnt
-- 		FROM repositories r
-- 		JOIN branches b ON r.id = b.repository_id
-- 		JOIN pushes p ON b.id = p.branch_id
-- 		JOIN commits c ON p.id = c.push_id
-- 		GROUP BY r.id
-- 	) as r on r.id = repositories.id
-- 	ORDER BY cnt desc
-- 	LIMIT 1000
-- ) WITH DATA;

COPY
(
	SELECT row_to_json(outputs)
	FROM
	(
		SELECT
		r.id,
		r.name,
		b.branches,
		rel.releases,
		i.issues,
		pr.pull_requests
		FROM
		(
			SELECT
			b.repository_id,
			jsonb_agg(
				jsonb_build_object(
					'id', b.id,
					'name', b.name,
					'pushes', p.pushes
				)
			) as branches

			FROM
			(
				SELECT
				p.branch_id,
				jsonb_agg(
					jsonb_build_object(
						'id', p.id,
						'actor_login', a.login,
						'size', p.size,
						'distinct_size', p.distinct_size,
						'created_at', p.created_at,
						'commits', c.commits
					)
				) as pushes
				FROM
				(
					SELECT
						cranks.push_id,
						jsonb_agg(
							jsonb_build_object(
								'id', cranks.id,
								'message', cranks.message,
								'author_name', cranks.author_name,
								'author_email', cranks.author_email
							)
						) as commits
					FROM
					(
						SELECT
							c.id, c.push_id, c.message, c.author_name, c.author_email, rank() OVER (PARTITION BY r.id ORDER BY c.id DESC)
						FROM
							r1000 as r
						LEFT JOIN branches as b on b.repository_id = r.id
						LEFT JOIN pushes as p ON b.id = p.branch_id
						LEFT JOIN commits as c ON p.id = c.push_id
					) as cranks 
					WHERE cranks.rank < 10000
					GROUP BY 1
				) as c
				LEFT JOIN pushes as p ON p.id = c.push_id
				LEFT JOIN actors as a ON a.id = p.actor_id
				GROUP BY 1
			) as p
			LEFT JOIN branches as b ON b.id = p.branch_id
			GROUP BY 1
		) as b
		LEFT JOIN repositories as r ON r.id = b.repository_id
		LEFT JOIN (
				SELECT
				pr.repository_id,
				jsonb_agg(
					jsonb_build_object(
						'actor_login', a.login,
						'title', pr.title,
						'number', pr.number,
						'body', pr.body,
						'created_at', pr.created_at,
						'updated_at', pr.updated_at,
						'closed_at', pr.closed_at,
						'merged_at', pr.merged_at,
						'additions', pr.additions,
						'deletions', pr.deletions,
						'changed_files', pr.changed_files,
						'id', pr.id,
						'state', pr.state,
						'labels', pr.labels,
						'pull_request_reviews', prr.reviews
					) 
				) as pull_requests
			FROM
			(
				SELECT
					prr.pull_request_id,
					jsonb_agg(
						jsonb_build_object(
							'actor_login', a.login,
							'body', prr.body,
							'submitted_at', prr.submitted_at,
							'id', prr.id,
							'state', prr.state,
							'pull_request_review_comments', prrc.comments
						)
					) as reviews
				FROM
				(
					SELECT
						prrc.pull_request_review_id,
						jsonb_agg( 
							jsonb_build_object(
								'actor_login', a.login,
								'body', prrc.body,
								'path', prrc.path,
								'reactions', prrc.reactions,
								'created_at', prrc.created_at,
								'updated_at', prrc.updated_at,
								'id', prrc.id
							)
						) as comments
					FROM r1000 as r
					LEFT JOIN pull_requests as pr ON pr.repository_id = r.id
					LEFT JOIN pull_request_reviews as prr ON prr.pull_request_id = pr.id
					LEFT JOIN pull_request_review_comments as prrc ON prrc.pull_request_review_id = prr.id
					LEFT JOIN actors as a ON a.id = prrc.actor_id
					GROUP BY 1
				) as prrc
				LEFT JOIN pull_request_reviews as prr ON prr.id = prrc.pull_request_review_id
				LEFT JOIN actors as a ON a.id = prr.actor_id
				GROUP BY 1
			) as prr
			LEFT JOIN pull_requests as pr ON pr.id = prr.pull_request_id
			LEFT JOIN actors as a ON a.id = pr.actor_id
			GROUP BY 1

		) as pr on pr.repository_id = r.id

		LEFT JOIN (
			SELECT 
			i.repository_id,
			jsonb_agg(
				jsonb_build_object(
					'actor_login',  a.login,
					'title', i.title,
					'number', i.number,
					'created_at', i.created_at,
					'updated_at', i.updated_at,
					'closed_at', i.closed_at,
					'body', i.body,
					'reactions', i.reactions,
					'id', i.id,
					'labels', i.labels,
					'state', i.state,
					'issue_comments', ic.issue_comments
				)
			) as issues
			FROM 
			(
				SELECT
					ic.issue_id,
					jsonb_agg(
						jsonb_build_object(
							'actor_login', a.login,
							'body', ic.body,
							'reactions', ic.reactions,
							'created_at', ic.created_at,
							'updated_at', ic.updated_at,
							'id', ic.id
						)
					) as issue_comments
				FROM
				r1000 as r
				LEFT JOIN issues as i ON i.repository_id = r.id
				LEFT JOIN issue_comments as ic ON ic.issue_id = i.id
				LEFT JOIN actors as a ON a.id = ic.actor_id
				GROUP BY 1
			) as ic
			LEFT JOIN issues as i ON i.id = ic.issue_id
			LEFT JOIN actors as a ON a.id = i.actor_id
			GROUP BY 1
		) as i on i.repository_id = r.id


		LEFT JOIN (
			SELECT
				re.repository_id,
				jsonb_agg(
					jsonb_build_object(
						'actor_login', a.login,
						'is_prerelease', re.is_prerelease,
						'is_draft', re.is_draft,
						'published_at', re.published_at,
						'created_at', re.created_at,
						'body', re.body,
						'tag_name', re.tag_name,
						'release_name', re.release_name
					)
				) as releases
				FROM r1000 as r
				LEFT JOIN releases as re ON re.repository_id = r.id
				LEFT JOIN actors as a ON a.id = re.actor_id
				GROUP BY 1
		) as rel ON rel.repository_id = r.id
	) as outputs
)
TO 'D:/repositories.json';