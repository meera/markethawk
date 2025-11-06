#!/bin/bash
# Clean up duplicate earninglens mounts
# Run: ./cleanup-mounts.sh

set -e

echo "Cleaning up earninglens mounts..."

# Unmount duplicates if they exist
if mount | grep -q "/Volumes/earninglens-1"; then
    echo "Unmounting /Volumes/earninglens-1..."
    umount /Volumes/earninglens-1
fi

if mount | grep -q "/Volumes/earninglens-2"; then
    echo "Unmounting /Volumes/earninglens-2..."
    umount /Volumes/earninglens-2
fi

# Mount to clean location
echo "Mounting to /Volumes/earninglens..."
mount -t smbfs //meera@192.168.1.101/earninglens /Volumes/earninglens

# Update symlink
echo "Updating /var/earninglens symlink..."
sudo rm -f /var/earninglens
sudo ln -s /Volumes/earninglens /var/earninglens

# Verify
echo ""
echo "✓ Mounts cleaned up!"
echo ""
echo "Active mounts:"
mount | grep earninglens
echo ""
echo "Symlink:"
ls -la /var/earninglens
echo ""
echo "Data directory:"
ls -la /var/earninglens/_downloads 2>/dev/null || echo "(No _downloads yet)"
