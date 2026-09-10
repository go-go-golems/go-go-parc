// Usage: node render-diagrams.cjs ARTICLE PLAYWRIGHT_MODULE MERMAID_BUNDLE
// Isolated render check; does not launch or modify the user's browser session.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const [article, playwright, mermaid] = process.argv.slice(2);
const {chromium} = require(playwright);
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
(async () => {
  const text = fs.readFileSync(article, 'utf8');
  const blocks = [...text.matchAll(/^```mermaid\n([\s\S]*?)\n```/gm)];
  if (blocks.length !== 3) throw new Error(`Expected three diagrams, got ${blocks.length}`);
  const browser = await chromium.launch({headless:true});
  try {
    const page = await browser.newPage({viewport:{width:1100,height:1400}});
    const figures = [];
    for (let i=0; i<blocks.length; i++) {
      await page.setContent('<html><body style="margin:0;background:white"><div id="diagram"></div></body></html>');
      await page.addScriptTag({path:mermaid});
      const svg = await page.evaluate(async ({source,id}) => {
        mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'neutral'});
        const {svg} = await mermaid.render(id,source);
        document.querySelector('#diagram').innerHTML = svg;
        return svg;
      }, {source:blocks[i][1], id:`friction${i+1}`});
      const name = `figure-${i+1}`;
      fs.writeFileSync(path.join(__dirname,`${name}.svg`),svg+'\n');
      await page.locator('#diagram svg').screenshot({path:path.join(__dirname,`${name}.png`)});
      figures.push({name,source_sha256:hash(blocks[i][1]),box:await page.locator('#diagram svg').boundingBox()});
    }
    const receipt = {browser:await browser.version(),mermaid_bundle_sha256:hash(fs.readFileSync(mermaid)),renderer_sha256:hash(fs.readFileSync(__filename)),figures,note:'Rendering success is not visual review; review each PNG separately.'};
    fs.writeFileSync(path.join(__dirname,'render.json'),JSON.stringify(receipt,null,2)+'\n');
    console.log(JSON.stringify(receipt,null,2));
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
