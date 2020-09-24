CREATE TABLE IF NOT EXISTS accounts (
	id 				bigint PRIMARY KEY,
	screen_name		varchar(200),
	name			varchar(200),
	description		text,
	followers_count	integer,
	friends_count	integer,
	statuses_count	integer
);

CREATE TABLE IF NOT EXISTS countries (
	id 				serial PRIMARY KEY,
	code			varchar(2),
	name			varchar(200)
);

CREATE TABLE IF NOT EXISTS hashtags (
	id 				serial PRIMARY KEY,
	value			text UNIQUE
);

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS tweets (
	id				varchar(200) PRIMARY KEY,
	content 		text,
	location 		geometry(point,4326),
	retweet_count 	integer,
	favorite_count 	integer,
	happened_at 	timestamp with time zone,
	author_id 		bigint,
	country_id 		integer,
	parent_id 		varchar(20)	
);

CREATE TABLE IF NOT EXISTS tweet_mentions (
	id				serial PRIMARY KEY,
	account_id 		bigint,
	tweet_id 		varchar(20)	
);

CREATE TABLE IF NOT EXISTS tweet_hashtags (
	id				serial PRIMARY KEY,
	hashtag_id 		bigint,
	tweet_id 		varchar(20)	
);