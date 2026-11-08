# Ryan Xu Academic Website

A minimal three-tab academic website: **Home / CV / Research**, inspired by the restrained layout of perisadavutoglu.com. The research page has one featured project and a searchable scholarly literature feed with topic and sorting controls, paper abstracts, optional AI paper summaries, and monthly AI overviews.

## Local preview

From this directory, run:

```bash
python -m http.server 8000
```

Open http://localhost:8000 . A local server is needed for `fetch('papers.json')`.

## Make it yours

- Edit the text in `index.html`. The sample academic biography and project descriptions should be reviewed before publishing.
- Edit visual variables at the beginning of `styles.css`.
- The CV tab displays a single Google Drive link. To update it, change the URL and the "last updated" month in `index.html`. Ensure the Google Drive sharing settings allow visitors to view it.
- Set up your own domain after initial deployment.

## Research tracking

`update_research.py` searches **OpenAlex** for recent scholarly works on four themes. It retrieves actual bibliographic records and filters them by keywords and IO/global governance relevance. Papers are deduplicated and ranked by a transparent heuristic; summaries default to the actual OpenAlex abstract (when available).

The site displays up to 20 records at a time, with **Topic** (All themes, legitimacy, reputation, credibility, trust), **Sort** (newest, relevance, oldest), a paper window, an expandable original **Abstract**, and an **AI Summary** when generated. A **Monthly AI Summary** synthesizes abstracts from the most recent indexed publication month when AI processing is enabled. It shows only in the All themes view, because the synthesis covers all selected topics. The initial `papers.json` is intentionally empty. This is **not a live research feed** until the updater runs successfully.

1. Obtain an OpenAlex API key if necessary and set it as the `OPENALEX_API_KEY` environment variable.
2. Run `python update_research.py`. If successful, it writes `papers.json`.
3. Optionally run `pip install openai`, set `OPENAI_API_KEY` in your environment, then run the script again for abstract-based AI summaries of up to 20 recent papers and monthly digests for up to 3 publication months.
4. Review output before sharing important academic findings.

An automated GitHub Actions workflow in `.github/workflows/research-radar.yml` attempts to refresh the dataset every Monday. Add `OPENALEX_API_KEY` and optionally `OPENAI_API_KEY` as GitHub repository **Actions secrets**. Do not paste keys into client-side JavaScript or into commits. In repository Settings > Pages, select **Deploy from a branch**, `main`, `/ (root)`. Scheduled jobs can be delayed or disabled under GitHub settings, so monitor runs occasionally.

**Limitations:** The search window is based on publication dates, not the date works were first indexed. Monthly summaries group selected papers by publication month and do not claim to cover all papers published that month. Consequently, newly indexed older papers may be missed. Ranking is keyword-based, not a validated measure of conceptual relevance. Author names, dates, DOI, and abstracts should be verified against publication originals. A public site is not a substitute for systematic literature review.

## Sources

- https://docs.openalex.org/ and https://help.openalex.org/api/
- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

## Deploy

Create a GitHub repository, push these files, and enable GitHub Pages. The site works as static HTML/CSS/JS (no paid hosting required). The API requests occur in the Python updater, not in visitors' browsers.


## Custom domain: shixiongxu.com (IONOS)

The root `CNAME` file already contains `shixiongxu.com`. After uploading the site, enable GitHub Pages from the `main` branch / root and set **Settings → Pages → Custom domain** to `shixiongxu.com` **before** configuring DNS. GitHub recommends verifying ownership of the domain as well.

In IONOS → Domains & SSL → shixiongxu.com → DNS, use four `A` records for host `@`:

- `185.199.108.153`
- `185.199.109.153`
- `185.199.110.153`
- `185.199.111.153`

For `www`, add a `CNAME` with host `www` and value `YOUR-GITHUB-USERNAME.github.io` (replace the placeholder with your GitHub account name). Delete/replace conflicting parking records only after reviewing what they do. Do not remove MX/TXT records used for email. Enable **Enforce HTTPS** in GitHub Pages once available. DNS propagation may take up to 24 hours. Official documentation: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site

The homepage photo is at `assets/sequoia-home.jpg`. The `CV` tab links to your Google Drive CV; check the sharing permission before publishing. Research Radar needs OpenAlex configuration and an initial update before it displays papers.
