1. **Vyhľadajte v accounts screen_name s presnou hodnotou ‘realDonaldTrump’ a analyzujte daný select. Akú metódu vám vybral plánovač?**
    - `SELECT * FROM accounts WHERE screen_name = 'realDonaldTrump'`
    -  -> Parallel Seq Scan on accounts
    - ```
      Gather  (cost=1000.00..92687.80 rows=1 width=122) (actual time=786.947..874.206 rows=1 loops=1)
        Workers Planned: 2
        Workers Launched: 2
        ->  Parallel Seq Scan on accounts  (cost=0.00..91687.70 rows=1 width=122) (actual time=789.167..796.237 rows=0 loops=3)
              Filter: ((screen_name)::text = 'realDonaldTrump'::text)
              Rows Removed by Filter: 1156141
      Planning Time: 5.432 ms
      Execution Time: 874.250 ms```
2. **Koľko workerov pracovalo na danom selecte? Zdvihnite počet workerov a povedzte ako to  ovplyvňuje čas. Je tam nejaký strop?**
    - 2 workery
        - `Planning Time: 5.432 ms`
        - `Execution Time: 874.250 ms`
    - po zvýšení na 3: 
        - `SET max_parallel_workers_per_gather TO 3;`
        - ``` 
          Gather  (cost=1000.00..88608.68 rows=1 width=122) (actual time=309.024..331.010 rows=1 loops=1)
             Workers Planned: 3
             Workers Launched: 3
             ->  Parallel Seq Scan on accounts  (cost=0.00..87608.58 rows=1 width=122) (actual time=295.351..299.325 rows=0 loops=4)
                   Filter: ((screen_name)::text = 'realDonaldTrump'::text)
                   Rows Removed by Filter: 867106
           Planning Time: 0.091 ms
           Execution Time: 331.042 ms```
    - po zvýšení na 4:
        - ```
            Gather  (cost=1000.00..85461.92 rows=1 width=122) (actual time=260.660..313.972 rows=1 loops=1)
              Workers Planned: 4
              Workers Launched: 4
              ->  Parallel Seq Scan on accounts  (cost=0.00..84461.82 rows=1 width=122) (actual time=261.526..264.538 rows=0 loops=5)
                    Filter: ((screen_name)::text = 'realDonaldTrump'::text)
                    Rows Removed by Filter: 693684
            Planning Time: 0.147 ms
            Execution Time: 314.026 ms```
    - po zvýšení na 8 (použili sa však opäť len 4): 
        - ```
            Gather  (cost=1000.00..85461.92 rows=1 width=122) (actual time=268.771..297.035 rows=1 loops=1)
              Workers Planned: 4
              Workers Launched: 4
              ->  Parallel Seq Scan on accounts  (cost=0.00..84461.82 rows=1 width=122) (actual time=257.559..260.693 rows=0 loops=5)
                    Filter: ((screen_name)::text = 'realDonaldTrump'::text)
                    Rows Removed by Filter: 693684
            Planning Time: 0.091 ms
            Execution Time: 297.084 ms
            ```
    - pri viac workeroch čas vykonávania klesá, maximálne sa použili 4 workery
    - strop je nastavenie v konfiguračnom súbore servera, prípadne počet jadier stroja
       
3. **Vytvorte index nad screen_name a pozrite ako sa zmenil a porovnajte výstup oproti požiadavke bez indexu. Potrebuje plánovač v tejto požiadavke viac workerov? Bol tu aplikovaný nejaký filter na riadky? Prečo?**
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
    
    - Použije sa index scan - nepoužije sa filter na riadky, použije sa len index condition podla screen name.
    - Predĺžil sa čas plánovania, skrátil sa čas vykonávania. 
    - Viac workerov sa nepoužije, lebo index scan s 1 podmienkou sa nedá paralelizovať.

4. **Vyberte používateľov, ktorý majú followers_count väčší, rovný ako 100 a zároveň menší, rovný 200. Je správanie rovnaké v prvej úlohe? Je správanie rovnaké ako  v druhej úlohe? Prečo?**
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
    - Spravanie nie je rovnake ani ako v 1. ani ako v 2. ulohe, lebo sa nerobí paralel sequence scan.
    
5. **Vytvorte index nad 4 úlohou a popíšte prácu s indexom. Čo je to Bitmap Index Scan a prečo  je tam Bitmap Heap Scan? Prečo je tam recheck condition?**
    - `CREATE INDEX ON accounts (followers_count);`
    - `SELECT * FROM accounts WHERE followers_count >= 100 AND followers_count <= 200;`
    ```
        Bitmap Heap Scan on accounts  (cost=6750.25..86803.22 rows=428665 width=122) (actual time=49.805..466.929 rows=422237 loops=1)
         Recheck Cond: ((followers_count >= 100) AND (followers_count <= 200))
         Heap Blocks: exact=73127
         ->  Bitmap Index Scan on accounts_followers_count_idx  (cost=0.00..6643.08 rows=428665 width=0) (actual time=38.788..38.788 rows=422237 loops=1)
               Index Cond: ((followers_count >= 100) AND (followers_count <= 200))
       Planning Time: 0.144 ms
       Execution Time: 480.839 ms
    ```
   - Bitmap index scan je tam kvoli použitiu bitmap indexu.
   - Vytvori sa bitova maska riadkov pre 1. podmienku a pre 2. podmienku a potom sa najdu riadky, ktore vyhovuju naraz obom podmienkam pomocou bitovej operácie AND
   - Recheck condition sa použije je v prípade, keď by bitové masky zabrali veľa miesta a teda sa vytvoria len pre celé stránky, avšak záznamy v nich je nutné potom znovu skontrolovať.
   
6. **Vyberte používateľov, ktorí majú followers_count väčší, rovný ako 100 a zároveň menší, rovný 1000? V čom je rozdiel, prečo?**
    - `SELECT * FROM accounts WHERE followers_count >= 100 AND followers_count <= 1000;`
    ```
       Bitmap Heap Scan on accounts  (cost=23780.91..120061.20 rows=1510486 width=122) (actual time=123.633..447.429 rows=1504549 loops=1)
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
   - pribudla sekcia JIT aby pri vyhodnocovaní nad viac záznamamy bolo spracovanie rýchlejšie
   
7. **Vytvorte daľšie 3 indexy na name, friends_count, a description a insertnite si  svojho používateľa (to je jedno aké dáta) do accounts. Koľko to trvalo? Dropnite indexy a spravte to ešte raz. Prečo je tu rozdiel?**
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
    - Rozdiel je, lebo pri každom zápise treba aj upravovať všetky indexy, čo chvíľku trvá.

8. **Vytvorte index nad tweetami pre retweet_count a pre content. Porovnajte ich dĺžku vytvárania. Prečo je tu taký rozdiel?**

    - `CREATE INDEX ON tweets (retweet_count);`
    - trvalo 8.5s
    - `CREATE INDEX ON tweets (content);`
    - trvalo 33.9s
    - Rozdiel je, lebo v 1. pripade indexujeme iba čísla, v druhom pripade indexujeme textové hodnoty
9. **Porovnajte indexy pre retweet_count, content, followers_count, screen_name,... v čom sa líšia a prečo (stačí stručne)?**
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
    
    - líšia sa v mohutnosti (`live_items`) a index nad obsahom tweetov sa líši aj v hĺbke (`level`). 
    - priemernú veľkosť položky majú rozdielne indexy nad číselnými a textovými stĺpcami - lebo pochopiteľne textová položka má zvyčajne inú veľkosť, než číselná, ktorá má zvyčajne fixne definovanú veľkosť.