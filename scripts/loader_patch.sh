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
  res=`curl --user "borntohonk:$GITHUB_TOKEN" -X POST https://api.github.com/repos/borntohonk/SigPatches/releases \
  -d "
  {
      \"tag_name\": \"$HOSVER-$AMSVER-$HASH\",
      \"target_commitish\": \"master\",
      \"name\": \"Supports HOS firmware $HOSVER and AMS $AMSVER-$HASH\",
      \"body\": \"- es, fs and nifm patches for HOS ${HOSVER} are included. \r\n\r\n- has loader patches for Atmosphere version ${AMSVER}-${HASH} \r\n\r\n- Hekate style patches are included for both loader and FS \",
      \"draft\": false,
      \"prerelease\": false
  }"`
  echo Create release result: ${res}
  rel_id=`echo ${res} | python -c 'import json,sys;print(json.load(sys.stdin, strict=False)["id"])'`
  curl --user "borntohonk:$GITHUB_TOKEN" -X POST https://uploads.github.com/repos/borntohonk/SigPatches/releases/${rel_id}/assets?name=SigPatches.zip --header 'Content-Type: application/zip ' --upload-file SigPatches.zip
  sleep 5
  rm -rf Atmosphere
else
  echo "No new patches were generated"
  rm -rf Atmosphere
fi
