# Appflame - Product Analyst Test Task

Нижче наведено коротке Summary за результатами виконання тестового завдання. Детальна методологія та код знаходяться у відповідних папках завдань.

## Результати

### Task 1 - SQL
- **Retention LT1** реалізовано через CTE + LEFT JOIN. Середній Day-1 Retention на тестових даних: 65.83%
- **Window function** `AVG() OVER (PARTITION BY source)` коректно рахує відхилення юзера від середнього по каналу (перевірка: середнє diff = ~0)
- **Inactive users** - розподіл сторінок в останній день для юзерів що не заходили 3+ днів

### Task 2 - Mail Retention EDA
- **Воронка:** доставка ідеальна (99.94%), головний drop-off - Delivered → Read (лише 16.88% відкривають)
- **Buyer vs Not Buyer:** click rate у Buyer в 3x вищий (8.29% vs 2.77%), credits rate в 53x вищий (0.53% vs 0.01%)
- **Типи листів:** `welcome_message` має найвищий CTR (6.94%), `unread_used_message` - найнижчий (1.68%)
- **Rule-сегменти:** FH і New лідирують (~53% read rate, ~18% click rate); History і SM - нульові показники
- **A/B тести:** Group_1 показала значущий lift по click rate (+25.58%, p<0.0001) і credits rate (+49.34%, p=0.03); Group_2 шкідлива (-22.87% click rate, p<0.0001)

### Task 3 - Data App
- Streamlit додаток з двома розділами: моніторинг метрик і A/B аналіз
- Виявлення аномалій: дні де метрика падає нижче 80% від середнього
- Chi-square тест для кожної метрики з lift % і p-value
- AI summary і рекомендації через Google Gemini API

### Task 4 - Dataset Research
- Методологія: pivot table -> cosine similarity -> hierarchical clustering (Ward) -> dendrogram
- Середня cosine similarity між групами: **0.999** - дані однорідні
- Виявлено 4 кластери, але різниця між найкращою і найгіршою групою по CTR лише ~3.6%
- Рекомендація: для змістовнішої кластеризації потрібні додаткові ознаки (демографія, гео, платформа)
