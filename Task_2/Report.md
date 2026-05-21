# Task 2 - Mail Retention EDA

## Задача

Провести exploratory data analysis email-каналу для dating-додатку Mailkeeper.
Дані: 472,636 відправок за 9 днів (02.10 - 10.10.2024), 18 колонок.


## Методологія

1. Побудова воронки: Sent -> Delivered -> Read -> Clicked -> Credits spent
2. Порівняння Buyer vs Not Buyer по всіх метриках
3. Аналіз ефективності по типу листа (response)
4. Аналіз по rule-сегментах
5. Аналіз динаміки метрик по датах
6. A/B тест аналіз по 4 групах з chi-square тестом значущості
7. Формулювання інсайтів та гіпотез


## Результати

### Воронка email-каналу

<img width="611" height="147" alt="image" src="https://github.com/user-attachments/assets/e4e5c105-10e1-40dd-81ec-dedb2864b2c0" />


**Ключовий інсайт:** головний drop-off між Delivered і Read - лише 27.63% юзерів відкривають листи. Email-канал майже не конвертує в покупку credits (0.06%).


### Buyer vs Not Buyer

<img width="632" height="75" alt="image" src="https://github.com/user-attachments/assets/ec68f30d-19d4-48c7-a1df-92d7ca56abab" />


- Read rate у Buyer вищий на 30%
- Click rate у Buyer в 3x вищий
- Credits rate у Buyer в 53x вищий

**Висновок:** email-канал ефективний для утримання платників, але майже не конвертує нових юзерів.


### Аналіз по типу листа

<img width="819" height="117" alt="image" src="https://github.com/user-attachments/assets/2ea4c6b1-767b-444e-9087-64a5c0409f53" />


- `welcome_message` має найвищий CTR (6.94%) попри малий об'єм
- `unread_used_message` - найгірший CTR (1.68%), в 3.8x нижчий за unused
- Листи про непрочитані нові повідомлення (unused) ефективніші ніж нагадування про старі (used)


### Аналіз по Rule-сегменту

<img width="537" height="198" alt="image" src="https://github.com/user-attachments/assets/9817b461-99b4-4ee5-aa6f-6e3cf3b3b253" />


- FH і New - лідери по обох метриках (~53% read rate, ~18% click rate)
- History і SM - нульові показники по всіх метриках
- FW - великий сегмент (7,253) але слабкий результат


### A/B тести

<img width="684" height="457" alt="image" src="https://github.com/user-attachments/assets/f47347a9-8644-4887-bb89-dd39369689fb" />



- **Group_1:** значуще покращення Click rate (+25.58%) і Credits rate (+49.34%) - рекомендується масштабувати
- **Group_2:** значуще погіршення Click rate (-22.87%) - тест шкідливий, зупинити
- **Group_3 і Group_4:** жодна метрика не досягла значущості


## Гіпотези для майбутніх тестів

1. **FW сегмент** має великий об'єм (7,253) але слабкий read rate (10%) - тестувати зміну subject line або часу відправки
2. **unread_used_message** має CTR в 3.8x нижчий за unused - тестувати обмеження частоти до 1 листа на 3 дні щоб не "спалювати" аудиторію
3. **welcome_message** має найвищий CTR (6.94%) але нульовий credits rate - тестувати додавання прямого CTA на покупку кредитів
4. **History і SM** сегменти повністю неефективні - тестувати повне відключення або радикальну зміну контенту
5. **Group_1** зміна показала реальний lift по кліках - масштабувати і відстежити чи конвертується в credits spend
