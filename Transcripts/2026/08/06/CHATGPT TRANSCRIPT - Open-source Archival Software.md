# Open-source Archival Software

- URL: https://chatgpt.com/c/6a74855a-0b5c-83ea-be7b-d9d97c4ce2af
- Created: 2026-08-06T13:00:21.093Z

---

> opensource archival software, maybe to capture a page to put it on the free archive?

I’ll separate tools that make a local archival copy from tools that submit a page to a public free archive.

```json
{"system2_search_query":[{"q":"open source web page archiving software ArchiveBox official"},{"q":"open source web archiving Browsertrix Crawler official"},{"q":"Internet Archive Save Page Now official API browser extension open source"},{"q":"Webrecorder ArchiveWeb.page open source official"}],"response_length":"long"}
```

<details><summary>💭 Thinking</summary>

**Choosing archival software**

I’m comparing simple public snapshots with full local captures. For a one-off page, I’d use Wayback Machine’s Save Page Now. For richer preservation, ArchiveWeb.page or ArchiveBox can save WARC/WACZ files, while Browsertrix suits larger crawls.

**Chose archival software**

**Searched 17 websites**

</details>

Assuming “the free archive” means the **Internet Archive’s Wayback Machine**:

### Best simple option: Wayback Machine extension

The official **Wayback Machine browser extension is open source**. Open the page, select **Save Page Now**, and it creates a public archived URL. It is suitable for individual public pages. citeturn716061search12turn116314search0

Save Page Now generally captures only the submitted page—not an entire directory or website—and some dynamic, login-protected, or blocked pages will not archive correctly. citeturn116314search4turn116314search24

### Better capture quality: ArchiveWeb.page

**ArchiveWeb.page** is an open-source browser extension and desktop application. You start recording, browse or interact with the page, then export the capture as **WARC** or **WACZ**. This is often better for JavaScript-heavy and interactive pages. citeturn716061search0turn116314search7

It creates a portable local archive; it does **not automatically publish the result to the Wayback Machine**. You can replay the exported file with ReplayWeb.page. citeturn116314search14turn116314search20

### Best self-hosted option: ArchiveBox

**ArchiveBox** runs on your own computer or server and saves pages in several formats, including HTML, screenshots, PDF, WARC, media and metadata. It is useful for maintaining a searchable personal collection or processing lists of URLs. citeturn716061search2turn116314search19

For public URLs, ArchiveBox can also request that Archive.org archive the URL while retaining its own local copy. Do not enable that submission for private, authenticated or sensitive pages. citeturn116314search2

### For entire websites

Use **Browsertrix Crawler** for modern, browser-based site crawls, or **Heritrix** for large, institutional-style crawls. Both are open source and produce archival WARC data. citeturn716061search5turn716061search27turn116314search15

**Practical recommendation:** use the Wayback extension for a quick public citation; use ArchiveWeb.page as a second, higher-fidelity local copy.

