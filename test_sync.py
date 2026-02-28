"""
双向同步测试：画布组件内容 <-> 右侧元素名称框
"""
import sys
import time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:3000"

def log(msg, ok=True):
    prefix = "✅" if ok else "❌"
    print(f"{prefix} {msg}")

def fail(msg):
    log(msg, ok=False)
    sys.exit(1)

def get_content_input(page, el_type):
    """根据组件类型获取右侧"内容"输入框"""
    if el_type == "text":
        return page.locator(".text-area").first
    else:
        # button/navbar: 找包含 label"内容"的 prop-row 里的 input
        # 定位：文字区域 section 里，label=内容 的那一行的 input
        rows = page.locator(".section .prop-row")
        count = rows.count()
        for i in range(count):
            row = rows.nth(i)
            label_text = row.locator("label").first.inner_text()
            if label_text.strip() == "内容":
                inp = row.locator("input.text-input").first
                return inp
        return None

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(BASE, timeout=30000)
        page.wait_for_selector(".canvas-stage", timeout=15000)
        time.sleep(1.5)
        log("页面加载成功")

        # ── 测试1：文本组件初始状态 ────────────────────────────────────
        print("\n── 测试1：文本组件初始状态 ──")

        text_btn = page.locator(".comp-item", has_text="文本").first
        text_btn.click()
        time.sleep(0.8)
        log("添加文本组件")

        name_input = page.locator(".el-name-input").first
        initial_name = name_input.input_value()
        print(f"  初始名称框值: '{initial_name}'")
        if initial_name != "双击编辑文本":
            fail(f"名称框初始值错误，期望'双击编辑文本'，实际: '{initial_name}'")
        log("初始名称框正确显示 text 默认值 ✓")

        # ── 测试2：右侧名称框输入 → 内容区域 + 画布同步 ──────────────
        print("\n── 测试2：右侧名称框输入 → 内容区域 + 画布同步 ──")

        name_input.fill("你好世界")
        time.sleep(0.3)

        # 右侧内容 textarea
        text_area = page.locator(".text-area").first
        panel_text = text_area.input_value()
        print(f"  右侧内容textarea值: '{panel_text}'")
        if panel_text != "你好世界":
            fail(f"内容区域未跟随名称框同步，实际: '{panel_text}'")
        log("名称框输入 → 右侧内容textarea实时同步 ✓")

        # 画布文本显示
        display = page.locator(".el-text-display").first
        canvas_html = display.inner_html()
        print(f"  画布文本HTML: '{canvas_html}'")
        if "你好世界" not in canvas_html:
            fail(f"画布文本未同步，实际: '{canvas_html}'")
        log("名称框输入 → 画布文本同步 ✓")

        # ── 测试3：双击画布编辑 → 名称框实时更新 ────────────────────
        print("\n── 测试3：双击画布编辑 → 名称框实时更新 ──")

        el_wrapper = page.locator(".el-wrapper").first
        el_wrapper.dblclick()
        time.sleep(0.5)

        canvas_ta = page.locator(".el-textarea").first
        canvas_ta.wait_for(state="visible", timeout=3000)
        log("进入画布编辑模式")

        canvas_ta.fill("实时同步测试")
        time.sleep(0.3)

        name_val = page.locator(".el-name-input").first.input_value()
        print(f"  画布输入后，名称框值: '{name_val}'")
        if name_val != "实时同步测试":
            fail(f"画布输入时名称框未实时同步，实际: '{name_val}'")
        log("画布输入 → 名称框实时同步 ✓")

        panel_text2 = page.locator(".text-area").first.input_value()
        print(f"  画布输入后，内容textarea: '{panel_text2}'")
        if panel_text2 != "实时同步测试":
            fail(f"画布输入时内容区域未同步，实际: '{panel_text2}'")
        log("画布输入 → 右侧内容区域实时同步 ✓")

        # 点击空白区域退出编辑
        page.locator(".page-canvas").first.click(position={"x": 5, "y": 5})
        time.sleep(0.5)

        # 重新选中，验证保存后名称仍正确
        el_wrapper.click()
        time.sleep(0.3)
        name_after = page.locator(".el-name-input").first.input_value()
        print(f"  退出编辑后名称框值: '{name_after}'")
        if name_after != "实时同步测试":
            fail(f"退出编辑后名称框值不对，实际: '{name_after}'")
        log("退出编辑后名称框保持正确值 ✓")

        # ── 测试4：按钮组件初始状态 + 名称→画布 ─────────────────────
        print("\n── 测试4：按钮组件双向同步 ──")

        page.keyboard.press("Escape")
        time.sleep(0.3)

        btn_comp = page.locator(".comp-item", has_text="按钮").first
        btn_comp.click()
        time.sleep(0.8)
        log("添加按钮组件")

        name2 = page.locator(".el-name-input").first.input_value()
        print(f"  按钮初始名称框: '{name2}'")
        if name2 != "按钮":
            fail(f"按钮名称框初始值错误，实际: '{name2}'")
        log("按钮名称框初始值正确 ✓")

        # 修改名称框
        page.locator(".el-name-input").first.fill("提交")
        time.sleep(0.3)

        # 画布按钮标签同步
        btn_label = page.locator(".el-button-label").first
        btn_text = btn_label.inner_text()
        print(f"  画布按钮文字: '{btn_text}'")
        if btn_text != "提交":
            fail(f"按钮画布文字未同步，实际: '{btn_text}'")
        log("名称框输入 → 按钮画布实时同步 ✓")

        # ── 测试5：右侧"内容"输入框修改 → 名称框同步 ─────────────────
        print("\n── 测试5：右侧内容区域修改 → 名称框同步 ──")

        content_inp = get_content_input(page, "button")
        if content_inp is None:
            fail("找不到右侧按钮内容输入框")

        content_inp.fill("确认提交")
        time.sleep(0.3)

        name3 = page.locator(".el-name-input").first.input_value()
        print(f"  内容修改后名称框: '{name3}'")
        if name3 != "确认提交":
            fail(f"内容区域修改后名称框未同步，实际: '{name3}'")
        log("右侧内容区域 → 名称框实时同步 ✓")

        # 画布同步
        btn_text2 = page.locator(".el-button-label").first.inner_text()
        print(f"  内容修改后画布按钮: '{btn_text2}'")
        if btn_text2 != "确认提交":
            fail(f"内容修改后画布按钮未同步，实际: '{btn_text2}'")
        log("右侧内容区域 → 画布按钮实时同步 ✓")

        # ── 测试6：双击画布按钮编辑 → 名称框同步 ─────────────────────
        print("\n── 测试6：双击画布按钮编辑 → 名称框同步 ──")

        btn_wrapper = page.locator(".el-wrapper").last
        btn_wrapper.dblclick()
        time.sleep(0.5)

        btn_ta = page.locator(".el-textarea-inline").first
        btn_ta.wait_for(state="visible", timeout=3000)
        log("进入按钮编辑模式")

        btn_ta.fill("立即购买")
        time.sleep(0.3)

        name4 = page.locator(".el-name-input").first.input_value()
        print(f"  按钮画布输入后名称框: '{name4}'")
        if name4 != "立即购买":
            fail(f"按钮画布输入时名称框未同步，实际: '{name4}'")
        log("按钮画布输入 → 名称框实时同步 ✓")

        # 退出并验证
        page.locator(".page-canvas").first.click(position={"x": 5, "y": 5})
        time.sleep(0.5)
        btn_wrapper.click()
        time.sleep(0.3)
        final_name = page.locator(".el-name-input").first.input_value()
        print(f"  按钮编辑结束后名称框: '{final_name}'")
        if final_name != "立即购买":
            fail(f"按钮编辑结束后名称框值不对，实际: '{final_name}'")
        log("按钮编辑结束后名称框保持正确 ✓")

        print("\n" + "="*58)
        print("🎉 全部 6 组测试通过！双向同步工作完全正常！")
        print("="*58)
        browser.close()

if __name__ == "__main__":
    run()
