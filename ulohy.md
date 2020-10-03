1. Vyhľadajte v accounts screen_name s presnou hodnotou ‘realDonaldTrump’ a analyzujte daný select. Akú metódu vám vybral plánovač?
    - `SELECT * FROM accounts WHERE screen_name = 'realDonaldTrump'`
    -  `-> Parallel Seq Scan on accounts`

2. Koľko workerov pracovalo na danom selecte? Zdvihnite počet workerov a povedzte ako to  ovplyvňuje čas. Je tam nejaký strop?
    - 2 workery
    - PRED: `Planning Time: 0.044 ms
            Execution Time: 143.643 ms`
    - po zvyseni na 3: `Planning Time: 0.050 ms
                       Execution Time: 111.803 ms`
    - `SET max_parallel_workers_per_gather TO 3;`
    - po zvyseni na 8 (pouzili sa 4): `Planning Time: 0.046 ms
                       Execution Time: 93.282 ms`
    - pri viac workeroch cas klesa na, maximalne sa daju pouzit 4 workery
     
3. Vytvorte index nad screen_name a pozrite ako sa zmenil a porovnajte výstup oproti požiadavke bez indexu. Potrebuje plánovač v tejto požiadavke viac workerov? Bol tu aplikovaný nejaký filter na riadky? Prečo?
    - BEZ INDEXU:
    ```
    Gather  (cost=1000.00..88615.21 rows=1 width=122) (actual time=110.196..111.784 rows=1 loops=1)
      Workers Planned: 3
      Workers Launched: 3
      ->  Parallel Seq Scan on accounts  (cost=0.00..87615.11 rows=1 width=122) (actual time=106.591..108.339 rows=0 loops=4)
            Filter: ((screen_name)::text = 'realDonaldTrump'::text)
            Rows Removed by Filter: 867105
    Planning Time: 0.050 ms
    Execution Time: 111.803 ms
    ```
    - `CREATE INDEX ON accounts (screen_name);`
    
    - S INDEXOM:
    ```
    Index Scan using accounts_screen_name_idx on accounts  (cost=0.43..4.45 rows=1 width=122) (actual time=0.036..0.037 rows=1 loops=1)
      Index Cond: ((screen_name)::text = 'realDonaldTrump'::text)
    Planning Time: 0.133 ms
    Execution Time: 0.047 ms
    ```
    
    - Pouzije sa index scan - aplikovany filter na riadky index condition podla screen name.
    - Predlzil sa cas planovania, skratil sa cas vykonavania. Viac workerov sa nepouzije, lebo index scan s 1 podmienkou sa neda paralelizovat.

4. Vyberte používateľov, ktorý majú followers_count väčší, rovný ako 100 a zároveň menší, rovný 200. Je správanie rovnaké v prvej úlohe? Je správanie rovnaké ako  v druhej úlohe? Prečo?
    - `SELECT * FROM accounts WHERE followers_count >= 100 AND followers_count <= 200;`
    ```
    Seq Scan on accounts  (cost=0.00..125649.32 rows=428665 width=122) (actual time=2.761..474.060 rows=422237 loops=1)
      Filter: ((followers_count >= 100) AND (followers_count <= 200))
      Rows Removed by Filter: 3046184
    Planning Time: 0.048 ms
    JIT:
      Functions: 2
    "  Options: Inlining false, Optimization false, Expressions true, Deforming true"
    "  Timing: Generation 0.280 ms, Inlining 0.000 ms, Optimization 0.193 ms, Emission 2.438 ms, Total 2.911 ms"
    Execution Time: 524.913 ms
    ``` 
    - Spravanie nie je rovnake ani ako v 1. ani ako v 2. ulohe
    
5. Vytvorte index nad 4 úlohou a popíšte prácu s indexom. Čo je to Bitmap Index Scan a prečo  je tam Bitmap Heap Scan? Prečo je tam recheck condition?
    - `CREATE INDEX ON accounts (followers_count);`
    - `SELECT * FROM accounts WHERE followers_count >= 100 AND followers_count <= 200;`
    ```Bitmap Heap Scan on accounts  (cost=6750.25..86803.22 rows=428665 width=122) (actual time=49.805..466.929 rows=422237 loops=1)
         Recheck Cond: ((followers_count >= 100) AND (followers_count <= 200))
         Heap Blocks: exact=73127
         ->  Bitmap Index Scan on accounts_followers_count_idx  (cost=0.00..6643.08 rows=428665 width=0) (actual time=38.788..38.788 rows=422237 loops=1)
               Index Cond: ((followers_count >= 100) AND (followers_count <= 200))
       Planning Time: 0.144 ms
       Execution Time: 480.839 ms
    ```
   - Bitmap index scan je tam kvoli zlozenej podmienke, vytvori sa bitova maska riadkov pre 1. podmienku a pre 2. podmienku a potom sa najdu riadky, ktore vyhovuju naraz obom podmienkam
   
