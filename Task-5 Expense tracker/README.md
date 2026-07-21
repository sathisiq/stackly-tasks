 
1. Create the database and tables by running [`database.sql`](database.sql) in MySQL.
2. Create a virtual environment and install packages: `py -m pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` (or set the shown environment variables) and enter your MySQL password. Set a strong `SECRET_KEY`.
4. Run `py app.py`, then visit `http://localhost:5000`.

## Required database SQL

The full setup SQL is in [`database.sql`](database.sql). It creates `users` and `expenses`, with `expenses.user_id` as a foreign key referencing `users.id` and `ON DELETE CASCADE`.

## Write-up

**What is a foreign key and what does `ON DELETE CASCADE` do?**
 A foreign key enforces a valid relationship between `expenses.user_id` and a row in `users`. `ON DELETE CASCADE` automatically removes a user's related expenses if that user is deleted, preventing orphan records.

**How are users' expenses kept private?**
 Every protected route first checks `session['user_id']`. All read, update, and delete SQL includes `user_id = %s` with that session value, so an ID from another account cannot return or change that account's expense.

**Category summary SQL:**

```sql
SELECT category, SUM(amount) AS amount
FROM expenses
WHERE user_id = %s
GROUP BY category
ORDER BY amount DESC;
```

**Hardest part:** Keeping the UI immediately in sync after create, update, delete, and filtering. The expenses page centralises loading in `refresh()`, which fetches the active filtered list again after every successful change and redraws the table without a page reload.
