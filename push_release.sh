#!/bin/bash
res=`curl --user "borntohonk:$GITHUB_TOKEN" -X POST https://api.github.com/repos/borntohonk/patches/releases \
-d "
{
  \"tag_name\": \"patches-$(date +%F)\",
  \"target_commitish\": \"master\",
  \"name\": \"New Patches $(date +%F)\",
  \"body\": \"New Patches published $(date +%F), you can assume if this date is near a recent System Firmware Update, that patches for this are included. Hekate style kip-patches are also included. Loader patches are not included, use a proper fork disabling this check instead of patching an open source module. See here for a fork example https://github.com/borntohonk/NeutOS/releases/latest \",
  \"draft\": false,
  \"prerelease\": false
}"`
echo Create release result: ${res}
rel_id=`echo ${res} | python -c 'import json,sys;print(json.load(sys.stdin, strict=False)["id"])'`

curl --user "borntohonk:$GITHUB_TOKEN" -X POST https://uploads.github.com/repos/borntohonk/patches/releases/${rel_id}/assets?name=patches.zip --header 'Content-Type: application/zip ' --upload-file patches.zip