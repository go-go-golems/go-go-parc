# Packaging and Publishing Chrome Extensions

*A practical guide to building, bundling, and distributing Manifest V3 browser extensions — from local development to the Chrome Web Store.*

---

## 1. The Chrome Extension as a Distribution Format

A Chrome extension is not a single executable file. It is a directory of web assets — HTML, CSS, JavaScript, images, and a manifest — that the browser loads and executes in a privileged context. This simple fact shapes every decision about how you build, package, and distribute your extension.

The browser treats an extension as a miniature web application with special powers: it can inject scripts into arbitrary pages, read and modify the DOM, intercept network requests, and persist data across sessions. But it is still fundamentally a collection of files that the browser reads from disk. The packaging step does not compile or transform the code; it merely collects the files into a format Chrome can install.

This chapter explains the complete lifecycle of a Chrome extension from development to distribution: how to structure your build pipeline, avoid common packaging mistakes, manage signing keys, and get your extension into users' hands.

---

## 2. Manifest V3: The Extension Contract

Every Chrome extension begins with `manifest.json`. This file declares what the extension is, what permissions it needs, and which files to load. Manifest V3, the current version, has strict constraints that affect how you write and package your code.

```json
{
  "manifest_version": 3,
  "name": "Pyxis Component Extractor",
  "version": "1.1.0",
  "permissions": ["activeTab", "storage", "scripting"],
  "host_permissions": ["file://*/*", "http://localhost/*"],
  "content_scripts": [{
    "matches": ["<all_urls>"],
    "js": ["content_scripts/overlay.js"],
    "css": ["content_scripts/overlay.css"],
    "run_at": "document_end"
  }],
  "background": {
    "service_worker": "background/background.js"
  },
  "action": {
    "default_popup": "popup/popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  }
}
```

### Key constraints

**Content Security Policy (CSP).** Manifest V3 enforces a strict CSP that forbids inline scripts, inline event handlers (`onclick="..."`), and `eval()`. Any dynamically generated HTML page must use external scripts with `addEventListener`, not inline handlers. This affects popup pages, options pages, and any HTML your extension generates programmatically.

**Service workers instead of background pages.** The `background` field must point to a single service worker script, not a persistent background page. Service workers are event-driven and terminate when idle, which means you cannot rely on global state persisting between events. State must be stored and retrieved explicitly.

**File paths are relative to the extension root.** Every path in the manifest is resolved relative to the directory containing `manifest.json`. If your content script references `content_scripts/overlay.js`, then `content_scripts/` must be a subdirectory at the same level as `manifest.json`. This seems obvious until a build tool flattens the directory structure and breaks every path.

---

## 3. The Build Pipeline: From Source to Bundle

Modern extensions use ES modules during development but must ship as a single file (or a few files) that Chrome can load without module support. Content scripts, in particular, cannot use ES module imports — even with `"type": "module"` in the manifest. That setting only works for background service workers.

### Why bundling is necessary

Chrome content scripts run in the page's execution context, not the extension's. When a content script tries to execute `import { foo } from './modules/bar.js'`, the browser resolves that import relative to the page's URL, not the extension's. The page sees a request for `./modules/bar.js` and returns a 404. The import fails silently or throws a syntax error.

The solution is to bundle all modules into a single Immediately Invoked Function Expression (IIFE) before packaging. The bundler resolves all imports, tree-shakes unused code, and outputs one self-contained file.

### Vite configuration

Vite, built on Rollup, is well-suited for this task:

```javascript
// vite.config.js
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    lib: {
      entry: 'content_scripts/main.js',
      name: 'MyExtension',
      fileName: () => 'overlay.js',
      formats: ['iife'],
    },
    outDir: 'content_scripts',
    emptyOutDir: false,
  },
});
```

The `iife` format wraps everything in a function that executes immediately, which is what Chrome expects. The `emptyOutDir: false` setting preserves other files in the output directory, such as `overlay.css`.

### Build scripts

```json
{
  "scripts": {
    "build": "vite build",
    "dev": "vite build --watch",
    "clean": "rm -f content_scripts/overlay.js"
  }
}
```

Running `npm run build` produces `content_scripts/overlay.js` in under a second. Running `npm run dev` watches source files and rebuilds on changes, which is useful during active development.

---

## 4. The Packaging Problem: What to Include

The most common mistake in extension packaging is including development dependencies. The `extension/` directory typically contains:

- Source files (`content_scripts/modules/*.js`)
- Build configuration (`vite.config.js`, `package.json`)
- Development dependencies (`node_modules/` — often hundreds of megabytes)
- Generated bundles (`content_scripts/overlay.js`)
- Assets (`icons/`, `popup/`, `background/`)

Only the manifest, the bundle, the assets, and the CSS are needed at runtime. Everything else is dead weight.

### The node_modules trap

