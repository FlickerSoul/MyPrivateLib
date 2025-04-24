#! /bin/bash

set -e

source scripts/set-version.sh

echo "Building XCFramework For Version '${SDK_VERSION}'..."

export PROJECT_PATH="MyPrivateLib.xcodeproj"
export FRAMEWORK_NAME="MyPrivateLib"
export SCHEME_NAME="MyPrivateLib"
export ARCHIVE_PATH="./.build"
export XCFRAMEWORK_OUTPUT="${ARCHIVE_PATH}/Product"
export XCFRAMEWORK_PATH="${XCFRAMEWORK_OUTPUT}/${FRAMEWORK_NAME}-${SDK_VERSION}.xcframework"

PLATFORMS=("iOS" "iOS Simulator")

rm -rf "${ARCHIVE_PATH}"
mkdir -p "${ARCHIVE_PATH}"

for PLATFORM in "${PLATFORMS[@]}"; do
    # Replace spaces with hyphens for archive filenames
    SAFE_NAME="${PLATFORM// /-}"

    DEST="generic/platform=${PLATFORM}"
    OUT_ARCHIVE="${ARCHIVE_PATH}/${SAFE_NAME}.xcarchive"

    echo "▸ Archiving for ${PLATFORM} → ${OUT_ARCHIVE}"
    xcodebuild archive \
      -project "${PROJECT_PATH}" \
      -scheme "${SCHEME_NAME}" \
      -configuration "${CONFIGURATION}" \
      -destination "${DEST}" \
      -archivePath "${OUT_ARCHIVE}" \
      -skipPackagePluginValidation \
      -skipMacroValidation \
      SKIP_INSTALL=NO \
      BUILD_LIBRARY_FOR_DISTRIBUTION=YES
done

echo "Building XCFramework Creation Args..."
ARGS=()
for PLATFORM in "${PLATFORMS[@]}"; do
  SAFE_NAME="${PLATFORM// /-}"
  ARCHIVE_FILE="${ARCHIVE_PATH}/${SAFE_NAME}.xcarchive"
  ARGS+=(-archive "${ARCHIVE_FILE}" -framework "${FRAMEWORK_NAME}.framework")
done

echo "Creating XCFramework..."
xcodebuild -create-xcframework \
  "${ARGS[@]}" \
  -output "${XCFRAMEWORK_PATH}"

if [ "$GITHUB_ACTIONS" = "true" ]; then
  # Export the variable for later steps in the workflow
  echo "Export output path to GitHub"
  echo "XCFRAMEWORK_OUTPUT=$(realpath "${XCFRAMEWORK_OUTPUT}")" >> "$GITHUB_ENV"
  echo "XCFRAMEWORK_PATH=$(realpath "${XCFRAMEWORK_PATH}")" >> "$GITHUB_ENV"
fi

echo "XCFramework created successfully at ${XCFRAMEWORK_PATH}"
