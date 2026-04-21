import os

frontend_dir = 'frontend'

def finalize_admin():
    for filename in os.listdir(frontend_dir):
        if filename.endswith('.html'):
            path = os.path.join(frontend_dir, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 1. Simple string replacements for the role logic
                new_content = content.replace('role ? role.toUpperCase() : "STAFF"', '"ADMIN"')
                new_content = new_content.replace('role ? role.toUpperCase() : \'STAFF\'', '"ADMIN"')
                
                # 2. General terminology cleanup
                new_content = new_content.replace('Staff Panel', 'Admin Panel')
                new_content = new_content.replace('Staff Dashboard', 'Admin Dashboard')
                new_content = new_content.replace('Staff Hub', 'Admin Hub')
                new_content = new_content.replace('Staff Portal', 'Admin Control')
                
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated {filename} to Admin Panel")
                else:
                    print(f"No Staff terminology found in {filename}")
            except Exception as e:
                print(f"Error in {filename}: {e}")

if __name__ == "__main__":
    finalize_admin()
