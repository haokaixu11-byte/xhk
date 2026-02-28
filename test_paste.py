"""
Test clipboard image paste via Playwright with actual image injection
"""
import asyncio
import base64
import os

# Create a small test PNG (8x8 red square) as base64
# This is a valid minimal PNG
PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAFklEQVQI12P8"
    "z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=="
)
PNG_BYTES = base64.b64decode(PNG_BASE64)

async def main():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            permissions=["clipboard-read", "clipboard-write"],
        )
        page = await ctx.new_page()
        
        # Collect console messages
        messages = []
        page.on("console", lambda m: messages.append(f"[{m.type}] {m.text}"))
        
        await page.goto("https://3000-irwjpbeuyfymnkyphrwgp-2e77fc33.sandbox.novita.ai/paste-debug.html", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        
        print("=== Page loaded ===")
        
        # Write image to system clipboard via JS
        print("\n--- Writing image to clipboard via JS ---")
        write_result = await page.evaluate("""async () => {
            try {
                const base64 = '""" + PNG_BASE64 + """';
                const byteStr = atob(base64);
                const bytes = new Uint8Array(byteStr.length);
                for (let i = 0; i < byteStr.length; i++) bytes[i] = byteStr.charCodeAt(i);
                const blob = new Blob([bytes], { type: 'image/png' });
                const item = new ClipboardItem({ 'image/png': blob });
                await navigator.clipboard.write([item]);
                return { ok: true };
            } catch(e) {
                return { ok: false, error: e.message };
            }
        }""")
        print(f"Clipboard write result: {write_result}")
        
        if not write_result.get("ok"):
            print("CLIPBOARD WRITE FAILED - trying DataTransfer simulation instead")
        
        await asyncio.sleep(1)
        
        # Now simulate paste event with DataTransfer containing image
        print("\n--- Simulating paste event with image ---")
        paste_result = await page.evaluate("""async () => {
            try {
                // Build a DataTransfer with the image
                const base64 = '""" + PNG_BASE64 + """';
                const byteStr = atob(base64);
                const bytes = new Uint8Array(byteStr.length);
                for (let i = 0; i < byteStr.length; i++) bytes[i] = byteStr.charCodeAt(i);
                const blob = new Blob([bytes], { type: 'image/png' });
                const file = new File([blob], 'test.png', { type: 'image/png' });
                
                const dt = new DataTransfer();
                dt.items.add(file);
                
                const event = new ClipboardEvent('paste', {
                    clipboardData: dt,
                    bubbles: true,
                    cancelable: true
                });
                
                // Dispatch on body (window listener should catch it)
                document.body.dispatchEvent(event);
                
                return { ok: true, itemCount: dt.items.length };
            } catch(e) {
                return { ok: false, error: e.message };
            }
        }""")
        print(f"Paste simulation result: {paste_result}")
        
        await asyncio.sleep(2)
        
        # Check if image was placed
        img_src = await page.evaluate("""() => {
            const img = document.querySelector('#canvas-area img');
            return img ? img.src.slice(0, 60) : null;
        }""")
        print(f"\nImage in canvas area: {img_src}")
        
        # Check console messages  
        print("\n=== Console messages ===")
        for m in messages:
            print(m)
        
        # Now test the actual ProtoFlow app
        print("\n\n=== Testing actual ProtoFlow app ===")
        
        page2 = await ctx.new_page()
        msgs2 = []
        page2.on("console", lambda m: msgs2.append(f"[{m.type}] {m.text}"))
        
        await page2.goto("https://3000-irwjpbeuyfymnkyphrwgp-2e77fc33.sandbox.novita.ai", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        
        # Write image to clipboard
        await page2.evaluate("""async () => {
            const base64 = '""" + PNG_BASE64 + """';
            const byteStr = atob(base64);
            const bytes = new Uint8Array(byteStr.length);
            for (let i = 0; i < byteStr.length; i++) bytes[i] = byteStr.charCodeAt(i);
            const blob = new Blob([bytes], { type: 'image/png' });
            const item = new ClipboardItem({ 'image/png': blob });
            await navigator.clipboard.write([item]);
        }""")
        
        # Click on canvas to make sure canvas has focus
        canvas_el = page2.locator('.page-canvas')
        if await canvas_el.count() > 0:
            await canvas_el.click()
        await asyncio.sleep(0.5)
        
        # Count elements before paste
        before_count = await page2.evaluate("""() => document.querySelectorAll('.el-wrapper').length""")
        print(f"Elements before paste: {before_count}")
        
        # Simulate paste event on the document
        paste_result2 = await page2.evaluate("""async () => {
            try {
                const base64 = '""" + PNG_BASE64 + """';
                const byteStr = atob(base64);
                const bytes = new Uint8Array(byteStr.length);
                for (let i = 0; i < byteStr.length; i++) bytes[i] = byteStr.charCodeAt(i);
                const blob = new Blob([bytes], { type: 'image/png' });
                const file = new File([blob], 'test-image.png', { type: 'image/png' });
                
                const dt = new DataTransfer();
                dt.items.add(file);
                
                const event = new ClipboardEvent('paste', {
                    clipboardData: dt,
                    bubbles: true,
                    cancelable: true
                });
                
                window.dispatchEvent(event);
                
                return { ok: true };
            } catch(e) {
                return { ok: false, error: e.message };
            }
        }""")
        print(f"ProtoFlow paste simulation: {paste_result2}")
        
        await asyncio.sleep(2)
        
        # Count elements after paste
        after_count = await page2.evaluate("""() => document.querySelectorAll('.el-wrapper').length""")
        print(f"Elements after paste: {after_count}")
        
        if after_count > before_count:
            print(f"\n✅ SUCCESS! Image element was added to canvas ({before_count} -> {after_count} elements)")
        else:
            print(f"\n❌ FAILED: No new element added ({before_count} -> {after_count})")
            print("\nConsole messages from ProtoFlow:")
            for m in msgs2:
                print(m)
        
        await browser.close()

asyncio.run(main())
