import os
import re

frontend_dir = 'frontend'

def strip_auth():
    for filename in os.listdir(frontend_dir):
        if filename.endswith('.html'):
            path = os.path.join(frontend_dir, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Broad pattern to catch any script that redirects to login.html if token is missing
                # Matches: <script> ... if (!localStorage.getItem("token")) { ... window.location.href = "login.html" ... } ... </script>
                pattern = r'<script>.*?if\s*\(!localStorage\.getItem\([\'"]token[\'"]\)\).*?login\.html.*?</script>'
                
                new_content = re.sub(pattern, '', content, flags=re.DOTALL | re.MULTILINE)
                
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Removed auth from {filename}")
                else:
                    print(f"No auth script found in {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    strip_auth()
