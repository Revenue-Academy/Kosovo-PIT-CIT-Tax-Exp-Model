@ECHO OFF
SETLOCAL

git branch

:PROMPT
SET /P ONMASTER=Are you on the main branch (y/n)?
IF /I "%ONMASTER%" NEQ "y" GOTO END

git fetch upstream
git merge upstream/main
git push origin main

:END
ENDLOCAL
