echo "# clb-editor" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote set-url origin https://github.com/Crazydoub/clb-editor.git
git remote add origin https://github.com/Crazydoub/clb-editor.git
git push -u origin main
pause