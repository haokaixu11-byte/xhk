#!/usr/bin/env python3
"""
Comprehensive component interaction test for ProtoFlow
Tests all 11 component types and key interactions
"""
from playwright.sync_api import sync_playwright
import time

BASE = "https://3000-irwjpbeuyfymnkyphrwgp-2e77fc33.sandbox.novita.ai"
PASS = "✅"
FAIL = "❌"
results = []

def check(desc, condition):
    icon = PASS if condition else FAIL
    results.append((icon, desc, condition))
    print(f"  {icon} {desc}")

def run_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1400, "height": 900})
        page = ctx.new_page()
        js_errors = []
        page.on("console", lambda m: js_errors.append(m.text()) if m.type == "error" else None)

        print("\n🔄 Loading ProtoFlow editor...")
        page.goto(BASE, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)

        check("Page title is correct", page.title() == "ProtoFlow - 高保真原型设计工具")
        check("Editor layout loaded", page.locator(".editor-layout").is_visible())
        check("Left panel visible", page.locator(".left-panel").is_visible())
        check("Right panel visible", page.locator(".right-panel").is_visible())
        check("Canvas stage visible", page.locator(".canvas-stage").is_visible())
        check("Page canvas visible", page.locator(".page-canvas").is_visible())

        print("\n🧩 Testing component panel...")
        comp_items = page.locator(".comp-item")
        comp_count = comp_items.count()
        check("Component items visible (>=11)", comp_count >= 11)
        names = [comp_items.nth(i).locator("span").inner_text() for i in range(comp_count)]
        print(f"    Components found: {', '.join(names)}")

        print("\n🎨 Testing adding each component type...")
        for i in range(comp_count):
            item = comp_items.nth(i)
            name = item.locator("span").inner_text()
            before = page.locator(".el-wrapper").count()
            item.click()
            page.wait_for_timeout(300)
            after = page.locator(".el-wrapper").count()
            check(f"Add {name}: element count increased", after == before + 1)
            # Click canvas background to deselect
            page.mouse.click(1000, 700)
            page.wait_for_timeout(200)

        total_elements = page.locator(".el-wrapper").count()
        print(f"\n    Total elements on canvas: {total_elements}")

        print("\n✏️  Testing right panel interactions (Backspace/Delete should NOT delete elements)...")
        # Select first element
        first_el = page.locator(".el-wrapper").first()
        first_el.click()
        page.wait_for_timeout(300)
        check("Selecting element shows type badge", page.locator(".el-type-badge").is_visible())
        check("Selecting element shows properties", page.locator(".props-content").is_visible())

        # Type in element name input - Backspace should NOT delete element
        name_input = page.locator(".el-name-input")
        name_input.click()
        page.wait_for_timeout(100)
        name_input.fill("Test Element Name")
        for _ in range(5):
            page.keyboard.press("Backspace")
        page.wait_for_timeout(300)
        el_after_name_bs = page.locator(".el-wrapper").count()
        check(f"Backspace in name input: element count unchanged ({el_after_name_bs}/{total_elements})", 
              el_after_name_bs == total_elements)

        # Type in X position input - Backspace should NOT delete element
        num_inputs = page.locator(".num-input")
        if num_inputs.count() > 0:
            num_inputs.first().click()
            page.wait_for_timeout(100)
            num_inputs.first().fill("150")
            page.keyboard.press("Backspace")
            page.wait_for_timeout(300)
            el_after_num_bs = page.locator(".el-wrapper").count()
            check(f"Backspace in num input: element count unchanged ({el_after_num_bs}/{total_elements})",
                  el_after_num_bs == total_elements)

        # Type in text area (right panel)
        text_areas = page.locator(".text-area")
        if text_areas.count() > 0:
            text_areas.first().click()
            page.wait_for_timeout(100)
            text_areas.first().fill("Hello World")
            page.keyboard.press("Backspace")
            page.wait_for_timeout(300)
            el_after_ta_bs = page.locator(".el-wrapper").count()
            check(f"Backspace in text area: element count unchanged ({el_after_ta_bs}/{total_elements})",
                  el_after_ta_bs == total_elements)

        print("\n🗑️  Testing Delete key on canvas properly deletes element...")
        # Click canvas background to lose focus from inputs
        page.mouse.click(1050, 750)
        page.wait_for_timeout(300)
        # Click an element on canvas to select it
        canvas_el = page.locator(".el-wrapper").first()
        canvas_el.click()
        page.wait_for_timeout(300)
        before_del = page.locator(".el-wrapper").count()
        page.keyboard.press("Delete")
        page.wait_for_timeout(300)
        after_del = page.locator(".el-wrapper").count()
        check(f"Delete key on canvas deletes selected element ({before_del} -> {after_del})",
              after_del == before_del - 1)

        print("\n📋 Testing layer panel...")
        page.locator(".panel-tabs button").nth(1).click()
        page.wait_for_timeout(300)
        layer_items = page.locator(".layer-item")
        layer_count = layer_items.count()
        check(f"Layer panel shows elements ({layer_count} layers)", layer_count > 0)

        print("\n📄 Testing page management...")
        page.locator(".panel-tabs button").nth(2).click()
        page.wait_for_timeout(300)
        add_page_btn = page.locator(".add-page-btn")
        check("Add page button visible", add_page_btn.is_visible())
        add_page_btn.click()
        page.wait_for_timeout(300)
        page_items = page.locator(".page-item")
        check("New page created (2 pages total)", page_items.count() == 2)
        # Switch back to first page
        page_items.first().click()
        page.wait_for_timeout(300)

        print("\n🔗 Testing share link generation...")
        share_btn = page.locator(".share-btn")
        check("Share button visible", share_btn.is_visible())
        share_btn.click()
        page.wait_for_timeout(500)
        check("Share modal opened", page.locator(".modal").is_visible())
        gen_btn = page.locator(".generate-btn")
        check("Generate link button visible", gen_btn.is_visible())
        gen_btn.click()
        page.wait_for_timeout(500)
        check("Share link generated (link-input visible)", page.locator(".link-input").is_visible())
        link_val = page.locator(".link-input").input_value()
        check(f"Share link contains /preview/", "/preview/" in link_val)
        print(f"    Generated link: {link_val}")
        # Close modal
        page.locator(".modal-close").click()
        page.wait_for_timeout(300)

        print("\n👁️  Testing preview mode...")
        preview_btn = page.locator(".preview-btn")
        check("Preview button visible", preview_btn.is_visible())

        print("\n↩️  Testing undo/redo...")
        # Add an element
        page.locator(".panel-tabs button").first().click()
        page.wait_for_timeout(200)
        page.locator(".comp-item").first().click()
        page.wait_for_timeout(300)
        before_undo = page.locator(".el-wrapper").count()
        # Undo
        page.keyboard.press("Control+z")
        page.wait_for_timeout(300)
        after_undo = page.locator(".el-wrapper").count()
        check(f"Ctrl+Z undo works ({before_undo} -> {after_undo})", after_undo == before_undo - 1)
        # Redo
        page.keyboard.press("Control+y")
        page.wait_for_timeout(300)
        after_redo = page.locator(".el-wrapper").count()
        check(f"Ctrl+Y redo works ({after_undo} -> {after_redo})", after_redo == after_undo + 1)

        print("\n🖱️  Testing element drag (position change)...")
        page.mouse.click(1050, 750)  # deselect
        page.wait_for_timeout(200)
        first_el = page.locator(".el-wrapper").first()
        box = first_el.bounding_box()
        if box:
            cx = box['x'] + box['width']/2
            cy = box['y'] + box['height']/2
            first_el.click()
            page.wait_for_timeout(200)
            # Get position before drag
            x_before = page.locator(".num-input").nth(0).input_value()
            # Drag
            page.mouse.move(cx, cy)
            page.mouse.down()
            page.mouse.move(cx + 60, cy + 40, steps=10)
            page.mouse.up()
            page.wait_for_timeout(300)
            x_after = page.locator(".num-input").nth(0).input_value()
            check(f"Drag moves element (X: {x_before} -> {x_after})", x_before != x_after)

        print("\n🔍 Checking for JS console errors...")
        check(f"No JS console errors ({len(js_errors)} errors)", len(js_errors) == 0)
        if js_errors:
            for err in js_errors[:5]:
                print(f"    Error: {err}")

        browser.close()

    print("\n" + "="*60)
    passed = sum(1 for r in results if r[2])
    failed = sum(1 for r in results if not r[2])
    total = len(results)
    print(f"📊 TEST RESULTS: {passed}/{total} passed, {failed} failed")
    print("="*60)

    if failed > 0:
        print("\n❌ Failed tests:")
        for icon, desc, ok in results:
            if not ok:
                print(f"  • {desc}")

if __name__ == "__main__":
    run_tests()
