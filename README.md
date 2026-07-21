# VCE English Exam Preparation Guide — Website

A browsable static website built from the South Oakleigh College *Units 3/4 English
Exam Preparation Guide* (2026). All content from the booklet is included: 12 parts,
30 images, 15 embedded practice-exam / reference PDFs, and full-text heading search.

The site is plain HTML/CSS/JS in `public/` — no build step, no dependencies.

## Deploy to GitLab Pages (your NMO-SOC account)

1. Create a **new blank project** on GitLab (e.g. `vce-english-guide`) — do not add a README.
2. In a terminal, from **inside this folder** (`vce-english-site`), run:

   ```bash
   git init
   git add .
   git commit -m "VCE English exam prep website"
   git branch -M main
   git remote add origin https://gitlab.com/NMO-SOC/vce-english-guide.git
   git push -u origin main
   ```

   Replace the remote URL with your project's URL if the path differs.

3. GitLab runs the `pages` job automatically (see `.gitlab-ci.yml`). After it finishes
   (Build → Pipelines), your site is live at:

   ```
   https://NMO-SOC.gitlab.io/vce-english-guide/
   ```

   Find the exact URL under **Deploy → Pages** in the project sidebar.

### Note on relative paths
All links in the site are **relative**, so it works from a project subpath
(`/vce-english-guide/`) without changes. If you later host it at a custom domain
root, nothing needs to change.

## Deploy to GitHub Pages instead (optional)
The same folder also contains `.github/workflows/pages.yml`. Push this folder to a
GitHub repo, then enable **Settings → Pages → Source: GitHub Actions**. The workflow
publishes `public/` automatically. (You can delete `.gitlab-ci.yml` or the `.github`
folder depending on which host you use.)

## Editing content
The site is generated from the LaTeX source (`main.tex`) in the booklet project.
To regenerate after editing the booklet, re-run the build script (`build.py`) used
to create this site.

## Structure
```
public/
  index.html                 landing page + contents
  part-01 … part-12 .html    one page per Part
  assets/
    style.css  site.js  search.json
    img/     images from the booklet
    pdf/     embedded practice exams & reference PDFs
    files/   downloadable attachments (script, exam generator)
.gitlab-ci.yml               GitLab Pages deploy
.github/workflows/pages.yml  GitHub Pages deploy (optional)
```
