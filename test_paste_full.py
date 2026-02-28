"""
Comprehensive paste image test for ProtoFlow
Tests:
1. paste event with image when canvas has focus
2. paste event with image when RightPanel input has focus (the main bug)
3. paste event with image when toolbar input has focus
4. drag-and-drop image file onto canvas
"""
import asyncio
import base64

PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAFklEQVQI12P8"
    "z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=="
)

APP_URL = "https://3000-irwjpbeuyfymnkyphrwgp-2e77fc33.sandbox.novita.ai"

def make_paste_event_js(name="test.png"):
    return f"""async () => {{
        const base64 = '{PNG_BASE64}';
        const byteStr = atob(base64);
        const bytes = new Uint8Array(byteStr.length);
        for (let i = 0; i < byteStr.length; i++) bytes[i] = byteStr.charCodeAt(i);
        const blob = new Blob([bytes], {{ type: 'image/png' }});
        const file = new File([blob], '{name}', {{ type: 'image/png' }});
        const dt = new DataTransfer();
        dt.items.add(file);
        const event = new ClipboardEvent('paste', {{
            clipboardData: dt, bubbles: true, cancelable: true
        }});
        window.dispatchEvent(event);
        return {{ activeElement: document.activeElement?.tagName + '.' + (document.activeElement?.className?.slice(0,30)||'') }};
    }}"""

async def count_elements(page):
    return await page.evaluate("() => document.querySelectorAll('.el-wrapper').length")

async def main():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(permissions=["clipboard-read", "clipboard-write"])
        page = await ctx.new_page()
        
        msgs = []
        page.on("console", lambda m: msgs.append(f"[{m.type}] {m.text}"))
        
        await page.goto(APP_URL, wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        print(f"App loaded: {APP_URL}\n")
        
        passed = 0
        failed = 0

        # ── Test 1: Paste when canvas has focus ─────────────────────────
        print("Test 1: Paste image when canvas has focus")
        await page.locator('.canvas-stage').click(position={"x": 300, "y": 300})
        await asyncio.sleep(0.3)
        before = await count_elements(page)
        result = await page.evaluate(make_paste_event_js("canvas-paste.png"))
        await asyncio.sleep(1.5)
        after = await count_elements(page)
        if after > before:
            print(f"  ✅ PASS: {before} -> {after} elements | active={result['activeElement']}")
            passed += 1
        else:
            print(f"  ❌ FAIL: {before} -> {after} elements | active={result['activeElement']}")
            failed += 1

        # ── Test 2: Paste when RightPanel input has focus (the main bug) ─
        print("\nTest 2: Paste image when RightPanel input has focus (key bug)")
        # Click on an element first so RightPanel shows fields
        # Add a text element via keyboard shortcut to have something selected
        await page.locator('.canvas-stage').click(position={"x": 200, "y": 200})
        await asyncio.sleep(0.3)
        # Select the image element we just added
        wrappers = page.locator('.el-wrapper')
        if await wrappers.count() > 0:
            await wrappers.first.click()
            await asyncio.sleep(0.3)
        
        # Try to focus an input in the right panel
        right_inputs = page.locator('.right-panel input, .right-panel textarea')
        focused_input = False
        if await right_inputs.count() > 0:
            await right_inputs.first.click()
            await asyncio.sleep(0.2)
            active_tag = await page.evaluate("() => document.activeElement?.tagName")
            if active_tag in ('INPUT', 'TEXTAREA'):
                focused_input = True
                print(f"  RightPanel input focused: {active_tag}")
        
        before = await count_elements(page)
        result = await page.evaluate(make_paste_event_js("right-panel-paste.png"))
        await asyncio.sleep(1.5)
        after = await count_elements(page)
        if after > before:
            print(f"  ✅ PASS: {before} -> {after} elements | active={result['activeElement']} | input_focused={focused_input}")
            passed += 1
        else:
            print(f"  ❌ FAIL: {before} -> {after} elements | active={result['activeElement']} | input_focused={focused_input}")
            failed += 1

        # ── Test 3: Paste when toolbar title input has focus ─────────────
        print("\nTest 3: Paste image when toolbar title input has focus")
        title_input = page.locator('.title-input')
        if await title_input.count() > 0:
            await title_input.click()
            await asyncio.sleep(0.2)
        
        before = await count_elements(page)
        result = await page.evaluate(make_paste_event_js("toolbar-paste.png"))
        await asyncio.sleep(1.5)
        after = await count_elements(page)
        if after > before:
            print(f"  ✅ PASS: {before} -> {after} elements | active={result['activeElement']}")
            passed += 1
        else:
            print(f"  ❌ FAIL: {before} -> {after} elements | active={result['activeElement']}")
            failed += 1

        # ── Test 4: Drag and drop image file onto canvas ──────────────────
        print("\nTest 4: Drag-and-drop image file onto canvas")
        before = await count_elements(page)
        drop_result = await page.evaluate(f"""async () => {{
            const base64 = '{PNG_BASE64}';
            const byteStr = atob(base64);
            const bytes = new Uint8Array(byteStr.length);
            for (let i = 0; i < byteStr.length; i++) bytes[i] = byteStr.charCodeAt(i);
            const blob = new Blob([bytes], {{ type: 'image/png' }});
            const file = new File([blob], 'dropped.png', {{ type: 'image/png' }});
            
            const dt = new DataTransfer();
            dt.items.add(file);
            
            const stage = document.querySelector('.canvas-stage');
            if (!stage) return {{ ok: false, error: 'no .canvas-stage' }};
            
            const rect = stage.getBoundingClientRect();
            
            const dragover = new DragEvent('dragover', {{
                dataTransfer: dt, bubbles: true, cancelable: true,
                clientX: rect.left + 400, clientY: rect.top + 300
            }});
            const drop = new DragEvent('drop', {{
                dataTransfer: dt, bubbles: true, cancelable: true,
                clientX: rect.left + 400, clientY: rect.top + 300
            }});
            
            stage.dispatchEvent(dragover);
            stage.dispatchEvent(drop);
            return {{ ok: true }};
        }}""")
        await asyncio.sleep(1.5)
        after = await count_elements(page)
        if after > before:
            print(f"  ✅ PASS: {before} -> {after} elements (drag-drop) | {drop_result}")
            passed += 1
        else:
            print(f"  ❌ FAIL: {before} -> {after} elements | {drop_result}")
            failed += 1

        # ── Summary ───────────────────────────────────────────────────────
        print(f"\n{'='*50}")
        print(f"Results: {passed} passed, {failed} failed")
        print(f"{'='*50}")
        
        if failed == 0:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Some tests failed. Console messages:")
            for m in msgs:
                if '[error]' in m.lower() or '[warn]' in m.lower():
                    print(f"  {m}")
        
        await browser.close()
        return failed == 0

import sys
result = asyncio.run(main())
sys.exit(0 if result else 1)
