rm -rf .git

git init

git config user.email "contact@bscpredict.com"
git config user.name "bsc-predict"

git add .
git commit -m update


git remote add origin git@bsc-predict:bsc-predict/bsc-predict-updater
git push -u --force origin master
