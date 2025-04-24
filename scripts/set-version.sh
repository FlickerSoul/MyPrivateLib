#!/bin/bash

export SDK_VERSION=$(head -n 1 VERSION | xargs)
if [ -z "$SDK_VERSION" ]; then
  echo "Error: VERSION is empty." >&2
  exit 1
fi
