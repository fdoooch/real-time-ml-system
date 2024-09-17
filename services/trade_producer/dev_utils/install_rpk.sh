#!/bin/bash

# Download the latest rpk binary
if ! curl -LO https://github.com/redpanda-data/redpanda/releases/latest/download/rpk-linux-amd64.zip; then
    echo "Failed to download rpk. Please check your internet connection and try again."
    exit 1
fi

# Unzip the file
if ! unzip rpk-linux-amd64.zip; then
    echo "Failed to unzip rpk. Please make sure 'unzip' is installed: sudo apt install unzip"
    exit 1
fi

# Move rpk to a directory in your PATH
if ! sudo mv rpk /usr/local/bin/; then
    echo "Failed to move rpk to /usr/local/bin/. Please check your permissions."
    exit 1
fi

# Make it executable
if ! sudo chmod +x /usr/local/bin/rpk; then
    echo "Failed to make rpk executable. Please check your permissions."
    exit 1
fi

# Verify the installation
if rpk version; then
    echo "rpk has been successfully installed!"
else
    echo "rpk installation seems to have failed. Please check the error messages above."
fi

# Clean up
rm rpk-linux-amd64.zip