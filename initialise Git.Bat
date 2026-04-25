git init
git config --global --add safe.directory "//CRAZYCLOUD/Fichiers/Github/clb_editor"
git config --global user.email "crazydoub@gmail.com"
git config --global user.name "Crazydoub"
git add .
git commit -m "Initial commit"
echo creez le repo
pause

git remote add origin https://github.com/TONPSEUDO/clb-editor.git
git branch -M main
git push -u origin main

echo on envoie
Pause