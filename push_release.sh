#!/bin/bash
HASH=$(curl --silent "https://api.github.com/repos/Atmosphere-NX/Atmosphere/releases" | grep "browser_download_url" | head -1 | grep -oE "\-([0-9a-f]{8})" | cut -c2-)
AMSVERSION=$(curl --silent "https://api.github.com/repos/Atmosphere-NX/Atmosphere/releases" | grep "tag" | head -1 | cut -c 75-79)
FWVERSION=$(curl --silent "https://en-americas-support.nintendo.com/app/answers/detail/a_id/22525/kw/nintendo%20switch%20system%20update" | grep "Ver." | head -1 | cut -c 28-33)
res=`curl --user "borntohonk:$GITHUB_TOKEN" -X POST https://api.github.com/repos/borntohonk/patches/releases \
-d "
{
    \"tag_name\": \"$FWVERSION-$AMSVERSION-$HASH\",
    \"target_commitish\": \"master\",
    \"name\": \"Supports HOS firmware $FWVERSION and AMS $AMSVERSION-$HASH\",
    \"body\": \"- es, fs and nifm patches for HOS ${FWVERSION} are included. \r\n\r\n- has loader patches for Atmosphere version ${AMSVERSION}-${HASH} \r\n\r\n- Hekate style patches are included for both loader and FS \",
    \"draft\": false,
    \"prerelease\": false
}"`
echo Create release result: ${res}
rel_id=`echo ${res} | python -c 'import json,sys;print(json.load(sys.stdin, strict=False)["id"])'`

curl --user "borntohonk:$GITHUB_TOKEN" -X POST https://uploads.github.com/repos/borntohonk/patches/releases/${rel_id}/assets?name=patches.zip --header 'Content-Type: application/zip ' --upload-file patches.zip