6. Vyberte používateľov, ktorí majú followers_count väčší, rovný ako 100 a zároveň menší, rovný 1000? V čom je rozdiel, prečo?
    - `SELECT * FROM accounts WHERE followers_count >= 100 AND followers_count <= 1000;`
    ```Bitmap Heap Scan on accounts  (cost=23780.91..120061.20 rows=1510486 width=122) (actual time=123.633..447.429 rows=1504549 loops=1)
         Recheck Cond: ((followers_count >= 100) AND (followers_count <= 1000))
         Heap Blocks: exact=73621
         ->  Bitmap Index Scan on accounts_followers_count_idx  (cost=0.00..23403.29 rows=1510486 width=0) (actual time=113.141..113.141 rows=1504549 loops=1)
               Index Cond: ((followers_count >= 100) AND (followers_count <= 1000))
       Planning Time: 0.084 ms
       JIT:
         Functions: 2
       "  Options: Inlining false, Optimization false, Expressions true, Deforming true"
       "  Timing: Generation 0.491 ms, Inlining 0.000 ms, Optimization 0.000 ms, Emission 0.000 ms, Total 0.491 ms"
       Execution Time: 493.820 ms
    ```
   - pribudol recheck cond 
   
7. Vytvorte daľšie 3 indexy na name, friends_count, a description a insertnite si  svojho používateľa (to je jedno aké dáta) do accounts. Koľko to trvalo? Dropnite indexy a spravte to ešte raz. Prečo je tu rozdiel?
    - `CREATE INDEX ON accounts (name);`
    - `CREATE INDEX ON accounts (friends_count);`
    - `CREATE INDEX ON accounts (description);`
    
    - `INSERT INTO accounts (id, screen_name, name, description, followers_count, friends_count, statuses_count) VALUES (1, 'moj pouzivatel', 'moj_pouzivatel', 'moj pouzivatel', 100, 10, 1);`
    - trvalo 17ms
    - `drop index accounts_screen_name_idx;`       
    - `drop index accounts_followers_count_idx;`
    - `drop index accounts_name_idx;`
    - `drop index accounts_friends_count_idx;`
    - `drop index accounts_description_idx;`
    - `INSERT INTO accounts (id, screen_name, name, description, followers_count, friends_count, statuses_count) VALUES (1, 'moj pouzivatel', 'moj_pouzivatel', 'moj pouzivatel', 100, 10, 1);`
    - trvalo 17ms
    - `INSERT INTO accounts (id, screen_name, name, description, followers_count, friends_count, statuses_count) VALUES (2, 'to je jedno', 'to_je_jedno', 'To je jedno ake data', 200, 20, 2);` 
    - trvalo 14ms
    - Rozdiel je, lebo pri zapise treba aj upravovat vsetky indexy, co chvilku trva.

8. Vytvorte index nad tweetami pre retweet_count a pre content. Porovnajte ich dĺžku vytvárania. Prečo je tu taký rozdiel?

    - `CREATE INDEX ON tweets (retweet_count);`
    - trvalo 8.5s
    - `CREATE INDEX ON tweets (content);`
    - trvalo 33.9s
    - Rozdiel je, lebo v 1. pripade indexujeme iba cisla, v druhom pripade indexujeme textove hodnoty
