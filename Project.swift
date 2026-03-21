import ProjectDescription

let project = Project(
    name: "MyPrivateLib",
    targets: [
        .target(
            name: "MyPrivateLib",
            destinations: .iOS,
            product: .framework,
            bundleId: "observer.universe.MyPrivateLib",
            deploymentTargets: .iOS("13.0"),
            sources: ["Sources/MyPrivateLib/**/*.swift"],
            settings: .settings(base: [
                "SWIFT_VERSION": "6.0",
                "SKIP_INSTALL": "NO",
                "BUILD_LIBRARY_FOR_DISTRIBUTION": "YES",
                "CODE_SIGN_IDENTITY": "",
                "CODE_SIGN_STYLE": "Manual",
            ]),
        ),
        .target(
            name: "MyPrivateLibTests",
            destinations: .iOS,
            product: .unitTests,
            bundleId: "observer.universe.MyPrivateLibTests",
            deploymentTargets: .iOS("13.0"),
            sources: ["Tests/MyPrivateLibTests/**/*.swift"],
            dependencies: [
                .target(name: "MyPrivateLib"),
            ],
        ),
    ],
)
