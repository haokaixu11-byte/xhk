"""
Test clipboard image paste directly in ProtoFlow app
"""
import asyncio
import base64

PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAFklEQVQI12P8"
    "z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=="
)

async def main():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            permissions=["clipboard-read", "clipboard-write"],
        )
        page = await ctx.new_page()
        
        msgs = []
        errors = []
        page.on("console", lambda m: msgs.append(f"[{m.type}] {m.text}"))
        page.on("pageerror", lambda e: errors.append(str(e)))
        
        print("Loading ProtoFlow app...")
        await page.goto("https://3000-irwjpbeuyfymnkyphrwgp-2e77fc33.sandbox.novita.ai", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(3)
        print("App loaded")
        
        # Check activeElement and canvas stage
        info = await page.evaluate("""() => {
            return {
                activeElement: document.activeElement?.tagName,
                activeClass: document.activeElement?.className,
                hasCanvasStage: !!document.querySelector('.canvas-stage'),
                hasPageCanvas: !!document.querySelector('.page-canvas'),
                elWrappers: document.querySelectorAll('.el-wrapper').length
            }
        }""")
        print(f"Initial state: {info}")
        
        # Click on the stage background area (not on any element)
        stage = page.locator('.canvas-stage')
        await stage.click(position={"x": 300, "y": 300})
        await asyncio.sleep(0.5)
        
        after_click = await page.evaluate("""() => ({
            activeElement: document.activeElement?.tagName,
            activeClass: document.activeElement?.className?.slice(0,40),
        })""")
        print(f"After click on stage: {after_click}")
        
        before_count = await page.evaluate("""() => document.querySelectorAll('.el-wrapper').length""")
        print(f"\nElements before paste: {before_count}")
        
        # Now simulate a paste event with image using ClipboardEvent
        print("\n--- Dispatching paste event with image to window ---")
        result = await page.evaluate("""async () => {
            const base64 = '""" + PNG_BASE64 + """';
            const byteStr = atob(base64);
            const bytes = new Uint8Array(byteStr.length);
            for (let i = 0; i < byteStr.length; i++) bytes[i] = byteStr.charCodeAt(i);
            const blob = new Blob([bytes], { type: 'image/png' });
            const file = new File([blob], 'screenshot.png', { type: 'image/png' });
            
            const dt = new DataTransfer();
            dt.items.add(file);
            
            const event = new ClipboardEvent('paste', {
                clipboardData: dt,
                bubbles: true,
                cancelable: true
            });
            
            // Check what activeElement is
            const ae = document.activeElement;
            const aeInfo = ae ? `${ae.tagName}.${ae.className?.slice(0,30)}` : 'none';
            
            // Check isInputFocused would return
            const tag = ae?.tagName?.toLowerCase();
            const isInput = tag === 'input' || tag === 'textarea' || tag === 'select' || ae?.isContentEditable;
            
            window.dispatchEvent(event);
            
            return { 
                activeElement: aeInfo,
                isInputFocused: isInput,
                eventDispatched: true
            };
        }""")
        print(f"Dispatch result: {result}")
        
        await asyncio.sleep(2)
        
        after_count = await page.evaluate("""() => document.querySelectorAll('.el-wrapper').length""")
        print(f"Elements after paste: {after_count}")
        
        if after_count > before_count:
            print(f"\n✅ SUCCESS! Image element added ({before_count} -> {after_count})")
        else:
            print(f"\n❌ FAILED: No element added ({before_count} -> {after_count})")
            
            # Check if there's an error - maybe onPaste listener isn't even attached
            # Let's check by looking at event listeners
            has_listener = await page.evaluate("""() => {
                // Try to get listeners - we can only check indirectly
                // by dispatching and seeing if our handler fires
                let fired = false;
                const handler = () => { fired = true; };
                // We can't introspect window event listeners directly
                // but we can check Vue app state
                const app = document.querySelector('#app').__vue_app__;
                return { 
                    vueAppExists: !!app,
                    editingTextId: window._editingTextId
                };
            }""")
            print(f"Debug info: {has_listener}")
        
        # Print console messages
        print("\n=== Console messages ===")
        for m in msgs:
            print(m)
        if errors:
            print("\n=== Page errors ===")
            for e in errors:
                print(e)
        
        # Test 2: Try Ctrl+V keyboard shortcut
        print("\n\n=== Test 2: Ctrl+V keyboard approach ===")
        
        # Click stage first
        await stage.click(position={"x": 400, "y": 200})
        await asyncio.sleep(0.3)
        
        before2 = await page.evaluate("""() => document.querySelectorAll('.el-wrapper').length""")
        
        # Write to actual clipboard first
        write_ok = await page.evaluate("""async () => {
            try {
                const base64 = '""" + PNG_BASE64 + """';
                const byteStr = atob(base64);
                const bytes = new Uint8Array(byteStr.length);
                for (let i = 0; i < byteStr.length; i++) bytes[i] = byteStr.charCodeAt(i);
                const blob = new Blob([bytes], { type: 'image/png' });
                await navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]);
                return true;
            } catch(e) { return e.message; }
        }""")
        print(f"clipboard.write: {write_ok}")
        
        # Press Ctrl+V
        await page.keyboard.press("Control+v")
        await asyncio.sleep(2)
        
        after2 = await page.evaluate("""() => document.querySelectorAll('.el-wrapper').length""")
        print(f"Elements {before2} -> {after2} after Ctrl+V")
        if after2 > before2:
            print("✅ Ctrl+V worked!")
        else:
            print("❌ Ctrl+V did not add element")
        
        await browser.close()

asyncio.run(main())
