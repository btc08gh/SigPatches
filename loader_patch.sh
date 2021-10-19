#!/bin/bash
git config --global user.name 'borntohonk'
git config --global user.email '6264306+borntohonk@users.noreply.github.com'
AMSHASH=$(curl -s https://api.github.com/repos/Atmosphere-NX/Atmosphere/releases | grep "browser_download_url" | head -1 | grep -oE "\-([0-9a-f]{8})" | head -1 | cut -c2-)
git fetch
sleep 5
git add .
sleep 5
if [[ `git status --porcelain` ]]; then
  git commit -m"Loader patch for $AMSHASH was added!"
  git push
else
  echo "No new patches were generated"
fi