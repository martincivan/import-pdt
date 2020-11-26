mapping = {
    "settings": {
        "analysis": {
            "analyzer": {
                "standard_asciifolding": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "my_ascii_folding"
                    ]
                }
            },
            "filter": {
                "my_ascii_folding": {
                    "type": "asciifolding",
                    "preserve_original": True
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "id": {
               "type": "unsigned_long"
            },
            "created_at": {
                "type": "date",
                "format": "EEE MMM dd HH:mm:ss Z yyyy"
            },
            "full_text": {
                "type": "text"
            },
            "entities": {
                "properties": {
                    "hashtags": {
                        "properties": {
                            "text": {
                                "type": "keyword"
                            },
                        }
                    },
                    "user_mentions": {
                        "properties": {
                            "screen_name": {
                                "type": "keyword"
                            },
                            "name": {
                                "type": "keyword"
                            },
                            "id": {
                                "type": "unsigned_long"
                            }
                        }
                    }
                }
            },
            "source": {
                "type": "keyword"
            },
            "in_reply_to_status_id": {
                "type": "unsigned_long"
            },
            "in_reply_to_user_id": {
                "type": "unsigned_long"
            },
            "in_reply_to_screen_name": {
                "type": "keyword"
            },
            "user": {
                "properties": {
                    "id": {
                        "type": "unsigned_long"
                    },
                    "name": {
                        "type": "keyword"
                    },
                    "screen_name": {
                        "type": "keyword"
                    },
                    "location": {
                        "type": "keyword"
                    },
                    "description": {
                        "type": "text"
                    },
                    "followers_count": {
                        "type": "integer"
                    },
                    "friends_count": {
                        "type": "integer"
                    },
                    "statuses_count": {
                        "type": "integer"
                    },
                    "created_at": {
                        "type": "date",
                        "format": "EEE MMM dd HH:mm:ss Z yyyy"
                    }
                }
            },
            "retweet_count": {
                "type": "integer"
            },
            "favorite_count": {
                "type": "integer"
            }
        }
    }
}