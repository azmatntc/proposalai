bash

# The user's local files are out of date. 
# Generate a shell script they can run to replace just the broken files
cat > /home/azmat/projects/proposalai/fix_svelte_errors.sh << 'EOF'
#!/bin/bash
# Run this from your project root: ~/projects/proposalai/
# It replaces the broken Svelte files with the fixed versions

FRONTEND_DIR="./frontend/src"

if [ ! -d "$FRONTEND_DIR" ]; then
  echo "❌ Run this from ~/projects/proposalai/ (frontend/src directory not found)"
  exit 1
fi

echo "🔧 Applying Svelte fixes..."

# The core fix: replace all app route files
# These files had button-nesting, @const placement, and dynamic class issues

EOF

# Now append each file's content directly into the fix script
python3 << 'PYEOF'
import os

files_to_fix = [
    '/home/azmat/projects/proposalai/frontend/src/routes/(app)/+layout.svelte',
    '/home/azmat/projects/proposalai/frontend/src/routes/(app)/templates/+page.svelte', 
    '/home/azmat/projects/proposalai/frontend/src/routes/(app)/leads/+page.svelte',
    '/home/azmat/projects/proposalai/frontend/src/routes/(app)/proposals/+page.svelte',
    '/home/azmat/projects/proposalai/frontend/src/routes/(app)/dashboard/+page.svelte',
    '/home/azmat/projects/proposalai/frontend/src/routes/(app)/analytics/+page.svelte',
    '/home/azmat/projects/proposalai/frontend/src/routes/(app)/settings/+page.svelte',
    '/home/azmat/projects/proposalai/frontend/src/routes/(auth)/login/+page.svelte',
    '/home/azmat/projects/proposalai/frontend/src/routes/(auth)/register/+page.svelte',
    '/home/azmat/projects/proposalai/frontend/src/routes/+layout.svelte',
    '/home/azmat/projects/proposalai/frontend/src/routes/+page.svelte',
    '/home/azmat/projects/proposalai/frontend/src/lib/api/client.ts',
    '/home/azmat/projects/proposalai/frontend/src/lib/api/types.ts',
    '/home/azmat/projects/proposalai/frontend/src/lib/stores/auth.svelte.ts',
    '/home/azmat/projects/proposalai/frontend/src/lib/stores/ui.svelte.ts',
    '/home/azmat/projects/proposalai/frontend/src/app.css',
    '/home/azmat/projects/proposalai/frontend/src/app.html',
    '/home/azmat/projects/proposalai/frontend/svelte.config.js',
    '/home/azmat/projects/proposalai/frontend/vite.config.ts',
]

script_lines = []

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        continue
    
    # Compute destination path relative to frontend/
    rel = filepath.replace('/home/azmat/projects/proposalai/frontend/', '')
    dest = f'$FRONTEND_DIR/../{rel}'
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Write using a heredoc
    script_lines.append(f'\necho "  Writing {rel}..."')
    script_lines.append(f'mkdir -p "$(dirname "{dest}")"')
    # Use base64 to avoid heredoc escaping issues
    import base64
    encoded = base64.b64encode(content.encode()).decode()
    script_lines.append(f'echo "{encoded}" | base64 -d > "{dest}"')

script_lines.append('\necho ""')
script_lines.append('echo "✅ All files replaced. Now run: cd frontend && npm run dev"')

with open('/home/azmat/projects/proposalai/fix_svelte_errors.sh', 'a') as f:
    f.write('\n'.join(script_lines))

print(f"Fix script written with {len(files_to_fix)} files")
PYEOF

chmod +x /home/azmat/projects/proposalai/fix_svelte_errors.sh
echo "Script ready: $(wc -l < /home/azmat/projects/proposalai/fix_svelte_errors.sh) lines"
echo "Script size: $(du -sh /home/azmat/projects/proposalai/fix_svelte_errors.sh | cut -f1)"