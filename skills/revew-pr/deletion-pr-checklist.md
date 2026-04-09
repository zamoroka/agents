# Deletion PR checklist

Use this checklist when the PR is a pure deletion (modules/files removed).

- Check **orphaned references** in non-deleted files (`composer.json` `require`, `patches/`, `app/etc/hyva-themes.json`, XML `di`/config references to removed classes).
- Check **DB schema leftovers**: if a deleted module had `db_schema.xml`, its tables/columns remain after `setup:upgrade`; flag required manual SQL (`DROP TABLE` / `ALTER TABLE DROP COLUMN`).
- Check **config.php completeness**: all removed modules must be deregistered.
- Skip code quality issues in deleted code itself (unless they affect remaining code).
