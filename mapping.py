mapping = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 2,
        "max_ngram_diff": 9,
        "analysis": {
            "analyzer": {
                "englando": {
                    "tokenizer": "standard",
                    "filter": [
                        "english_possessive_stemmer",
                        "lowercase",
                        "english_stop",
                        "english_stemmer"
                    ],
                    "char_filter": "html_strip"
                },
                "custom_ngram": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "asciifolding",
                        "filter_ngrams"
                    ],
                    "char_filter": "html_strip"
                },
                "custom_shingles": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "asciifolding",
                        "filter_shingles"
                    ],
                    "char_filter": "html_strip"
                }
            },
            "filter": {
                "filter_ngrams": {
                    "type": "ngram",
                    "max_gram": 10
                },
                "filter_shingles": {
                    "type": "shingle",
                    "token_separator": ""
                },
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                }
            }
        }
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {
                "type": "unsigned_long"
            },
            "created_at": {
                "type": "date",
                "format": "EEE MMM dd HH:mm:ss Z yyyy"
            },
            "full_text": {
                "type": "text",
                "analyzer": "englando"
            },
            "hashtags": {
                "type": "keyword"
            },
            "user_mentions": {
                "type": "nested",
                "dynamic": "strict",
                "properties": {
                    "screen_name": {
                        "type": "text",
                        "analyzer": "englando",
                        "fields": {
                            "ngram": {
                                "type": "text",
                                "analyzer": "custom_ngram"
                            }
                        }
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "englando",
                        "fields": {
                            "ngram": {
                                "type": "text",
                                "analyzer": "custom_ngram"
                            }
                        }
                    },
                    "id": {
                        "type": "unsigned_long"
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
            "coordinates": {
                "type": "geo_point"
            },
            "user": {
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "unsigned_long"
                    },
                    "name": {
                        "type": "text",
                        "analyzer": "custom_ngram",
                        "fields": {
                            "shingle": {
                                "type": "text",
                                "analyzer": "custom_shingles"
                            }
                        }
                    },
                    "screen_name": {
                        "type": "text",
                        "analyzer": "englando",
                        "fields": {
                            "ngram": {
                                "type": "text",
                                "analyzer": "custom_ngram"
                            }
                        }
                    },
                    "description": {
                        "type": "text",
                        "analyzer": "englando",
                        "fields": {
                            "shingle": {
                                "type": "text",
                                "analyzer": "custom_shingles"
                            }
                        }
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
            },
            "parent_id": {
                "type": "unsigned_long"
            }
        }
    }
}
