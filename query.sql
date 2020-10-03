EXPLAIN ANALYZE SELECT * FROM accounts WHERE screen_name = 'realDonaldTrump';

SET max_parallel_workers_per_gather TO 3;

CREATE INDEX ON accounts (screen_name);

EXPLAIN ANALYZE SELECT * FROM accounts WHERE followers_count >= 100 AND followers_count <= 200;

CREATE INDEX ON accounts (followers_count);

EXPLAIN ANALYZE SELECT * FROM accounts WHERE followers_count >= 100 AND followers_count <= 1000;

CREATE INDEX ON accounts (name);
CREATE INDEX ON accounts (friends_count);
CREATE INDEX ON accounts (description);

INSERT INTO accounts (id, screen_name, name, description, followers_count, friends_count, statuses_count) VALUES (1, 'moj pouzivatel', 'moj_pouzivatel', 'moj pouzivatel', 100, 10, 1);

drop index accounts_screen_name_idx;
drop index accounts_followers_count_idx;
drop index accounts_name_idx;
drop index accounts_friends_count_idx;
drop index accounts_description_idx;

INSERT INTO accounts (id, screen_name, name, description, followers_count, friends_count, statuses_count) VALUES (2, 'to je jedno', 'to_je_jedno', 'To je jedno ake data', 200, 20, 2);

CREATE INDEX ON tweets (retweet_count);
CREATE INDEX ON tweets (content);

create extension pageinspect;
select * from bt_metap('tweets_content_idx');
select type, live_items, dead_items, avg_item_size, page_size, free_size from bt_page_stats('tweets_content_idx',1000)
select itemoffset, itemlen, data from bt_page_items('tweets_content_idx',1) limit 1000;


select * from bt_metap('tweets_retweet_count_idx');
select type, live_items, dead_items, avg_item_size, page_size, free_size from bt_page_stats('tweets_retweet_count_idx',1000)
select itemoffset, itemlen, data from bt_page_items('tweets_retweet_count_idx',1) limit 1000;


select * from bt_metap('accounts_followers_count_idx');
select type, live_items, dead_items, avg_item_size, page_size, free_size from bt_page_stats('accounts_followers_count_idx',1000)
select itemoffset, itemlen, data from bt_page_items('accounts_followers_count_idx',1) limit 1000;


select * from bt_metap('accounts_screen_name_idx');
select type, live_items, dead_items, avg_item_size, page_size, free_size from bt_page_stats('accounts_screen_name_idx',1000)
select itemoffset, itemlen, data from bt_page_items('accounts_screen_name_idx',1) limit 1000;