A typical `node_modules/` directory for an extension with Vite, Rollup, and html2canvas can exceed 50 megabytes. If you point Chrome's "Pack extension" tool at a folder containing `node_modules/`, it packs the entire 50 MB into the `.crx` file. The extension installs, but it is bloated and slow to load.

The solution is to create a **clean distribution folder** that contains only the files Chrome needs:

```
dist/
├── manifest.json
├── content_scripts/
│   ├── overlay.js
│   └── overlay.css
├── popup/
│   ├── popup.html
│   └── popup.js
├── background/
│   └── background.js
├── icons/
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md
```

This folder is approximately 400-500 KB — a reasonable size for a browser extension.

### Automating with Make

A Makefile can automate the creation of this clean folder:

```makefile
EXTENSION_DIR = extension
DIST_DIR = dist

.PHONY: dist

dist: build
	@rm -rf $(DIST_DIR)
	@mkdir -p $(DIST_DIR)/content_scripts
	@cp $(EXTENSION_DIR)/manifest.json $(DIST_DIR)/
	@cp $(EXTENSION_DIR)/content_scripts/overlay.js $(DIST_DIR)/content_scripts/
	@cp $(EXTENSION_DIR)/content_scripts/overlay.css $(DIST_DIR)/content_scripts/
	@cp -r $(EXTENSION_DIR)/popup $(DIST_DIR)/
	@cp -r $(EXTENSION_DIR)/background $(DIST_DIR)/
	@cp -r $(EXTENSION_DIR)/icons $(DIST_DIR)/
```

Running `make dist` builds the bundle and copies only the necessary files. This folder is what you point Chrome's "Pack extension" tool at.

---

## 5. Chrome Pack Extension: Creating a .crx

Chrome's native extension format is `.crx`. It is essentially a ZIP file with a cryptographic signature prepended. Chrome verifies the signature on installation to ensure the extension has not been tampered with.

### Creating the .crx

1. Open `chrome://extensions/`
2. Toggle **Developer mode** ON
3. Click **"Pack extension"**
4. Select your **clean `dist/` folder** (not the development folder)
5. Chrome creates two files:
   - `extension-name.crx` — the signed extension package
   - `extension-name.pem` — the private signing key

### The private key is everything

The `.pem` file is the most important artifact in this process. It is the private key that corresponds to the public key embedded in the `.crx`. Chrome uses this to:

- Assign a **permanent extension ID** (derived from the public key)
- Verify updates come from the **same author**
- Enable **automatic updates** when a new `.crx` is published

**If you lose the `.pem` file, you cannot update the extension.** Users would have to manually uninstall the old version and install a new one with a different extension ID. All their data (storage, settings) would be lost because Chrome associates storage with the extension ID.

**Store the `.pem` file in a password manager or encrypted backup.** Treat it with the same care as an SSH private key or a code signing certificate.

### Updating the extension

When you release an update:

1. Rebuild the bundle (`npm run build`)
2. Recreate the clean `dist/` folder (`make dist`)
3. Open `chrome://extensions/` → "Pack extension"
4. Select the `dist/` folder
5. **Click "Browse" and select your existing `.pem` file**
6. Chrome creates a new `.crx` with the **same extension ID**

Users who have the old `.crx` installed will receive the update automatically if the extension checks for updates (for self-hosted extensions) or if you publish through the Chrome Web Store.

---

## 6. Distribution Strategies

There are three ways to get an extension into users' hands: drag-and-drop `.crx` installation, self-hosted updates, and the Chrome Web Store.

### Drag-and-drop .crx

The simplest method for internal distribution. The recipient drags the `.crx` file onto `chrome://extensions/` (with Developer mode ON) and Chrome installs it immediately.

**Pros:** No infrastructure needed; works offline; instant installation.

**Cons:** Requires Developer mode ON (which shows a warning banner); users must manually update by repeating the process; no automatic update mechanism.

### Self-hosted with update checks

For extensions distributed through a website or internal portal, you can configure automatic updates by adding an `update_url` to the manifest:

```json
{
  "update_url": "https://example.com/updates.xml"
}
```

The update XML file lists the latest version and download URL:

```xml
<?xml version='1.0' encoding='UTF-8'?>
<gupdate xmlns='http://www.google.com/update2/response' protocol='2.0'>
  <app appid='EXTENSION_ID_HERE'>
    <updatecheck codebase='https://example.com/extension.crx' version='1.2.0' />
  </app>
</gupdate>
```

Chrome checks this URL periodically and downloads the new `.crx` automatically. The extension ID must match, which is why keeping the `.pem` file is essential.

### Chrome Web Store

The official distribution channel. Users install with one click, and Chrome handles updates automatically.

**Steps:**

