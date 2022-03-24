#!/bin/bash
git config --global user.name 'borntohonk'
git config --global user.email '6264306+borntohonk@users.noreply.github.com'
HASH=$(curl --silent "https://api.github.com/repos/Atmosphere-NX/Atmosphere/releases" | grep "browser_download_url" | head -1 | grep -oE "\-([0-9a-f]{8})" | cut -c2-)
git clone https://github.com/Atmosphere-NX/Atmosphere.git
sleep 5
git -C Atmosphere checkout $HASH
AMSMAJORVER=$(grep 'define ATMOSPHERE_RELEASE_VERSION_MAJOR\b' Atmosphere/libraries/libvapours/include/vapours/ams/ams_api_version.h | tr -s [:blank:] | cut -d' ' -f3)
AMSMINORVER=$(grep 'define ATMOSPHERE_RELEASE_VERSION_MINOR\b' Atmosphere/libraries/libvapours/include/vapours/ams/ams_api_version.h | tr -s [:blank:] | cut -d' ' -f3)
AMSMICROVER=$(grep 'define ATMOSPHERE_RELEASE_VERSION_MICRO\b' Atmosphere/libraries/libvapours/include/vapours/ams/ams_api_version.h | tr -s [:blank:] | cut -d' ' -f3)
HOS_MAJORVER=$(grep 'define ATMOSPHERE_SUPPORTED_HOS_VERSION_MAJOR\b' Atmosphere/libraries/libvapours/include/vapours/ams/ams_api_version.h | tr -s [:blank:] | cut -d' ' -f3)
HOS_MINORVER=$(grep 'define ATMOSPHERE_SUPPORTED_HOS_VERSION_MINOR\b' Atmosphere/libraries/libvapours/include/vapours/ams/ams_api_version.h | tr -s [:blank:] | cut -d' ' -f3)
HOS_MICROVER=$(grep 'define ATMOSPHERE_SUPPORTED_HOS_VERSION_MICRO\b' Atmosphere/libraries/libvapours/include/vapours/ams/ams_api_version.h | tr -s [:blank:] | cut -d' ' -f3)
HOSVER=$HOS_MAJORVER.$HOS_MINORVER.$HOS_MICROVER
AMSVER=$AMSMAJORVER.$AMSMINORVER.$AMSMICROVER
sleep 1
git fetch
sleep 1
git add hekate_patches
sleep 1
git add SigPatches/atmosphere
sleep 1
if [[ `git status --porcelain` ]]; then
  git commit -m"Loader patch for $HASH was added!"
  git push
  sleep 1
  echo NeutOS $AMSVER-$AMSHASH for FW version $HOSVER > changelog.md
  echo "" >> changelog.md
  echo - Supports HOS firmware $HOSVER and AMS $AMSVER-$HASH >> changelog.md
  echo "" >> changelog.md
  echo - has loader patches for Atmosphere version ${AMSVER}-${HASH} >> changelog.md
  echo "" >> changelog.md
  echo "- Hekate style patches are included for both loader and FS" >> changelog.md
  echo "" >> changelog.md
  sleep 5
  echo gh release create $HOSVER-$AMSVER-$HASH -F changelog.md SigPatches.zip --repo github.com/borntohonk/SigPatches
  rm -rf Atmosphere
else
  echo "No new patches were generated"
  rm -rf Atmosphere
fi
