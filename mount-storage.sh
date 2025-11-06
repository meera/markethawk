#!/bin/bash
# Mount earninglens storage
# Run: ./mount-storage.sh

set -e

echo "Mounting earninglens storage..."

# Unmount any existing mounts (including -1, -2 duplicates)
for mount_point in /Volumes/earninglens /Volumes/earninglens-1 /Volumes/earninglens-2; do
    if mount | grep -q "$mount_point"; then
        echo "Unmounting $mount_point..."
        umount "$mount_point" 2>/dev/null || true
    fi
done

# Mount to clean location
echo "Mounting to /Volumes/earninglens..."
mount -t smbfs //meera@192.168.1.101/earninglens /Volumes/earninglens

# Update symlink
echo "Updating /var/earninglens symlink..."
sudo rm -f /var/earninglens
sudo ln -s /Volumes/earninglens /var/earninglens

echo ""
echo "✓ Mounted /Volumes/earninglens"
ls -ld /Volumes/earninglens

# Check if we can write to it
if [ -w /Volumes/earninglens ]; then
    echo "✓ Write access confirmed"
else
    echo "⚠ No write access - check permissions on Linux server (192.168.1.101:/var/earninglens)"
fi
