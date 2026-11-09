# Shixiong Xu academic website

Three-page static academic website: Home, CV, Research.

The Research page contains only the research statement and the UN human rights paper.
The OpenAlex literature tracker, filters, monthly AI summary, and automatic research-update workflow have been removed.

## Upload to GitHub

Replace `index.html`, `script.js`, and `styles.css` in the root of the existing `ryan-shixiongxu/shixiongxu-website` repository. Keep the existing `sequoia-home.jpg` and `CNAME`.

To stop all scheduled updates, delete `.github/workflows/research-radar.yml` from GitHub. You may also delete `update_research.py` and `papers.json` because the site no longer uses them.

Commit the changes and GitHub Pages will redeploy automatically.
