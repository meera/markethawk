#!/bin/bash
# Auto-mount earninglens storage on login
# Add to System Settings > Users & Groups > Login Items

# Wait for network (important!)
sleep 5

# Mount via Finder (will use whatever name is available)
open "smb://meera@192.168.1.101/earninglens"

# Wait for mount
sleep 3

# Find the actual mount point
MOUNT_POINT=$(mount | grep earninglens | awk '{print $3}' | head -1)

if [ -n "$MOUNT_POINT" ]; then
    # Update symlink to point to actual mount
    sudo rm -f /var/earninglens
    sudo ln -s "$MOUNT_POINT" /var/earninglens

    echo "✓ Mounted: $MOUNT_POINT"
    echo "✓ Symlink: /var/earninglens -> $MOUNT_POINT"
else
    echo "❌ Failed to mount earninglens"
fi
