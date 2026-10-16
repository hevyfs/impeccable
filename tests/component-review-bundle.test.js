import { test, expect } from 'bun:test';
import { resolve } from 'node:path';
const root=resolve(import.meta.dir,'..');
test('native component review bundle matches the shared UI source',async()=>{
 const result=await Bun.build({entrypoints:[resolve(root,'ui/component-review/entry.ts')],target:'browser',format:'iife',minify:true});
 expect(result.success).toBe(true);
 const generated=await result.outputs[0].text();
 const checkedIn=await Bun.file(resolve(root,'crates/context/assets/component-review.js')).text();
 // On Windows, Git can check out the tracked JS bundle with CRLF, whereas
 // Bun.build emits LF. Compare canonical LF text; still require every
 // executable character to match the shared UI source.
 const canonical=(value)=>value.replace(/\r\n/g,'\n');
 expect(canonical(generated)).toBe(canonical(checkedIn));
});
