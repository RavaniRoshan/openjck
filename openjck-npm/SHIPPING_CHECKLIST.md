# OpenJCK v0.2.1 Pre-Launch Checklist

This internal document confirms we are ready to ship v0.2.1.

[x] VERSION ALIGNMENT
    - All version strings say 0.2.1: `npm audit` is configured for 0.2.1
    - Health endpoint returning 0.2.1
    - README roadmap confirms v0.2.1 as current

[x] README CLARITY
    - Quick Start is runnable and short
    - Installation instructions cover both npm and pip
    - Roadmap is updated
    - No unshipped features are promised

[x] PACKAGE QUALITY
    - npm audit has zero vulnerabilities natively
    - no unresolved dependencies
    - package.json "main" points to correct file
    - .npmignore excludes tests, docs, env files

[x] CLI BEHAVIOR
    - `npx openjck` shows colored ascii banner
    - Links to docs, repo, support are visible
    - Ctrl+C cleanly stops the server and process

[x] DASHBOARD CONSOLIDATION
    - Single source of truth at `openjck-npm/src/ui/index.html`
    - Removed duplicate Python FastAPI static HTML
    - Fallback message added in Python when UI accessed via its server

[x] PYTHON PACKAGE
    - `__version__` bumped down to 0.2.1
    - No backward compatibility breaks

## Next Steps for Publisher
1. `cd openjck-npm && npm publish`
2. `python -m build && twine upload dist/*`
3. Push `v0.2.1` tag to git and create GitHub Release
4. Share on PH/Twitter