1. Go to [Chrome Web Store Developer Dashboard](https://chrome.google.com/webstore/devconsole/)
2. Pay the $5 one-time registration fee
3. Click "New item" → upload a `.zip` (not `.crx`)
4. Fill in description, screenshots, category, and privacy policy
5. Submit for review (typically 1-3 business days)

**The Store handles signing.** You do not upload your `.pem` file. The Store signs the extension with its own key and assigns a Store-specific extension ID. This means you cannot seamlessly migrate from self-hosted `.crx` to the Store — users must reinstall.

**Pros:** One-click install for users; automatic updates; discoverability.

**Cons:** Review process; $5 fee; must comply with Store policies; cannot use certain APIs (some are restricted to Store-distributed extensions).

---

## 7. Common Packaging Pitfalls

### Pitfall 1: Including node_modules

**Symptom:** The `.crx` or `.zip` is 50+ MB. Chrome installs slowly or hangs.

**Cause:** The package includes `node_modules/`, `.git/`, or other development artifacts.

**Fix:** Use a clean `dist/` folder. Never point Chrome's "Pack extension" at a folder containing `node_modules/`.

### Pitfall 2: Flattening the directory structure

**Symptom:** Chrome reports "Could not load javascript 'content_scripts/overlay.js' for script. Could not load manifest."

**Cause:** The build tool or copy script placed `overlay.js` at the root instead of inside `content_scripts/`. The manifest references `content_scripts/overlay.js`, so Chrome cannot find it.

**Fix:** Preserve the directory structure. The manifest's paths must match the actual file locations exactly.

### Pitfall 3: Inline event handlers in generated HTML

**Symptom:** Clicking a button in a popup or generated report page does nothing. The console shows: "Refused to execute inline event handler because it violates the following Content Security Policy directive..."

**Cause:** The HTML contains `onclick="..."` or other inline JavaScript. Manifest V3's CSP forbids inline event handlers.

**Fix:** Use a `<script>` block with `addEventListener`:

```javascript
// Wrong — CSP blocks this
<button onclick="window.print()">Print</button>

// Correct
<button id="printBtn">Print</button>
<script>
  document.getElementById('printBtn').addEventListener('click', () => {
    window.print();
  });
</script>
```

### Pitfall 4: Forgetting to rebuild before packaging

**Symptom:** The extension behaves like an older version. Recent fixes or features are missing.

**Cause:** You edited source files but forgot to run `npm run build` before packaging. The `overlay.js` bundle is stale.

**Fix:** Always run the build step before packaging. Automate this with Make: `make dist` should always call `npm run build` first.

### Pitfall 5: Including source maps or development files

**Symptom:** The `.crx` is larger than expected. Source maps or unminified code are present.

**Cause:** The build tool generated `.map` files or you included source modules alongside the bundle.

**Fix:** Exclude `*.map` files and source modules from the `dist/` folder. Only the bundled output is needed.

---

## 8. The Complete Workflow

Here is the complete lifecycle from code change to distributed extension:

```
Edit source files
       |
       v
  npm run build  ————  Vite bundles modules into overlay.js
       |
       v
  make dist      ————  Copies only required files to dist/
       |
       v
  Chrome → Pack extension → select dist/ folder
       |
       v
  Chrome creates:
    - extension.crx  (signed package)
    - extension.pem  (private key — KEEP SAFE)
       |
       v
  Distribute .crx via email, web, or Chrome Web Store
```

For updates:

```
Edit source files
       |
       v
  npm run build
       |
       v
  make dist
       |
       v
  Chrome → Pack extension → select dist/ folder
       |
       v
  Browse → select existing .pem file
       |
       v
  Chrome creates new .crx with SAME extension ID
       |
       v
  Users receive automatic update
```

---

## 9. What to Remember

The most important ideas about Chrome extension packaging:

- **Chrome extensions are directories, not executables.** The packaging step collects files; it does not transform them. What matters is what is in the folder, not how it was built.

- **Content scripts cannot use ES modules.** You must bundle them into a single IIFE. Background service workers can use modules, but content scripts cannot.

- **Never include node_modules in the package.** A clean `dist/` folder should contain only the manifest, the bundle, the assets, and the CSS. Everything else is dead weight.

- **Preserve the directory structure.** The manifest's paths must match the actual file locations. Flattening the structure breaks the extension.

- **The .pem file is your identity.** Losing it means losing the ability to update the extension. Store it with the same care as an SSH private key.

- **The .crx format is for distribution; the .zip format is for the Web Store.** Chrome installs `.crx` files directly, but the Web Store requires a `.zip` upload.

- **CSP affects all dynamically generated HTML.** Inline event handlers and inline scripts are forbidden. Use external `<script>` blocks with `addEventListener`.

- **Build before you package.** Always run the build step before creating the `dist/` folder. Stale bundles are the most common cause of "my fix didn't work" confusion.

If you internalize these principles, packaging and publishing Chrome extensions becomes a mechanical process: build, copy, pack, distribute. The complexity comes from the edge cases — CSP violations, path mismatches, forgotten rebuilds — and now you know how to avoid them.