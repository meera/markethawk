#!/bin/bash
# Mount sushi's /var/markethawk directory on Mac
# Run once per boot or add to startup

MOUNT_POINT="$HOME/sushi-videos"
SUSHI_HOST="sushi"
SUSHI_PATH="/var/markethawk"

# Check if already mounted
if mount | grep -q "$MOUNT_POINT"; then
  echo "✓ Already mounted at $MOUNT_POINT"
  exit 0
fi

# Create mount point
mkdir -p "$MOUNT_POINT"

# Mount using SSHFS
echo "Mounting sushi:$SUSHI_PATH to $MOUNT_POINT..."

sshfs "$SUSHI_HOST:$SUSHI_PATH" "$MOUNT_POINT" \
  -o auto_cache \
  -o reconnect \
  -o defer_permissions \
  -o noappledouble \
  -o nolocalcaches \
  -o volname=SushiVideos

if [ $? -eq 0 ]; then
  echo "✓ Mounted successfully!"
  echo "  Access files at: $MOUNT_POINT"
  echo ""
  echo "To unmount: umount $MOUNT_POINT"
else
  echo "✗ Mount failed. Install sshfs:"
  echo "  brew install --cask macfuse"
  echo "  brew install gromgit/fuse/sshfs-mac"
fi
