# How to push to GitHub

1. Create a new repository on GitHub, e.g. `hermes-hybrid-memory` under your account.
2. Add the remote and push:

```bash
cd /opt/hermes-hybrid-memory
git remote add origin https://github.com/YOUR_USERNAME/hermes-hybrid-memory.git
git branch -M main
git push -u origin main
```

If you use a PAT, replace the URL with:
```bash
git remote add origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/hermes-hybrid-memory.git
```

Or configure SSH:
```bash
git remote add origin git@github.com:YOUR_USERNAME/hermes-hybrid-memory.git
```

3. After push, update `README.md` and `POST.draft.md` with the real repository URL.
