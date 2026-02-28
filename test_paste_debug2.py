"""
Simulate real screenshot paste: paste event comes from OS clipboard
with image/png item, but active element is the browser window (not canvas).
Test exactly what happens step by step.
"""
import asyncio
import base64

# A proper 100x100 red PNG
import struct, zlib

def make_png(width=100, height=100, r=200, g=50, b=50):
    def chunk(name, data):
        c = zlib.crc32(name + data) & 0xffffffff
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', c)
    
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    raw = b''
    for _ in range(height):
        raw += b'\x00'  # filter type
        for _ in range(width):
            raw += bytes([r, g, b])
    
    compressed = zlib.compress(raw)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr_data)
    png += chunk(b'IDAT', compressed)
    png += chunk(b'IEND', b'')
    return png

PNG_BYTES = make_png()
PNG_BASE64 = base64.b64encode(PNG_BYTES).decode()

APP_URL = "https://3000-irwjpbeuyfymnkyphrwgp-2e77fc33.sandbox.novita.ai"

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
        print("App loaded\n")

        # ── Step 1: understand what activeElement is at page load ──────────
        initial = await page.evaluate("""() => ({
            activeEl: document.activeElement?.tagName,
            bodyClass: document.body.className,
        })""")
        print(f"Initial active element: {initial}")

        # ── Step 2: simulate EXACTLY what OS does when user presses Ctrl+V ──
        # The OS generates a 'paste' event on document/window with clipboardData.
        # The key question: does our listener receive it with a real image?
        print("\n--- Step 2: Raw paste event simulation (no focus change) ---")
        
        result = await page.evaluate(f"""async () => {{
            const logs = [];
            
            // Intercept the onPaste function to see what it receives
            const base64 = '{PNG_BASE64}';
            const byteStr = atob(base64);
            const bytes = new Uint8Array(byteStr.length);
            for (let i = 0; i < byteStr.length; i++) bytes[i] = byteStr.charCodeAt(i);
            const blob = new Blob([bytes], {{ type: 'image/png' }});
            const file = new File([blob], 'screenshot.png', {{ type: 'image/png' }});
            
            const dt = new DataTransfer();
            dt.items.add(file);
            
            logs.push('activeElement before: ' + document.activeElement?.tagName + '.' + (document.activeElement?.className||''));
            logs.push('clipboardData items: ' + dt.items.length);
            logs.push('item[0] type: ' + dt.items[0]?.type);
            logs.push('item[0] kind: ' + dt.items[0]?.kind);
            
            const event = new ClipboardEvent('paste', {{
                clipboardData: dt,
                bubbles: true,
                cancelable: true
            }});
            
            // Check if event.clipboardData.items is accessible
            logs.push('event.clipboardData: ' + !!event.clipboardData);
            logs.push('event.clipboardData.items: ' + (event.clipboardData?.items?.length ?? 'null'));
            
            // Try iterating items
            if (event.clipboardData?.items) {{
                for (let i = 0; i < event.clipboardData.items.length; i++) {{
                    const item = event.clipboardData.items[i];
                    logs.push('  item['+i+'] kind=' + item.kind + ' type=' + item.type);
                }}
            }}
            
            window.dispatchEvent(event);
            return logs;
        }}""")
        
        for line in result:
            print(f"  {line}")
        
        await asyncio.sleep(1.5)
        count1 = await page.evaluate("() => document.querySelectorAll('.el-wrapper').length")
        print(f"\nElements after: {count1}")
        
        # ── Step 3: Check if ClipboardEvent preserves items ───────────────
        print("\n--- Step 3: Check ClipboardEvent items preservation ---")
        check = await page.evaluate(f"""() => {{
            const base64 = '{PNG_BASE64}';
            const byteStr = atob(base64);
            const bytes = new Uint8Array(byteStr.length);
            for (let i = 0; i < byteStr.length; i++) bytes[i] = byteStr.charCodeAt(i);
            const blob = new Blob([bytes], {{ type: 'image/png' }});
            const file = new File([blob], 'test.png', {{ type: 'image/png' }});
            
            const dt = new DataTransfer();
            dt.items.add(file);
            
            // Check BEFORE creating event
            const beforeItems = dt.items.length;
            const beforeType = dt.items[0]?.type;
            
            const event = new ClipboardEvent('paste', {{
                clipboardData: dt,
                bubbles: true,
                cancelable: true
            }});
            
            // Check AFTER creating event - does clipboardData preserve items?
            const afterItems = event.clipboardData?.items?.length;
            const afterType = event.clipboardData?.items?.[0]?.type;
            
            // The crucial test: can we getAsFile() from the event?
            const file2 = event.clipboardData?.items?.[0]?.getAsFile?.();
            
            return {{
                dt_items_before: beforeItems,
                dt_type_before: beforeType,
                event_items_after: afterItems,
                event_type_after: afterType,
                can_getAsFile: !!file2,
                file_size: file2?.size || 0,
            }};
        }}""")
        print(f"  {check}")
        
        # ── Critical check: does ClipboardEvent nullify items? ────────────
        if check.get('event_items_after') == 0 or check.get('can_getAsFile') == False:
            print("\n🔴 FOUND THE BUG: ClipboardEvent constructor LOSES the DataTransfer items!")
            print("   items.length becomes 0 or getAsFile() returns null after ClipboardEvent creation")
        else:
            print("\n✅ ClipboardEvent preserves DataTransfer items correctly")
        
        # ── Step 4: Use InputEvent approach instead ────────────────────────
        print("\n--- Step 4: Test alternative - manually set clipboard then trigger paste ---")
        count_before = await page.evaluate("() => document.querySelectorAll('.el-wrapper').length")
        
        alt_result = await page.evaluate(f"""async () => {{
            // Instead of ClipboardEvent, manually intercept clipboard API
            const base64 = '{PNG_BASE64}';
            const byteStr = atob(base64);
            const bytes = new Uint8Array(byteStr.length);
            for (let i = 0; i < byteStr.length; i++) bytes[i] = byteStr.charCodeAt(i);
            const blob = new Blob([bytes], {{ type: 'image/png' }});
            
            // Monkey-patch navigator.clipboard.read to return our image
            const origRead = navigator.clipboard.read.bind(navigator.clipboard);
            navigator.clipboard.read = async () => {{
                const item = new ClipboardItem({{ 'image/png': blob }});
                return [item];
            }};
            
            // Now trigger Ctrl+V keydown (which calls pasteFromSystemClipboard)
            const keyEvent = new KeyboardEvent('keydown', {{
                key: 'v',
                ctrlKey: true,
                metaKey: false,
                bubbles: true,
                cancelable: true
            }});
            window.dispatchEvent(keyEvent);
            
            // Restore
            await new Promise(r => setTimeout(r, 500));
            navigator.clipboard.read = origRead;
            
            return {{ ok: true }};
        }}""")
        print(f"  Alt result: {alt_result}")
        
        await asyncio.sleep(2)
        count_after = await page.evaluate("() => document.querySelectorAll('.el-wrapper').length")
        print(f"  Elements: {count_before} -> {count_after}")
        
        if count_after > count_before:
            print("  ✅ Alternative approach (navigator.clipboard.read patch) WORKS!")
        else:
            print("  ❌ Alternative approach also failed")
        
        print("\n=== All console messages ===")
        for m in msgs:
            print(f"  {m}")
        
        await browser.close()

asyncio.run(main())