9. Porovnajte indexy pre retweet_count, content, followers_count, screen_name,... v čom sa líšia a prečo (stačí stručne)?
    - a. create extension pageinspect;
    - b. select * from bt_metap('idx_content');
    - c. select type, live_items, dead_items, avg_item_size, page_size, free_size from bt_page_stats('idx_content',1000);
    - d. select itemoffset, itemlen, data from bt_page_items('idx_content',1) limit 1000;
    
    - `select * from bt_metap('tweets_content_idx');`
    
    | magic  | version | root  | level | fastlroot | fastlevel | oldest_xact | last_cleanup_num_tuples |
    | ------ | ------- | ----  | ----- | --------- | --------- | ----------- | ----------------------- |
    | 340322 | 4       | 10338 | 4     | 10338     | 4         | 0           | -1                      |

    - `select type, live_items, dead_items, avg_item_size, page_size, free_size from bt_page_stats('tweets_content_idx',1000)`
    
    | type | live_items | dead_items | avg_item_size | page_size | free_size |
    | ---- | ---------- | ---------- | ------------- | --------- | --------- |
    | l    | 36         | 0          | 200           | 8192      | 804       |
    
    - `select itemoffset, itemlen, data from bt_page_items('tweets_content_idx',1) limit 1000;`
    
    | itemoffset | itemlen | data        |
    | ---------- | ------- | ----------- |
    | 1          | 192     | c8 08 00... |
    | 2          | 392     | f0 05 00... |
    | 3          | 48      | 4b 28 e3... |
    
    - `select * from bt_metap('tweets_retweet_count_idx');`
    
    | magic  | version | root  | level | fastlroot | fastlevel | oldest_xact | last_cleanup_num_tuples |
    | ------ | ------- | ----  | ----- | --------- | --------- | ----------- | ----------------------- |
    | 340322 | 4       | 209   | 2     | 209       | 2         | 0           | -1                      |

    - `select type, live_items, dead_items, avg_item_size, page_size, free_size from bt_page_stats('tweets_retweet_count_idx',1000)`
    
    | type | live_items | dead_items | avg_item_size | page_size | free_size |
    | ---- | ---------- | ---------- | ------------- | --------- | --------- |
    | l    | 367        | 0          | 16            | 8192      | 800       |
    
    - `select itemoffset, itemlen, data from bt_page_items('tweets_retweet_count_idx',1) limit 1000;`
    
    | itemoffset | itemlen | data                    |
    | ---------- | ------- | ----------------------- |
    | 1          | 24      | 00 00 00... 48 00 09 00 |
    | 2          | 16      | 00 00 00 00 00 00 00 00 |
    | 3          | 16      | 00 00 00 00 00 00 00 00 |
    
    - `select * from bt_metap('accounts_followers_count_idx');`
    
    | magic  | version | root  | level | fastlroot | fastlevel | oldest_xact | last_cleanup_num_tuples |
    | ------ | ------- | ----  | ----- | --------- | --------- | ----------- | ----------------------- |
    | 340322 | 4       | 209   | 2     | 209       | 2         | 0           | -1                      |

    - `select type, live_items, dead_items, avg_item_size, page_size, free_size from bt_page_stats('accounts_followers_count_idx',1000)`
    
    | type | live_items | dead_items | avg_item_size | page_size | free_size |
    | ---- | ---------- | ---------- | ------------- | --------- | --------- |
    | l    | 367        | 0          | 16            | 8192      | 800       |
    
    - `select itemoffset, itemlen, data from bt_page_items('accounts_followers_count_idx',1) limit 1000;`
    
    | itemoffset | itemlen | data                    |
    | ---------- | ------- | ----------------------- |
    | 1          | 24      | 00 00 00... 48 00 09 00 |
    | 2          | 16      | 00 00 00 00 00 00 00 00 |
    | 3          | 16      | 00 00 00 00 00 00 00 00 |
    
    - `select * from bt_metap('accounts_screen_name_idx');`
    
    | magic  | version | root  | level | fastlroot | fastlevel | oldest_xact | last_cleanup_num_tuples |
    | ------ | ------- | ----  | ----- | --------- | --------- | ----------- | ----------------------- |
    | 340322 | 4       | 219   | 2     | 219       | 2         | 0           | -1                      |

    - `select type, live_items, dead_items, avg_item_size, page_size, free_size from bt_page_stats('accounts_screen_name_idx',1000)`
    
    | type | live_items | dead_items | avg_item_size | page_size | free_size |
    | ---- | ---------- | ---------- | ------------- | --------- | --------- |
    | l    | 282        | 0          | 22            | 8192      | 804       |
    
    - `select itemoffset, itemlen, data from bt_page_items('accounts_screen_name_idx',1) limit 1000;`
    
    | itemoffset | itemlen | data                    |
    | ---------- | ------- | ----------------------- |
    | 1          | 24      | 1d 30 30... 74 6f 00 00 |
    | 2          | 16      | 05 5f 00 5f 00 00 00 00 |
    | 3          | 16      | 0f 5f 5f 5f 5f 5f 5f 00 |
    
    - Lisia sa v dlzkach a samotnych datach (pochopitelne - lebo maju rozne stlpce a rozne typy chodnot: text - cisla). Taktiez sa lisia v hlbkach kvoli rozdielnej kardinalite. 