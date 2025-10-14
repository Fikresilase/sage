common_ignores = [
    # ==============================
    # Common build and dependency directories
    # ==============================
    "node_modules/",
    "__pycache__/",
    ".pytest_cache/",
    "target/",
    "build/",
    "dist/",
    "bin/",
    "obj/",
    "out/",
    ".gradle/",
    ".cargo/",
    ".tox/",
    ".next/",
    ".nuxt/",
    ".parcel-cache/",
    ".cache/",
    "coverage/",
    "reports/",
    "public/",  # Often compiled front-end assets
    "generated/",
    "android/app/build/",
    "ios/DerivedData/",
    "",
    # ==============================
    # Version control and metadata
    # ==============================
    ".git/",
    ".svn/",
    ".hg/",
    ".gitlab/",
    ".github/",
    "",
    # ==============================
    # Dependency lock / install files
    # ==============================
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
    "Pipfile.lock",
    "poetry.lock",
    "requirements.txt",  # optional — keep only if dependencies matter
    "composer.lock",
    "Cargo.lock",
    "Gemfile.lock",
    "",
    # ==============================
    # Environments and IDE configs
    # ==============================
    ".env",
    ".env.local",
    ".env.*",
    ".venv/",
    "venv/",
    "env/",
    ".idea/",
    ".vscode/",
    ".vs/",
    "*.iml",
    "",
    # ==============================
    # OS generated or temporary
    # ==============================
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    "~$*",
    "*.swp",
    "*.tmp",
    "*.bak",
    "*.old",
    "*.orig",
    "",
    # ==============================
    # Logs, databases, and runtime data
    # ==============================
    "*.log",
    "*.sqlite",
    "*.sqlite3",
    "*.db",
    "*.pid",
    "*.seed",
    "",
    # ==============================
    # Compiled, bundled, or binary output
    # ==============================
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.class",
    "*.so",
    "*.dll",
    "*.dylib",
    "*.exe",
    "*.o",
    "*.a",
    "*.lib",
    "*.jar",
    "*.war",
    "*.ear",
    "*.apk",
    "*.ipa",
    "*.app",
    "*.wasm",
    "*.map",  # source maps
    "",
    # ==============================
    # Framework-specific junk
    # ==============================
    # Flutter / Dart
    ".dart_tool/",
    ".flutter-plugins",
    ".flutter-plugins-dependencies",
    ".packages",
    "pubspec.lock",
    "generated_plugin_registrant.dart",
    # React / Next / Vue
    ".vercel/",
    ".netlify/",
    ".expo/",
    # Java / Kotlin
    ".idea_modules/",
    "*.jar",
    "*.iml",
    # Rust
    "Cargo.lock",
    "target/",
    # Go
    "go.sum",
    "go.work.sum",
    # C/C++
    "CMakeFiles/",
    "CMakeCache.txt",
    "Makefile",
    "",
    # ==============================
    # Testing and coverage
    # ==============================
    "coverage.xml",
    "coverage-final.json",
    ".coverage",
    "lcov-report/",
    "*.lcov",
    "test-results/",
    "",
        # ==============================
    # Containerization and deployment
    # ==============================
    # "Dockerfile",              
    "docker-compose.yml",
    ".dockerignore",
    "charts/",                 # Helm charts
    "k8s/", "kubernetes/",     # manifests
    ".terraform/", "terraform.tfstate", "*.tfstate.backup",
    ".ansible/",
    "",
    # ==============================
    # Cloud / CI-CD pipelines
    # ==============================
    ".circleci/",
    ".github/workflows/",
    ".gitlab-ci.yml",
    "Jenkinsfile",
    ".travis.yml",
    "azure-pipelines.yml",
    ".drone.yml",
    "",
    # ==============================
    # Documentation builds and site outputs
    # ==============================
    "docs/_build/",
    "mkdocs_site/",
    "book/",
    "_site/",
    ".docusaurus/",
    "",
    # ==============================
    # Backup or editor artifacts
    # ==============================
    "*.sublime-project",
    "*.sublime-workspace",
    "*.code-workspace",
    "*.orig",
    "*.rej",
    "*.tmp",
    "*.bak",
    "*.swp",
    "*.swo",
    "*.tmp",
    "",
    # ==============================
    # Virtualization and OS-specific
    # ==============================
    ".vagrant/",
    ".virtualenv/",
    "*.iso",
    "*.img",
    "*.qcow2",
    "",
    # ==============================
    # Misc auto-generated stuff
    # ==============================
    "node_modules_cache/",
    "typings/",
    "docs/api/",
    "schemas/",
    "examples/",
    "tests/snapshots/",
    "__snapshots__/",
    "sandbox/",
    "",
    # ==============================
    # Data-heavy or private files
    # ==============================
    "data/",
    "*.csv",
    "*.tsv",
    "*.jsonl",
    "*.parquet",
    "*.h5",
    "*.npy",
    "*.pkl",
    "*.pt",
    "*.ckpt",
    "*.weights",
    "*.onnx",
    "*.model",
    "*.ipynb_checkpoints/",
    "",
    # ==============================
    # System or app cache
    # ==============================
    ".mypy_cache/",
    ".ruff_cache/",
    ".pytest_cache/",
    ".coverage_cache/",
    "__snapshots__/",
    ".scannerwork/",
    ".sonarlint/",

    # ==============================
    # Project-specific (example)
    # ==============================
    "Sage/",  # if this is a generated folder in your project
]
