1. Vyhľadajte v tweets.content meno „Gates“ na ľubovoľnom mieste a porovnajte výsledok po tom, ako content naindexujete. V čom je rozdiel a prečo?
    - `EXPLAIN ANALYZE SELECT * FROM tweets WHERE content LIKE '%Gates%';`
    - pred indexovanim:
        - ```
          Gather  (cost=1000.00..252899.76 rows=650 width=249) (actual time=1.916..867.058 rows=21021 loops=1)
            Workers Planned: 2
            Workers Launched: 2
            ->  Parallel Seq Scan on tweets  (cost=0.00..251834.76 rows=271 width=249) (actual time=2.251..831.130 rows=7007 loops=3)
                  Filter: (content ~~ '%Gates%'::text)
                  Rows Removed by Filter: 2319634
          Planning Time: 0.155 ms
          JIT:
            Functions: 6
          "  Options: Inlining false, Optimization false, Expressions true, Deforming true"
          "  Timing: Generation 0.881 ms, Inlining 0.000 ms, Optimization 0.475 ms, Emission 5.636 ms, Total 6.992 ms"
          Execution Time: 868.091 ms
          ```
        - Po vytvorení indexu: `CREATE INDEX ON tweets (content);`
        - ```
          Gather  (cost=1000.00..252899.76 rows=650 width=249) (actual time=1.903..852.614 rows=21021 loops=1)
            Workers Planned: 2
            Workers Launched: 2
            ->  Parallel Seq Scan on tweets  (cost=0.00..251834.76 rows=271 width=249) (actual time=2.582..816.634 rows=7007 loops=3)
                  Filter: (content ~~ '%Gates%'::text)
                  Rows Removed by Filter: 2319634
          Planning Time: 0.206 ms
          JIT:
            Functions: 6
          "  Options: Inlining false, Optimization false, Expressions true, Deforming true"
          "  Timing: Generation 0.852 ms, Inlining 0.000 ms, Optimization 0.464 ms, Emission 5.507 ms, Total 6.824 ms"
          Execution Time: 853.676 ms
            ``` 
    - Rozdiel neni v ničom, klasický BTree index nevieme použiť na hľadanie textu kdekoľvek v texte - vieme ho použiť iba na hľadanie hodnoty na začiatku. Na hľadanie kdekoľvek by sme potrebovali napr. inverzný index

2. Vyhľadajte tweet, ktorý začína “DANGER: WARNING:”. Použil sa index?
    - `EXPLAIN ANALYZE SELECT * FROM tweets WHERE content LIKE 'DANGER: WARNING:%';`
    - ```
      Gather  (cost=1000.00..252899.76 rows=650 width=249) (actual time=211.861..368.764 rows=1 loops=1)
        Workers Planned: 2
        Workers Launched: 2
        ->  Parallel Seq Scan on tweets  (cost=0.00..251834.76 rows=271 width=249) (actual time=283.837..335.157 rows=0 loops=3)
              Filter: (content ~~ 'DANGER: WARNING:%'::text)
              Rows Removed by Filter: 2326640
      Planning Time: 0.097 ms
      JIT:
        Functions: 6
      "  Options: Inlining false, Optimization false, Expressions true, Deforming true"
      "  Timing: Generation 0.861 ms, Inlining 0.000 ms, Optimization 0.459 ms, Emission 5.538 ms, Total 6.859 ms"
      Execution Time: 369.086 ms
      ```
   - nepoužil sa index 😱
