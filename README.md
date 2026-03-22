# MyPrivateLib

This is a close-source Swift package repository that publishes `.xcframework` and distribute it as [a Swift package](https://github.com/FlickerSoul/MyPrivateLibRelease). It also distributes a "private" repository as a private swift package that can only be accessed by clients who have been granted access. You can find the full tutorial on [here](https://universe.observer/posts/2025/publish-xcframework).

## Repository Structure

```
MyPrivateLib/
├── Sources/MyPrivateLib/        # Swift library source code
├── Tests/MyPrivateLibTests/     # Unit tests
├── scripts/
│   ├── archive_proj.py          # Builds the XCFramework for iOS device + simulator,
│   │                            #   zips it, and exports paths/checksum to $GITHUB_ENV
│   ├── upload_release.py        # Creates a draft GitHub release on the binary repo,
│   │                            #   updates Package.swift with the new URL/checksum,
│   │                            #   commits, tags, and pushes to the release repo
│   └── sdk_tools/               # Shared helpers (process utilities, version reading)
├── .github/workflows/
│   ├── release.yaml             # CI: builds & publishes to FlickerSoul/MyPrivateLibRelease
│   └── release-private.yaml     # CI: builds & publishes to FlickerSoul/MyPrivateLibReleasePrivate
├── Package.swift                # SPM manifest (used for local development/tests)
├── Project.swift                # Tuist project definition (used to generate the Xcode project for archiving)
└── Tuist.swift                  # Tuist configuration
```

### Release flow

1. Trigger a release by pushing a new tag to the repository (via drafting a release on GitHub or pushing a tag locally).
2. CI runs `scripts/archive_proj.py` — installs Tuist, generates the Xcode project, archives for iOS device and Simulator, and assembles an `.xcframework` zip.
3. CI runs `scripts/upload_release.py` — creates a draft release on the binary distribution repo, updates `Package.swift` there with the new download URL and checksum, commits, tags, and pushes.
