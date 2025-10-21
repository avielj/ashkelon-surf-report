#!/bin/bash
# Auto-update Ashkelon Surf Sensor from GitHub
# Usage: bash update_from_github.sh

set -e

GITHUB_REPO="avielj/ashkelon-surf-report"
GITHUB_BRANCH="main"
COMPONENT_NAME="ashkelon_surf"
HA_CONFIG_DIR="${HA_CONFIG_DIR:-/config}"
CUSTOM_COMPONENTS_DIR="$HA_CONFIG_DIR/custom_components/$COMPONENT_NAME"

echo "🌊 Ashkelon Surf Sensor - Auto Updater"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if custom component exists
if [ ! -d "$CUSTOM_COMPONENTS_DIR" ]; then
    echo -e "${RED}❌ Component not found at: $CUSTOM_COMPONENTS_DIR${NC}"
    echo -e "${YELLOW}Please install the component first.${NC}"
    exit 1
fi

echo -e "${GREEN}📍 Found component at: $CUSTOM_COMPONENTS_DIR${NC}"
echo ""

# Backup current version
BACKUP_DIR="$HA_CONFIG_DIR/backups/ashkelon_surf_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "💾 Creating backup..."
cp -r "$CUSTOM_COMPONENTS_DIR" "$BACKUP_DIR/"
echo -e "${GREEN}✅ Backup saved to: $BACKUP_DIR${NC}"
echo ""

# Download latest files from GitHub
echo "📥 Downloading latest version from GitHub..."

FILES=("sensor.py" "__init__.py" "manifest.json")
BASE_URL="https://raw.githubusercontent.com/$GITHUB_REPO/$GITHUB_BRANCH/home-assistant"

for file in "${FILES[@]}"; do
    echo "  ⬇️  Downloading $file..."
    curl -sS -o "$CUSTOM_COMPONENTS_DIR/$file" "$BASE_URL/$file"
    
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} $file updated"
    else
        echo -e "  ${RED}✗${NC} Failed to download $file"
        echo -e "${YELLOW}Rolling back from backup...${NC}"
        rm -rf "$CUSTOM_COMPONENTS_DIR"
        cp -r "$BACKUP_DIR/$COMPONENT_NAME" "$CUSTOM_COMPONENTS_DIR"
        exit 1
    fi
done

echo ""
echo -e "${GREEN}✅ All files updated successfully!${NC}"
echo ""
echo -e "${YELLOW}⚠️  Please restart Home Assistant for changes to take effect.${NC}"
echo ""
echo "Restart command:"
echo "  ha core restart"
echo ""
echo -e "Backup location: ${BACKUP_DIR}"
echo ""
echo "To rollback if needed:"
echo "  rm -rf $CUSTOM_COMPONENTS_DIR"
echo "  cp -r $BACKUP_DIR/$COMPONENT_NAME $CUSTOM_COMPONENTS_DIR"
echo "  ha core restart"
echo ""