3. Teraz naindexujte content tak, aby sa použil index a zhodnoťte prečo sa pred tým nad “DANGER: WARNING:” nepoužil. Použije sa teraz na „Gates“ na ľubovoľnom mieste?
    - `CREATE INDEX ON tweets (content TEXT_PATTERN_OPS);`
    - `EXPLAIN ANALYZE SELECT * FROM tweets WHERE content LIKE 'DANGER: WARNING:%';`
    - ```
      Index Scan using tweets_content_idx on tweets  (cost=0.68..4.71 rows=650 width=249) (actual time=0.018..0.020 rows=1 loops=1)
        Index Cond: ((content ~>=~ 'DANGER: WARNING:'::text) AND (content ~<~ 'DANGER: WARNING;'::text))
        Filter: (content ~~ 'DANGER: WARNING:%'::text)
      Planning Time: 0.202 ms
      Execution Time: 0.032 ms
      ```
    - Teraz sa už použil. 
    - Predtým sa nepoužil, kvôli rozdielnemu kódovaniu indexu a dát - s predvoleným nastavením indexu sa dá použiť pri operátore `LIKE` iba pokiaľ má databáza kódovanie `C`, čo v našom prípade nemá `SHOW LC_COLLATE` -> `en_US.UTF-8`
    - Zmenou nastavenia indexu vieme toto obmedzenie obísť, môžme však prísť o podporu `<` a podobných operátorov.
    - Index sa však ani teraz nepoužije pri hľadaní "Gates" na ľubovoľnom mieste - pri tejto požiadavke nezáleží na kódovaní - bežný BTree index nevie ȟľadať na ľubovoľnom mieste v texte. 

4. Vytvorte nový index, tak aby ste vedeli vyhľadať tweet, ktorý konči reťazcom „LUCIFERASE“ a nezáleží na tom ako to napíšete.
    - `CREATE INDEX ON tweets (upper(reverse(content)) TEXT_PATTERN_OPS);`
    - `EXPLAIN ANALYZE SELECT * FROM tweets WHERE upper(reverse(content)) LIKE upper(reverse('%LUCIFERASE'));`
    - ```
      Bitmap Heap Scan on tweets  (cost=2026.41..54711.84 rows=34900 width=249) (actual time=0.063..0.064 rows=0 loops=1)
        Filter: (upper(reverse(content)) ~~ 'ESAREFICUL%'::text)
        ->  Bitmap Index Scan on tweets_upper_idx  (cost=0.00..2017.68 rows=34900 width=0) (actual time=0.062..0.062 rows=0 loops=1)
              Index Cond: ((upper(reverse(content)) ~>=~ 'ESAREFICUL'::text) AND (upper(reverse(content)) ~<~ 'ESAREFICUM'::text))
      Planning Time: 0.090 ms
      Execution Time: 0.077 ms
      ```

5. Nájdite účty, ktoré majú follower_count menší ako 10 a friends_count väčší ako 1000 a výsledok zoraďte podľa statuses_count. Následne spravte jednoduché indexy tak, aby to malo zmysel a popíšte výsledok.
    - `CREATE INDEX ON accounts (followers_count);`
    - `CREATE INDEX ON accounts (friends_count);`
    - `EXPLAIN ANALYZE SELECT * FROM accounts WHERE followers_count < 10 AND friends_count > 1000 ORDER BY statuses_count;`
    - ```
      Sort  (cost=58765.87..58866.42 rows=40219 width=122) (actual time=61.221..61.230 rows=171 loops=1)
        Sort Key: statuses_count
        Sort Method: quicksort  Memory: 53kB
        ->  Bitmap Heap Scan on accounts  (cost=12598.42..55690.00 rows=40219 width=122) (actual time=61.054..61.182 rows=171 loops=1)
              Recheck Cond: ((followers_count < 10) AND (friends_count > 1000))
              Heap Blocks: exact=170
              ->  BitmapAnd  (cost=12598.42..12598.42 rows=40219 width=0) (actual time=60.646..60.647 rows=0 loops=1)
                    ->  Bitmap Index Scan on accounts_followers_count_idx  (cost=0.00..2289.92 rows=176199 width=0) (actual time=13.166..13.166 rows=174003 loops=1)
                          Index Cond: (followers_count < 10)
                    ->  Bitmap Index Scan on accounts_friends_count_idx  (cost=0.00..10288.14 rows=791695 width=0) (actual time=45.289..45.289 rows=788089 loops=1)
                          Index Cond: (friends_count > 1000)
      Planning Time: 0.095 ms
      Execution Time: 61.255 ms
      ```
    - Vytvorené 2 indexy na stĺpcoch `followers_count` a `friends_count` umožnia vybrať riadky vyhovujúce podmienke, tie je následne nutné ešte zoradiť 
