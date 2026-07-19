import os

def create_sample_files():
    system_dir = os.path.join("system_files", "test-system")
    os.makedirs(system_dir, exist_ok=True)

    readme_path = os.path.join(system_dir, "README.md")
    with open(readme_path, "w") as f:
        f.write("# Test System\n\nThis is a sample file for testing the download endpoint.\n")

    index_path = os.path.join(system_dir, "index.js")
    with open(index_path, "w") as f:
        f.write('console.log("Hello from Test System");\n')

    print(f"Sample files created in {system_dir}")

if __name__ == "__main__":
    create_sample_files()
