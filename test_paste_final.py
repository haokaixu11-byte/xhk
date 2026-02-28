"""
Final comprehensive test for clipboard image paste.
Tests all 4 paths in the new onPaste implementation:
  Path 1: e.clipboardData.items has image (DataTransfer items)
  Path 2: e.clipboardData.files has image
  Path 3: navigator.clipboard.read() API (real screenshots)
  Path 4: No image, input focused → text paste passes through
  Bonus:  Drag-and-drop still works
  Bonus:  Internal Ctrl+C / Ctrl+V still works for canvas elements
"""
import asyncio, base64, struct, zlib

def make_png(w=80, h=60, color=(180, 90, 200)):
    def chunk(name, data):
        c = zlib.crc32(name + data) & 0xffffffff
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', c)
    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    raw = b''.join(b'\x00' + bytes(color) * w for _ in range(h))
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', zlib.compress(raw))
    png += chunk(b'IEND', b'')
    return png

PNG_B64 = base64.b64encode(make_png()).decode()
APP = "https://3000-irwjpbeuyfymnkyphrwgp-2e77fc33.sandbox.novita.ai"

def paste_via_items(b64, type_='image/png', fname='shot.png'):
    return f"""() => {{
        const b=atob('{b64}'), arr=new Uint8Array(b.length);
        for(let i=0;i<b.length;i++) arr[i]=b.charCodeAt(i);
        const blob=new Blob([arr],{{type:'{type_}'}});
        const file=new File([blob],'{fname}',{{type:'{type_}'}});
        const dt=new DataTransfer(); dt.items.add(file);
        window.dispatchEvent(new ClipboardEvent('paste',{{clipboardData:dt,bubbles:true,cancelable:true}}));
    }}"""

def paste_via_clipboard_read(b64):
    """Monkey-patch navigator.clipboard.read then fire paste event with empty clipboardData"""
    return f"""async () => {{
        const b=atob('{b64}'), arr=new Uint8Array(b.length);
        for(let i=0;i<b.length;i++) arr[i]=b.charCodeAt(i);
        const blob=new Blob([arr],{{type:'image/png'}});
        // Patch clipboard.read to return our image
        const orig = navigator.clipboard.read.bind(navigator.clipboard);
        navigator.clipboard.read = async () => [new ClipboardItem({{'image/png': blob}})];
        // Fire paste event with EMPTY clipboardData (simulates real screenshot paste)
        const dt = new DataTransfer();  // empty - no items
        window.dispatchEvent(new ClipboardEvent('paste',{{clipboardData:dt,bubbles:true,cancelable:true}}));
        await new Promise(r=>setTimeout(r,800));
        navigator.clipboard.read = orig;
    }}"""

async def count(page):
    return await page.evaluate("()=>document.querySelectorAll('.el-wrapper').length")

async def run_test(label, page, js, expected_delta=1):
    before = await count(page)
    if js.strip().startswith('async'):
        await page.evaluate(js)
    else:
        await page.evaluate(js)
    await asyncio.sleep(1.5)
    after = await count(page)
    ok = (after - before) == expected_delta
    print(f"  {'✅' if ok else '❌'} {label}: {before}→{after} (Δ={after-before}, expected Δ={expected_delta})")
    return ok

async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(permissions=["clipboard-read","clipboard-write"])
        page = await ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        
        await page.goto(APP, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        await page.locator('.canvas-stage').click(position={"x":300,"y":300})
        print(f"App loaded: {APP}\n")
        
        passed = failed = 0

        print("=== Path 1: clipboardData.items (normal DataTransfer paste) ===")
        ok = await run_test("image/png via items", page, paste_via_items(PNG_B64))
        passed += ok; failed += not ok

        ok = await run_test("image/x-png (some OS variants)", page,
                            paste_via_items(PNG_B64, 'image/x-png'))
        passed += ok; failed += not ok

        ok = await run_test("image/jpeg via items", page,
                            paste_via_items(PNG_B64, 'image/jpeg', 'photo.jpg'))
        passed += ok; failed += not ok

        print("\n=== Path 3: navigator.clipboard.read() — real screenshot path ===")
        # Focus right panel input first to simulate user typing → then pastes screenshot
        await page.locator('.right-panel input').first.click()
        await asyncio.sleep(0.2)
        active = await page.evaluate("()=>document.activeElement?.tagName")
        print(f"  (RightPanel input focused: {active})")
        ok = await run_test("screenshot (clipboard.read) with input focused",
                            page, paste_via_clipboard_read(PNG_B64))
        passed += ok; failed += not ok

        # Canvas focused
        await page.locator('.canvas-stage').click(position={"x":200,"y":200})
        ok = await run_test("screenshot (clipboard.read) with canvas focused",
                            page, paste_via_clipboard_read(PNG_B64))
        passed += ok; failed += not ok

        print("\n=== Path 4: text paste should NOT create image element ===")
        ok = await run_test("text paste → no new element", page,
                            """() => {
                                const dt = new DataTransfer();
                                dt.setData('text/plain','hello world');
                                window.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true}));
                            }""", expected_delta=0)
        passed += ok; failed += not ok

        print("\n=== Drag-and-drop image ===")
        drop_js = f"""() => {{
            const b=atob('{PNG_B64}'), arr=new Uint8Array(b.length);
            for(let i=0;i<b.length;i++) arr[i]=b.charCodeAt(i);
            const blob=new Blob([arr],{{type:'image/png'}});
            const file=new File([blob],'drag.png',{{type:'image/png'}});
            const dt=new DataTransfer(); dt.items.add(file);
            const stage=document.querySelector('.canvas-stage');
            const rect=stage.getBoundingClientRect();
            stage.dispatchEvent(new DragEvent('dragover',{{dataTransfer:dt,bubbles:true,cancelable:true,clientX:rect.left+300,clientY:rect.top+200}}));
            stage.dispatchEvent(new DragEvent('drop',{{dataTransfer:dt,bubbles:true,cancelable:true,clientX:rect.left+300,clientY:rect.top+200}}));
        }}"""
        ok = await run_test("drag-and-drop image file", page, drop_js)
        passed += ok; failed += not ok

        print("\n=== Internal Ctrl+C / Ctrl+V (canvas elements) ===")
        n_before = await count(page)
        # Select first element
        wrappers = page.locator('.el-wrapper')
        if await wrappers.count() > 0:
            await wrappers.first.click()
            await asyncio.sleep(0.2)
            await page.keyboard.press("Control+c")
            await asyncio.sleep(0.2)
            before_v = await count(page)
            await page.keyboard.press("Control+v")
            await asyncio.sleep(1)
            after_v = await count(page)
            ok = after_v > before_v
            print(f"  {'✅' if ok else '❌'} Ctrl+C/V canvas element: {before_v}→{after_v}")
            passed += ok; failed += not ok
        else:
            print("  ⚠️  No elements to copy")

        print(f"\n{'='*50}")
        print(f"Results: {passed} passed, {failed} failed")
        if errs:
            print("\nPage errors:")
            for e in errs: print(f"  {e}")
        
        await browser.close()
        return failed == 0

import sys
ok = asyncio.run(main())
sys.exit(0 if ok else 1)
