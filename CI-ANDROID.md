Build Android APK with GitHub Actions

Overview
- This repository includes a workflow at `.github/workflows/android-debug.yml` that builds a Kivy/KivyMD Android debug APK in the cloud using Buildozer directly on the GitHub Ubuntu runner (no Docker), and uploads the built APK as an artifact.

How to use
- Push your code to GitHub (or create the repository if you haven't).
- Ensure GitHub Actions is enabled for the repository.
- Trigger the workflow:
  - Option A: Manual run — GitHub UI > Actions > Android Debug APK > Run workflow.
  - Option B: Push changes — pushing `.py` files or `buildozer.spec` triggers the build automatically.

Artifacts
- On success, the APK(s) will be available under the workflow run as an artifact named `android-debug-apk`.
- Download and share the `*-debug.apk` file with testers/friends.

Caching
- The workflow caches `~/.buildozer` and `~/.gradle` across runs to speed up subsequent builds.

Notes
- This is a debug build (already debug-signed). Suitable for personal testing and sharing outside app stores.
- If the build fails due to upstream SDK downloads or flaky network, simply re-run the job; caches should help after the first successful setup.
