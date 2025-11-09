#!/bin/bash
# Mount markethawk storage
# Run: ./mount-storage.sh

set -e

echo "Mounting markethawk storage..."

# Unmount any existing mounts (including -1, -2 duplicates)
for mount_point in /Volumes/markethawk /Volumes/markethawk-1 /Volumes/markethawk-2; do
    if mount | grep -q "$mount_point"; then
        echo "Unmounting $mount_point..."
        umount "$mount_point" 2>/dev/null || true
    fi
done

# Mount to clean location
echo "Mounting to /Volumes/markethawk..."
mount -t smbfs //meera@192.168.1.101/markethawk /Volumes/markethawk

# Update symlink
echo "Updating /var/markethawk symlink..."
sudo rm -f /var/markethawk
sudo ln -s /Volumes/markethawk /var/markethawk

echo ""
echo "✓ Mounted /Volumes/markethawk"
ls -ld /Volumes/markethawk

# Check if we can write to it
if [ -w /Volumes/markethawk ]; then
    echo "✓ Write access confirmed"
else
    echo "⚠ No write access - check permissions on Linux server (192.168.1.101:/var/markethawk)"
fi
