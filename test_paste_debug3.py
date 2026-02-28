"""
Deep diagnostic: what does the browser actually see in clipboardData.items
when a real screenshot is pasted? Let's log ALL items and their types.
Also test: does our paste listener even fire at all?
"""
import asyncio
import base64
import struct, zlib

def make_png(width=50, height=50):
    def chunk(name, data):
        c = zlib.crc32(name + data) & 0xffffffff
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', c)
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    raw = b''
    for y in range(height):
        raw += b'\x00'
        for x in range(width):
            raw += bytes([200, 100, 50])  # orange
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', zlib.compress(raw))
    png += chunk(b'IEND', b'')
    return png

PNG_BYTES = make_png()
PNG_B64 = base64.b64encode(PNG_BYTES).decode()

APP_URL = "https://3000-irwjpbeuyfymnkyphrwgp-2e77fc33.sandbox.novita.ai"

async def main():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(permissions=["clipboard-read", "clipboard-write"])
        page = await ctx.new_page()
        
        msgs = []
        page.on("console", lambda m: msgs.append(f"  [{m.type.upper()}] {m.text}"))
        
        await page.goto(APP_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)

        # ── Inject a diagnostic interceptor into the running Vue app ──────
        print("=== Injecting diagnostic interceptor ===")
        await page.evaluate("""() => {
            window.__pasteLog = [];
            // Intercept ALL paste events before Vue's handler
            window.addEventListener('paste', (e) => {
                const info = {
                    hasClipboardData: !!e.clipboardData,
                    itemCount: e.clipboardData?.items?.length ?? 'null',
                    types: e.clipboardData?.types ? [...e.clipboardData.types] : [],
                    items: [],
                    activeEl: document.activeElement?.tagName + '.' + (document.activeElement?.className?.slice(0,30)||''),
                };
                if (e.clipboardData?.items) {
                    for (let i = 0; i < e.clipboardData.items.length; i++) {
                        const item = e.clipboardData.items[i];
                        const f = item.getAsFile?.();
                        info.items.push({
                            kind: item.kind,
                            type: item.type,
                            canGetFile: !!f,
                            fileSize: f?.size ?? 0,
                        });
                    }
                }
                window.__pasteLog.push(info);
                console.log('PASTE_EVENT_FIRED:', JSON.stringify(info));
            }, true);  // capture phase - fires BEFORE Vue's handler
            console.log('Diagnostic interceptor installed');
        }""")
        await asyncio.sleep(0.3)
        
        # ── Test A: Paste with proper PNG DataTransfer ────────────────────
        print("\n=== Test A: PNG via DataTransfer (normal flow) ===")
        count_before = await page.evaluate("() => document.querySelectorAll('.el-wrapper').length")
        
        await page.evaluate(f"""() => {{
            const b64 = '{PNG_B64}';
            const bStr = atob(b64);
            const arr = new Uint8Array(bStr.length);
            for(let i=0;i<bStr.length;i++) arr[i]=bStr.charCodeAt(i);
            const blob = new Blob([arr], {{type:'image/png'}});
            const file = new File([blob], 'screenshot.png', {{type:'image/png'}});
            const dt = new DataTransfer();
            dt.items.add(file);
            window.dispatchEvent(new ClipboardEvent('paste', {{clipboardData:dt, bubbles:true, cancelable:true}}));
        }}""")
        await asyncio.sleep(1.5)
        count_after = await page.evaluate("() => document.querySelectorAll('.el-wrapper').length")
        print(f"  Elements: {count_before} -> {count_after} {'✅' if count_after>count_before else '❌'}")
        
        # ── Test B: What does macOS/Windows actually put in clipboard? ────
        # On macOS: screenshots are image/png or image/tiff
        # On Windows: screenshots are image/png or image/bmp  
        # Some apps put image/x-png instead of image/png!
        print("\n=== Test B: image/x-png (some OS variants) ===")
        count_before = await page.evaluate("() => document.querySelectorAll('.el-wrapper').length")
        
        await page.evaluate(f"""() => {{
            const b64 = '{PNG_B64}';
            const bStr = atob(b64);
            const arr = new Uint8Array(bStr.length);
            for(let i=0;i<bStr.length;i++) arr[i]=bStr.charCodeAt(i);
            // Some systems report 'image/x-png' instead of 'image/png'
            const blob = new Blob([arr], {{type:'image/x-png'}});
            const file = new File([blob], 'screenshot.png', {{type:'image/x-png'}});
            const dt = new DataTransfer();
            dt.items.add(file);
            window.dispatchEvent(new ClipboardEvent('paste', {{clipboardData:dt, bubbles:true, cancelable:true}}));
        }}""")
        await asyncio.sleep(1.5)
        count_after = await page.evaluate("() => document.querySelectorAll('.el-wrapper').length")
        print(f"  Elements: {count_before} -> {count_after} {'✅' if count_after>count_before else '❌'}")
        
        # ── Test C: What if clipboardData.files has it but not .items? ────
        print("\n=== Test C: File in dt.files but checking items vs files ===")
        check = await page.evaluate(f"""() => {{
            const b64 = '{PNG_B64}';
            const bStr = atob(b64);
            const arr = new Uint8Array(bStr.length);
            for(let i=0;i<bStr.length;i++) arr[i]=bStr.charCodeAt(i);
            const blob = new Blob([arr], {{type:'image/png'}});
            const file = new File([blob], 'test.png', {{type:'image/png'}});
            const dt = new DataTransfer();
            dt.items.add(file);
            return {{
                files_length: dt.files?.length,
                files_0_type: dt.files?.[0]?.type,
                items_length: dt.items?.length,
                items_0_type: dt.items?.[0]?.type,
            }};
        }}""")
        print(f"  DataTransfer check: {check}")
        
        # ── Test D: Simulate paste event with .files approach ────────────
        print("\n=== Test D: Read from e.clipboardData.files instead of .items ===")
        count_before = await page.evaluate("() => document.querySelectorAll('.el-wrapper').length")
        
        # Add a files-based paste listener to test
        files_result = await page.evaluate(f"""async () => {{
            const b64 = '{PNG_B64}';
            const bStr = atob(b64);
            const arr = new Uint8Array(bStr.length);
            for(let i=0;i<bStr.length;i++) arr[i]=bStr.charCodeAt(i);
            const blob = new Blob([arr], {{type:'image/png'}});
            const file = new File([blob], 'test.png', {{type:'image/png'}});
            const dt = new DataTransfer();
            dt.items.add(file);
            
            return {{
                items_len: dt.items.length,
                files_len: dt.files.length,
                files_0_type: dt.files[0]?.type,
            }};
        }}""")
        print(f"  Files approach: {files_result}")
        
        # ── Check paste log ───────────────────────────────────────────────
        print("\n=== Paste event log ===")
        paste_log = await page.evaluate("() => window.__pasteLog")
        for i, entry in enumerate(paste_log):
            print(f"  Event {i+1}: {entry}")
        
        print("\n=== Console messages ===")
        for m in msgs:
            print(m)
        
        await browser.close()

asyncio.run(main())