6. Na predošlú query spravte zložený index a porovnajte výsledok s tým, keď je sú indexy separátne.
    - `CREATE INDEX ON accounts (followers_count, friends_count);`
    - `EXPLAIN ANALYZE SELECT * FROM accounts WHERE followers_count < 10 AND friends_count > 1000 ORDER BY statuses_count;`
    - ```
      Sort  (cost=48907.92..49008.47 rows=40219 width=122) (actual time=4.470..4.479 rows=171 loops=1)
        Sort Key: statuses_count
        Sort Method: quicksort  Memory: 53kB
        ->  Bitmap Heap Scan on accounts  (cost=2740.47..45832.05 rows=40219 width=122) (actual time=4.311..4.429 rows=171 loops=1)
              Recheck Cond: ((followers_count < 10) AND (friends_count > 1000))
              Heap Blocks: exact=170
              ->  Bitmap Index Scan on accounts_followers_count_friends_count_idx  (cost=0.00..2730.42 rows=40219 width=0) (actual time=4.292..4.293 rows=171 loops=1)
                    Index Cond: ((followers_count < 10) AND (friends_count > 1000))
      Planning Time: 0.153 ms
      Execution Time: 4.500 ms
      ```
    - Použije sa iba 1 Bitmap index scan a výsledný čas je kratší, než pri použití 2 indexov, kedy ešte treba spracovať výsledky z každého indexu.
 
7. Upravte query tak, aby bol follower_count menší ako 1000 a friends_count vačší ako 1000. V čom je rozdiel a prečo?
    - `EXPLAIN ANALYZE SELECT * FROM accounts WHERE followers_count < 1000 AND friends_count > 1000 ORDER BY statuses_count;`
    - ```
      Gather Merge  (cost=126944.96..179781.85 rows=452856 width=122) (actual time=268.932..354.762 rows=269817 loops=1)
        Workers Planned: 2
        Workers Launched: 2
        ->  Sort  (cost=125944.94..126511.01 rows=226428 width=122) (actual time=225.050..239.891 rows=89939 loops=3)
              Sort Key: statuses_count
              Sort Method: external merge  Disk: 16536kB
              Worker 0:  Sort Method: external merge  Disk: 11968kB
              Worker 1:  Sort Method: external merge  Disk: 10680kB
              ->  Parallel Seq Scan on accounts  (cost=0.00..95300.65 rows=226428 width=122) (actual time=2.740..175.251 rows=89939 loops=3)
                    Filter: ((followers_count < 1000) AND (friends_count > 1000))
                    Rows Removed by Filter: 1066202
      Planning Time: 0.084 ms
      JIT:
        Functions: 6
      "  Options: Inlining false, Optimization false, Expressions true, Deforming true"
      "  Timing: Generation 1.071 ms, Inlining 0.000 ms, Optimization 0.545 ms, Emission 7.342 ms, Total 8.958 ms"
      Execution Time: 366.273 ms
      ```
    - Použije sa Parallel Sequence scan, lebo rozloženie hodnôt v indexe spôsobí, že index nevylúči dostatok riadkov aby sa oplatilo ho použiť.
