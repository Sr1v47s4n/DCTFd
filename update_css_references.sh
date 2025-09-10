#!/bin/zsh

# Script to update CSS references and clean up unused CSS files

echo "Updating CSS references in templates..."

# Create a backup directory
mkdir -p css_backup

# Backup original CSS files
cp -r static/css/* css_backup/

# Map of old CSS files to new locations
# Format: "old_path:new_path"
CSS_MAP=(
  "css/auth.css:css/components/authentication.css"
  "css/avatar-selection.css:css/components/avatar-selector.css"
  "css/avatar-upload.css:css/components/avatar-upload.css"
  "css/dashboard.css:css/layout/user-dashboard.css"
  "css/ctf-theme.css:css/themes/ctf-theme.css"
  "css/organizer-theme.css:css/themes/organizer-theme.css"
  "css/organizer-dashboard.css:css/layout/organizer-dashboard.css"
  "css/visibility-fixes.css:css/components/visibility-fixes.css"
)

# Update references in template files
for mapping in "${CSS_MAP[@]}"; do
  old_path=$(echo $mapping | cut -d: -f1)
  new_path=$(echo $mapping | cut -d: -f2)
  
  echo "Updating references from $old_path to $new_path"
  find templates -name "*.html" -exec sed -i '' "s|$old_path|$new_path|g" {} \;
done

echo "CSS references updated."

# Remove unused CSS files in the root directory
# We'll keep the original files for now, uncomment this if you want to remove them
# rm -f static/css/auth.css static/css/avatar-selection.css static/css/avatar-upload.css static/css/dashboard.css static/css/ctf-theme.css static/css/organizer-theme.css static/css/organizer-dashboard.css static/css/visibility-fixes.css

echo "Your CSS files have been reorganized into a component/layout/theme structure for better maintainability."
echo ""
echo "If you encounter any issues, you can restore the original files from the css_backup directory."
