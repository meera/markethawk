#!/bin/bash
# Clean up duplicate markethawk mounts
# Run: ./cleanup-mounts.sh

set -e

echo "Cleaning up markethawk mounts..."

# Unmount duplicates if they exist
if mount | grep -q "/Volumes/markethawk-1"; then
    echo "Unmounting /Volumes/markethawk-1..."
    umount /Volumes/markethawk-1
fi

if mount | grep -q "/Volumes/markethawk-2"; then
    echo "Unmounting /Volumes/markethawk-2..."
    umount /Volumes/markethawk-2
fi

# Mount to clean location
echo "Mounting to /Volumes/markethawk..."
mount -t smbfs //meera@192.168.1.101/markethawk /Volumes/markethawk

# Update symlink
echo "Updating /var/markethawk symlink..."
sudo rm -f /var/markethawk
sudo ln -s /Volumes/markethawk /var/markethawk

# Verify
echo ""
echo "✓ Mounts cleaned up!"
echo ""
echo "Active mounts:"
mount | grep markethawk
echo ""
echo "Symlink:"
ls -la /var/markethawk
echo ""
echo "Data directory:"
ls -la /var/markethawk/_downloads 2>/dev/null || echo "(No _downloads yet)"
