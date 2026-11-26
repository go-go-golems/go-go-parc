// From the Jig root: node path/to/01-shadow-query-probe.cjs
// Instrument a temporary copy of the real CPU picking routine. Only count work;
// machine timings and shader performance cannot be inferred from these counts.
const fs = require('node:fs')
const path = require('node:path')
const root = process.cwd()
const {transformSync} = require(path.join(root, '.bin/esbuild/node_modules/esbuild'))
const meshPath = path.join(root, 'import/candela/src/engine/mesh.ts')
const source = fs.readFileSync(meshPath, 'utf8')
const diagSource = fs.readFileSync(path.join(path.dirname(meshPath), 'diag.ts'), 'utf8')
function evaluate(source, dependencies = {}) {
  const code = transformSync(source, {loader:'ts', format:'cjs'}).code
  const module = {exports:{}}
  Function('module','exports','require',code)(module, module.exports, name => {
    if (!Object.hasOwn(dependencies, name)) throw Error('Unexpected dependency ' + name)
    return dependencies[name]
  })
  return module.exports
}
function replaceOnce(source, original, replacement) {
  if (source.split(original).length !== 2) throw Error('Recheck instrumentation: ' + original)
  return source.replace(original,replacement)
}
let probe = source.slice(source.indexOf('export function rayMesh('))
probe = replaceOnce(probe,'rayMesh(def, o, d, tmax = Infinity)','probeMesh(def, o, d, tmax, count, early)')
probe = replaceOnce(probe,'const ni = st.pop()!', 'count.nodes++; const ni = st.pop()!')
probe = replaceOnce(probe,'const s = (N[b + 3] + k) * 28;', 'count.triangles++; const s = (N[b + 3] + k) * 28;')
probe = replaceOnce(probe,'best = t; hit =', 'if (early) return {t}; best = t; hit =')
const {mesh, blasOf, rayMesh, probeMesh} = evaluate(source+'\n'+probe, {'./diag':evaluate(diagSource)})
const part = mesh.torus(1,0.18)
const result = {mesh:'Candela mesh.torus(1,0.18), default tessellation',triangles:part.count,
                nodes:blasOf(part).nNodes, grid:[96,96], workloads:[]}
for (const [name, origin, dir, limit] of [
  ['above', (u,v)=>[u,2,v], [0,-1,0], 4],
  ['below', (u,v)=>[u,-2,v], [0,1,0], 4],
  ['side', (u,v)=>[2,u,v], [-1,0,0], 4],
  ['short segment', (u,v)=>[u,2,v], [0,-1,0], 1],
]) {
  const full = {nodes:0,triangles:0}, early = {nodes:0,triangles:0}
  let hits = 0
  for (let y=0; y<96; y++) for (let x=0; x<96; x++) {
    const pos = origin(((x+0.5)/96-0.5)*2.6,((y+0.5)/96-0.5)*2.6)
    const reference = rayMesh(part,pos,dir,limit)
    const a = probeMesh(part,pos,dir,limit,full,false)
    const b = probeMesh(part,pos,dir,limit,early,true)
    if (!!reference !== !!b || reference?.t !== a?.t) throw Error('Query mismatch')
    if (b) hits++
  }
  result.workloads.push({name,rays:96*96,hits,full,early})
}
console.log(JSON.stringify(result,null,2))