8. Vyhľadajte všetky tweety (content), ktoré spomenul autor, ktorý obsahuje v popise (description) reťazec „comedian” (case insensitive), tweety musia obsahovať reťazec „conspiracy“ (case insensitive), tweety nesmú mať priradený hashtag a počet retweetov tweetu (retweet_count) je buď menší rovný 10, alebo väčší ako 50. Zobrazte len rozdielne záznamy a zoraďte ich podľa počtu followerov DESC a pobavte sa. Mimo to si nad tým spravte analýzu a tú popíšte do protokolu - čo všetko sa tam deje (explain analyse).
    - ```
      EXPLAIN ANALYZE SELECT a.name, a.screen_name, a.followers_count, t.retweet_count,  t.content FROM tweets t
      LEFT OUTER JOIN tweet_hashtags th on t.id = th.tweet_id
      LEFT JOIN tweet_mentions tm
          ON tm.tweet_id = t.id
      LEFT JOIN accounts a
            ON tm.account_id=a.id
      WHERE
          a.description ILIKE '%comedian%'
          AND t.content ILIKE '%conspiracy%'
          AND (t.retweet_count <= 10 OR t.retweet_count > 50)
          AND th.hashtag_id IS NULL
      ORDER BY a.followers_count DESC;
      ```
    - ```
      Sort  (cost=184137.75..184137.76 rows=1 width=186) (actual time=2523.017..2537.014 rows=8 loops=1)
        Sort Key: a.followers_count DESC
        Sort Method: quicksort  Memory: 28kB
        ->  Nested Loop Left Join  (cost=92690.06..184137.74 rows=1 width=186) (actual time=2125.383..2537.000 rows=8 loops=1)
              Filter: (th.hashtag_id IS NULL)
              Rows Removed by Filter: 9
              ->  Gather  (cost=92689.63..184130.75 rows=1 width=205) (actual time=2125.368..2536.912 rows=9 loops=1)
                    Workers Planned: 2
                    Workers Launched: 2
                    ->  Nested Loop  (cost=91689.63..183130.65 rows=1 width=205) (actual time=2033.239..2480.415 rows=3 loops=3)
                          ->  Parallel Hash Join  (cost=91689.07..182981.23 rows=227 width=51) (actual time=1959.265..2368.714 rows=10456 loops=3)
                                Hash Cond: (tm.account_id = a.id)
                                ->  Parallel Seq Scan on tweet_mentions tm  (cost=0.00..83375.95 rows=3015695 width=28) (actual time=0.019..180.409 rows=2412556 loops=3)
                                ->  Parallel Hash  (cost=91687.71..91687.71 rows=109 width=39) (actual time=1958.680..1958.681 rows=839 loops=3)
                                      Buckets: 4096 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 312kB
                                      ->  Parallel Seq Scan on accounts a  (cost=0.00..91687.71 rows=109 width=39) (actual time=13.043..1565.286 rows=839 loops=3)
                                            Filter: (description ~~* '%comedian%'::text)
                                            Rows Removed by Filter: 1155303
                          ->  Index Scan using tweets_pkey on tweets t  (cost=0.56..0.66 rows=1 width=174) (actual time=0.010..0.010 rows=0 loops=31367)
                                Index Cond: ((id)::text = (tm.tweet_id)::text)
                                Filter: ((content ~~* '%conspiracy%'::text) AND ((retweet_count <= 10) OR (retweet_count > 50)))
                                Rows Removed by Filter: 1
              ->  Index Only Scan using tweet_hashtags2_tweet_id_hashtag_id_key on tweet_hashtags th  (cost=0.43..6.95 rows=4 width=28) (actual time=0.008..0.008 rows=1 loops=9)
                    Index Cond: (tweet_id = (t.id)::text)
                    Heap Fetches: 9
      Planning Time: 1.253 ms
      JIT:
        Functions: 64
      "  Options: Inlining false, Optimization false, Expressions true, Deforming true"
      "  Timing: Generation 5.910 ms, Inlining 0.000 ms, Optimization 1.834 ms, Emission 34.912 ms, Total 42.657 ms"
      Execution Time: 2539.200 ms      
      ```
    - Parallel Sequence scan nad `accounts` hľadá záznamy, ktoré obsahujú `comedian` v popise, parallel sequence scan sa použije aj na nájdenie záznamov tweet_mentions
    - Index scanom sa nájdu tweety na ktoré sa dá spraviť join a odfiltrujú sa tie, ktoré neobsahujú `conspiracy`
    - Nested Loopom sa vykoná join
    - Index only scanom nad `tweet_hashtags` sa nájdu také, ktoré nemajú hashtag  