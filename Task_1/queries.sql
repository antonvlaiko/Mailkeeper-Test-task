-- TASK 1: Day-1 Retention (LT1) по датах реєстрації
-- Логіка: який % юзерів повернувся на наступний день після реєстрації

WITH registrations AS (
    SELECT user_id, DATE(MIN(first_ts), 'unixepoch') AS reg_date
    FROM user_sessions
    GROUP BY user_id
),

next_day_returns AS (
    SELECT DISTINCT r.user_id, r.reg_date
    FROM registrations r
    JOIN user_sessions s ON r.user_id = s.user_id
    WHERE DATE(s.first_ts, 'unixepoch') = DATE(r.reg_date, '+1 day')
)

SELECT r.reg_date, 
  COUNT(DISTINCT r.user_id) AS registered_users,
  COUNT(DISTINCT n.user_id) AS returned_next_day,
    ROUND(100.0 * COUNT(DISTINCT n.user_id) / COUNT(DISTINCT r.user_id), 2) AS retention_lt1_pct
FROM registrations r
LEFT JOIN next_day_returns n ON r.user_id = n.user_id
GROUP BY r.reg_date
ORDER BY r.reg_date;


-- TASK 2: Різниця між сторінками юзера і середнім по його source
-- Логіка: window function AVG() OVER (PARTITION BY source)

SELECT user_id, source, 
  SUM(pages) AS user_total_pages,
  ROUND(AVG(SUM(pages)) OVER (PARTITION BY source), 2) AS avg_pages_by_source,
    ROUND(SUM(pages) - AVG(SUM(pages)) OVER (PARTITION BY source), 2) AS diff_from_source_avg
FROM user_sessions
GROUP BY user_id, source
ORDER BY source, diff_from_source_avg DESC;


-- TASK 3: Структура сторінок в останній день логіну для юзерів, що не заходили 3+ днів
-- Логіка: знаходимо last_login кожного юзера, фільтруємо тих хто давно не заходив, дивимось розподіл pages в той останній день

WITH last_session AS (
    SELECT user_id,
      DATE(MAX(first_ts), 'unixepoch') AS last_login_date,
        SUM(CASE WHEN DATE(first_ts, 'unixepoch') = DATE(MAX(first_ts) OVER (PARTITION BY user_id), 'unixepoch') THEN pages ELSE 0 END) AS pages_on_last_day
    FROM user_sessions
    GROUP BY user_id
),

reference_date AS (
    SELECT DATE(MAX(first_ts), 'unixepoch') AS max_date
    FROM user_sessions
),

inactive_users AS (
    SELECT ls.user_id, ls.last_login_date, ls.pages_on_last_day
    FROM last_session ls
    CROSS JOIN reference_date rd
    WHERE JULIANDAY(rd.max_date) - JULIANDAY(ls.last_login_date) >= 3
)

SELECT
    pages_on_last_day,
    COUNT(user_id) AS user_count,
    ROUND(100.0 * COUNT(user_id) / SUM(COUNT(user_id)) OVER (), 2) AS pct_of_inactive
FROM inactive_users
GROUP BY pages_on_last_day
ORDER BY pages_on_last_day;
