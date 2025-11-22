// #include <windows.h>
// #include <string>
// #include <vector>

// #pragma comment(lib, "user32.lib")

// // 控件 ID
// #define ID_EDIT_COUNT   1001
// #define ID_BUTTON_START 1002

// // 自定义消息：线程完成时发给主窗口
// #define WM_USER_THREAD_MSG (WM_USER + 1)

// // 全局变量（简单粗暴但好理解）
// HWND g_hMainWnd = nullptr;
// HWND g_hEditCount = nullptr;
// HWND g_hOutput = nullptr;
// std::vector<int>    g_threadIndex;   // 保存线程编号
// std::vector<HANDLE> g_threadHandles; // 保存线程句柄，防止被系统回收

// // 在线程中执行的任务函数
// DWORD WINAPI ThreadFunc(LPVOID lpParam) {
//     int index = *reinterpret_cast<int*>(lpParam); // 线程编号（1~N）
//     DWORD tid = GetCurrentThreadId();             // 系统线程 ID

//     // 把结果发给主窗口，由主线程更新界面
//     PostMessage(g_hMainWnd, WM_USER_THREAD_MSG, (WPARAM)index, (LPARAM)tid);

//     // 模拟一点点工作量
//     Sleep(100);

//     return 0;
// }

// // 向多行编辑框追加一行文本
// void AppendTextToOutput(const std::string& text) {
//     int len = GetWindowTextLengthA(g_hOutput);
//     // 光标移到最后
//     SendMessageA(g_hOutput, EM_SETSEL, (WPARAM)len, (LPARAM)len);
//     // 在光标处插入文本
//     SendMessageA(g_hOutput, EM_REPLACESEL, FALSE, (LPARAM)text.c_str());
// }

// // 窗口过程
// LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
//     switch (msg) {
//     case WM_CREATE: {
//         // 创建控件：标签、输入框、按钮、输出框
//         CreateWindowExA(
//             0, "STATIC", "Thread Count:",
//             WS_CHILD | WS_VISIBLE,
//             20, 20, 90, 25,
//             hwnd, nullptr, GetModuleHandle(nullptr), nullptr
//         );

//         g_hEditCount = CreateWindowExA(
//             WS_EX_CLIENTEDGE, "EDIT", "5",
//             WS_CHILD | WS_VISIBLE | ES_NUMBER | ES_LEFT,
//             120, 20, 80, 25,
//             hwnd, (HMENU)ID_EDIT_COUNT, GetModuleHandle(nullptr), nullptr
//         );

//         CreateWindowExA(
//             0, "BUTTON", "Create Threads",
//             WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
//             220, 20, 120, 25,
//             hwnd, (HMENU)ID_BUTTON_START, GetModuleHandle(nullptr), nullptr
//         );

//         g_hOutput = CreateWindowExA(
//             WS_EX_CLIENTEDGE, "EDIT", "",
//             WS_CHILD | WS_VISIBLE | WS_VSCROLL |
//             ES_MULTILINE | ES_AUTOVSCROLL | ES_READONLY,
//             20, 60, 460, 260,
//             hwnd, nullptr, GetModuleHandle(nullptr), nullptr
//         );
//         break;
//     }
//     case WM_COMMAND: {
//         if (LOWORD(wParam) == ID_BUTTON_START && HIWORD(wParam) == BN_CLICKED) {
//             // 点击按钮：读取线程数量
//             char buf[32] = { 0 };
//             GetWindowTextA(g_hEditCount, buf, sizeof(buf));
//             int threadCount = 0;
//             try {
//                 threadCount = std::stoi(buf);
//             } catch (...) {
//                 MessageBoxA(hwnd, "Please input a valid positive integer.", "Error", MB_ICONERROR);
//                 break;
//             }

//             if (threadCount <= 0) {
//                 MessageBoxA(hwnd, "Thread count must be > 0.", "Error", MB_ICONERROR);
//                 break;
//             }

//             // 清理旧线程（简单起见：等待并关闭）
//             for (HANDLE h : g_threadHandles) {
//                 if (h) {
//                     WaitForSingleObject(h, INFINITE);
//                     CloseHandle(h);
//                 }
//             }
//             g_threadHandles.clear();
//             g_threadIndex.clear();

//             // 清空输出框
//             SetWindowTextA(g_hOutput, "");

//             g_threadIndex.resize(threadCount);
//             g_threadHandles.resize(threadCount);

//             for (int i = 0; i < threadCount; ++i) {
//                 g_threadIndex[i] = i + 1;
//                 DWORD tid = 0;
//                 HANDLE hThread = CreateThread(
//                     nullptr,
//                     0,
//                     ThreadFunc,
//                     &g_threadIndex[i],
//                     0,
//                     &tid
//                 );

//                 if (!hThread) {
//                     std::string err = "Failed to create thread " + std::to_string(i + 1) +
//                                       ", error = " + std::to_string(GetLastError()) + "\r\n";
//                     AppendTextToOutput(err);
//                 } else {
//                     g_threadHandles[i] = hThread;
//                 }
//             }

//             break;
//         }
//         break;
//     }
//     case WM_USER_THREAD_MSG: {
//         int index = (int)wParam;
//         DWORD tid = (DWORD)lParam;
//         std::string line = "Thread #" + std::to_string(index) +
//                            ", System Thread ID = " + std::to_string((unsigned long)tid) + "\r\n";
//         AppendTextToOutput(line);
//         break;
//     }
//     case WM_DESTROY: {
//         // 退出前等待并关闭所有线程
//         for (HANDLE h : g_threadHandles) {
//             if (h) {
//                 WaitForSingleObject(h, INFINITE);
//                 CloseHandle(h);
//             }
//         }
//         g_threadHandles.clear();
//         g_threadIndex.clear();

//         PostQuitMessage(0);
//         break;
//     }
//     default:
//         return DefWindowProcA(hwnd, msg, wParam, lParam);
//     }
//     return 0;
// }

// // Win32 GUI 程序入口
// int APIENTRY WinMain(HINSTANCE hInstance,
//                      HINSTANCE hPrevInstance,
//                      LPSTR     lpCmdLine,
//                      int       nCmdShow) {
//     // 注册窗口类
//     WNDCLASSEXA wcex = { 0 };
//     wcex.cbSize = sizeof(WNDCLASSEXA);
//     wcex.style = CS_HREDRAW | CS_VREDRAW;
//     wcex.lpfnWndProc = WndProc;
//     wcex.hInstance = hInstance;
//     wcex.hIcon = LoadIcon(nullptr, IDI_APPLICATION);
//     wcex.hCursor = LoadCursor(nullptr, IDC_ARROW);
//     wcex.hbrBackground = (HBRUSH)(COLOR_WINDOW + 1);
//     wcex.lpszClassName = "ThreadDemoWindowClass";
//     wcex.hIconSm = LoadIcon(nullptr, IDI_APPLICATION);

//     if (!RegisterClassExA(&wcex)) {
//         MessageBoxA(nullptr, "RegisterClassEx failed!", "Error", MB_ICONERROR);
//         return 1;
//     }

//     // 创建主窗口
//     HWND hwnd = CreateWindowExA(
//         0,
//         "ThreadDemoWindowClass",
//         "Win32 Multi-Thread Demo",
//         WS_OVERLAPPEDWINDOW ^ WS_MAXIMIZEBOX ^ WS_THICKFRAME, // 禁止最大化和改变大小，可按需修改
//         CW_USEDEFAULT, 0, 520, 380,
//         nullptr, nullptr, hInstance, nullptr
//     );

//     if (!hwnd) {
//         MessageBoxA(nullptr, "CreateWindowEx failed!", "Error", MB_ICONERROR);
//         return 1;
//     }

//     g_hMainWnd = hwnd;

//     ShowWindow(hwnd, nCmdShow);
//     UpdateWindow(hwnd);

//     // 消息循环
//     MSG msg;
//     while (GetMessageA(&msg, nullptr, 0, 0)) {
//         TranslateMessage(&msg);
//         DispatchMessageA(&msg);
//     }

//     return (int)msg.wParam;
// }


#include <windows.h>
#include <string>
#include <vector>

#pragma comment(lib, "Msimg32.lib") // 用于 GradientFill

// ==================== 主题配色（来自 Python theme.py） ====================
// 参考：BG_GRADIENT_TOP = (28, 34, 52), BG_GRADIENT_BOTTOM = (10, 13, 24)
//       ACCENT = (94, 155, 255), TEXT_MAIN = (248, 251, 255) 等
// ========================================================================
const COLORREF BG_TOP        = RGB(28, 34, 52);
const COLORREF BG_BOTTOM     = RGB(10, 13, 24);
const COLORREF PANEL_COLOR   = RGB(44, 52, 70);
const COLORREF EDIT_BG       = RGB(60, 66, 76);
const COLORREF ACCENT        = RGB(94, 155, 255);
const COLORREF ACCENT_DARK   = RGB(64, 115, 210);
const COLORREF TEXT_MAIN     = RGB(248, 251, 255);
const COLORREF TEXT_DIM      = RGB(210, 216, 228);

// 控件 ID
#define ID_EDIT_COUNT   1001
#define ID_BUTTON_START 1002

// 自定义消息：线程完成时发给主窗口
#define WM_USER_THREAD_MSG (WM_USER + 1)

// 全局变量
HWND g_hMainWnd   = nullptr;
HWND g_hEditCount = nullptr;
HWND g_hOutput    = nullptr;

// GDI 资源
HFONT  g_hFontTitle  = nullptr;
HFONT  g_hFontNormal = nullptr;
HBRUSH g_hPanelBrush = nullptr;
HBRUSH g_hEditBrush  = nullptr;

// 线程数据
std::vector<int>    g_threadIndex;
std::vector<HANDLE> g_threadHandles;

// ============ 工具函数：画竖直渐变背景 ============

void DrawVerticalGradient(HDC hdc, const RECT& rc, COLORREF top, COLORREF bottom)
{
    TRIVERTEX vert[2];
    GRADIENT_RECT gRect;

    vert[0].x     = rc.left;
    vert[0].y     = rc.top;
    vert[0].Red   = GetRValue(top)   << 8;
    vert[0].Green = GetGValue(top)   << 8;
    vert[0].Blue  = GetBValue(top)   << 8;
    vert[0].Alpha = 0xFF00;

    vert[1].x     = rc.right;
    vert[1].y     = rc.bottom;
    vert[1].Red   = GetRValue(bottom) << 8;
    vert[1].Green = GetGValue(bottom) << 8;
    vert[1].Blue  = GetBValue(bottom) << 8;
    vert[1].Alpha = 0xFF00;

    gRect.UpperLeft  = 0;
    gRect.LowerRight = 1;

    GradientFill(hdc, vert, 2, &gRect, 1, GRADIENT_FILL_RECT_V);
}

// ============ 工具函数：画圆角矩形面板 ============

void DrawRoundPanel(HDC hdc, const RECT& rc, COLORREF color, int radius = 18)
{
    HBRUSH hBrush = CreateSolidBrush(color);
    HBRUSH hOld   = (HBRUSH)SelectObject(hdc, hBrush);
    HPEN   hPen   = CreatePen(PS_SOLID, 1, RGB(0, 0, 0));
    HPEN   hOldPen = (HPEN)SelectObject(hdc, hPen);

    RoundRect(hdc, rc.left, rc.top, rc.right, rc.bottom, radius, radius);

    SelectObject(hdc, hOldPen);
    DeleteObject(hPen);
    SelectObject(hdc, hOld);
    DeleteObject(hBrush);
}

// ===================== 线程函数 =====================

DWORD WINAPI ThreadFunc(LPVOID lpParam)
{
    int index = *reinterpret_cast<int*>(lpParam);
    DWORD tid = GetCurrentThreadId();

    // 把结果发给主窗口，由主线程更新界面
    PostMessage(g_hMainWnd, WM_USER_THREAD_MSG, (WPARAM)index, (LPARAM)tid);

    Sleep(100); // 模拟一点点工作

    return 0;
}

// 向多行编辑框尾部追加文本
void AppendTextToOutput(const std::string& text)
{
    if (!g_hOutput) return;
    int len = GetWindowTextLengthA(g_hOutput);
    SendMessageA(g_hOutput, EM_SETSEL, (WPARAM)len, (LPARAM)len);
    SendMessageA(g_hOutput, EM_REPLACESEL, FALSE, (LPARAM)text.c_str());
}

// ===================== 窗口过程 =====================

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    switch (msg)
    {
    case WM_CREATE:
    {
        // 创建字体（优先中文 UI 字体）
        g_hFontTitle = CreateFontW(
            32, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_OUTLINE_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, VARIABLE_PITCH, L"Microsoft YaHei UI");
        g_hFontNormal = CreateFontW(
            18, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_OUTLINE_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, VARIABLE_PITCH, L"Microsoft YaHei UI");

        g_hPanelBrush = CreateSolidBrush(PANEL_COLOR);
        g_hEditBrush  = CreateSolidBrush(EDIT_BG);

        // 创建控件
        // 主面板区域：类似你 Pygame 登录面板居中布局
        int winW = 900;
        int winH = 540;

        // 标题
        HWND hTitle = CreateWindowExW(
            0, L"STATIC", L"C++ 多线程演示",
            WS_CHILD | WS_VISIBLE,
            0, 0, 0, 0,   // 位置在 WM_SIZE 里调整
            hwnd, (HMENU)0, GetModuleHandle(nullptr), nullptr);
        SendMessageW(hTitle, WM_SETFONT, (WPARAM)g_hFontTitle, TRUE);

        // “线程数量”标签
        HWND hLabel = CreateWindowExW(
            0, L"STATIC", L"线程数量：",
            WS_CHILD | WS_VISIBLE,
            0, 0, 0, 0,
            hwnd, (HMENU)0, GetModuleHandle(nullptr), nullptr);
        SendMessageW(hLabel, WM_SETFONT, (WPARAM)g_hFontNormal, TRUE);

        // 线程数量输入框
        g_hEditCount = CreateWindowExW(
            WS_EX_CLIENTEDGE, L"EDIT", L"8",
            WS_CHILD | WS_VISIBLE | ES_NUMBER | ES_LEFT,
            0, 0, 0, 0,
            hwnd, (HMENU)ID_EDIT_COUNT, GetModuleHandle(nullptr), nullptr);
        SendMessageW(g_hEditCount, WM_SETFONT, (WPARAM)g_hFontNormal, TRUE);

        // “创建线程”按钮
        HWND hBtn = CreateWindowExW(
            0, L"BUTTON", L"创建线程",
            WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
            0, 0, 0, 0,
            hwnd, (HMENU)ID_BUTTON_START, GetModuleHandle(nullptr), nullptr);
        SendMessageW(hBtn, WM_SETFONT, (WPARAM)g_hFontNormal, TRUE);

        // 输出框（多行、只读）
        g_hOutput = CreateWindowExW(
            WS_EX_CLIENTEDGE, L"EDIT", L"",
            WS_CHILD | WS_VISIBLE | WS_VSCROLL |
            ES_MULTILINE | ES_AUTOVSCROLL | ES_READONLY,
            0, 0, 0, 0,
            hwnd, nullptr, GetModuleHandle(nullptr), nullptr);
        SendMessageW(g_hOutput, WM_SETFONT, (WPARAM)g_hFontNormal, TRUE);

        break;
    }
    case WM_SIZE:
    {
        // 根据窗口大小重新布局控件（自适应居中）
        int w = LOWORD(lParam);
        int h = HIWORD(lParam);
        if (w == 0 || h == 0) break;

        int panelW = 760;
        int panelH = 360;
        int panelX = (w - panelW) / 2;
        int panelY = (h - panelH) / 2;

        // 标题放在面板上方一点
        HWND hTitle = FindWindowExW(hwnd, nullptr, L"Static", L"C++ 多线程演示");
        if (hTitle)
        {
            int titleW = 400;
            int titleH = 40;
            int titleX = (w - titleW) / 2;
            int titleY = panelY - 60;
            SetWindowPos(hTitle, nullptr, titleX, titleY, titleW, titleH, SWP_NOZORDER);
        }

        // “线程数量：” + 输入框 + 按钮 一行
        int labelW = 110;
        int labelH = 30;
        int editW  = 120;
        int editH  = 30;
        int btnW   = 120;
        int btnH   = 32;
        int gap    = 16;
        int rowY   = panelY + 30;

        HWND hLabel = nullptr;
        // 用 FindWindowEx 不太安全，这里用枚举 ID 的方式更好：
        // 但我们没有给 label 设置 ID，这里简单一点：从第一个 Static 开始找不是标题的那个。
        HWND hChild = nullptr;
        int staticCount = 0;
        while ((hChild = FindWindowExW(hwnd, hChild, L"Static", nullptr)) != nullptr)
        {
            staticCount++;
            if (staticCount == 2) // 第二个 Static 认为就是“线程数量：”
            {
                hLabel = hChild;
                break;
            }
        }

        int totalW = labelW + gap + editW + gap + btnW;
        int startX = (w - totalW) / 2;

        if (hLabel && g_hEditCount)
        {
            SetWindowPos(hLabel, nullptr, startX, rowY, labelW, labelH, SWP_NOZORDER);
            SetWindowPos(g_hEditCount, nullptr, startX + labelW + gap, rowY - 2, editW, editH + 4, SWP_NOZORDER);
        }
        HWND hBtn = GetDlgItem(hwnd, ID_BUTTON_START);
        if (hBtn)
        {
            SetWindowPos(hBtn, nullptr,
                         startX + labelW + gap + editW + gap, rowY - 2,
                         btnW, btnH + 4, SWP_NOZORDER);
        }

        // 输出框占据面板下方大部分区域
        int outX = panelX + 30;
        int outY = panelY + 90;
        int outW = panelW - 60;
        int outH = panelH - 120;
        if (g_hOutput)
        {
            SetWindowPos(g_hOutput, nullptr, outX, outY, outW, outH, SWP_NOZORDER);
        }

        InvalidateRect(hwnd, nullptr, TRUE);
        break;
    }
    case WM_COMMAND:
    {
        if (LOWORD(wParam) == ID_BUTTON_START && HIWORD(wParam) == BN_CLICKED)
        {
            // 读取线程数量
            wchar_t buf[32] = { 0 };
            GetWindowTextW(g_hEditCount, buf, 32);
            int threadCount = 0;
            try
            {
                threadCount = std::stoi(std::wstring(buf));
            }
            catch (...)
            {
                MessageBoxW(hwnd, L"请输入有效的正整数。", L"错误", MB_ICONERROR);
                break;
            }
            if (threadCount <= 0)
            {
                MessageBoxW(hwnd, L"线程数量必须大于 0。", L"错误", MB_ICONERROR);
                break;
            }

            // 清理旧线程
            for (HANDLE h : g_threadHandles)
            {
                if (h)
                {
                    WaitForSingleObject(h, INFINITE);
                    CloseHandle(h);
                }
            }
            g_threadHandles.clear();
            g_threadIndex.clear();

            // 清空输出框
            SetWindowTextW(g_hOutput, L"");

            g_threadIndex.resize(threadCount);
            g_threadHandles.resize(threadCount);

            for (int i = 0; i < threadCount; ++i)
            {
                g_threadIndex[i] = i + 1;
                DWORD tid = 0;
                HANDLE hThread = CreateThread(
                    nullptr,
                    0,
                    ThreadFunc,
                    &g_threadIndex[i],
                    0,
                    &tid
                );
                if (!hThread)
                {
                    std::string err = "创建线程 " + std::to_string(i + 1) +
                        " 失败，错误码: " + std::to_string(GetLastError()) + "\r\n";
                    AppendTextToOutput(err);
                }
                else
                {
                    g_threadHandles[i] = hThread;
                }
            }
        }
        break;
    }
    case WM_USER_THREAD_MSG:
    {
        int index = (int)wParam;
        DWORD tid = (DWORD)lParam;
        std::string line = "线程 #" + std::to_string(index) +
                           "，系统线程ID = " + std::to_string((unsigned long)tid) + "\r\n";
        AppendTextToOutput(line);
        break;
    }
    case WM_CTLCOLORSTATIC:
    {
        // STATIC 文本使用透明背景 + 浅色字体
        HDC hdc = (HDC)wParam;
        SetTextColor(hdc, TEXT_MAIN);
        SetBkMode(hdc, TRANSPARENT);
        return (LRESULT)g_hPanelBrush; // 靠 panel 颜色
    }
    case WM_CTLCOLOREDIT:
    {
        // EDIT 使用深色底 + 浅色字
        HDC hdc = (HDC)wParam;
        SetTextColor(hdc, TEXT_MAIN);
        SetBkColor(hdc, EDIT_BG);
        return (LRESULT)g_hEditBrush;
    }
    case WM_CTLCOLORBTN:
    {
        // 按钮文字颜色 & 背景色略深一点
        HDC hdc = (HDC)wParam;
        SetTextColor(hdc, TEXT_MAIN);
        SetBkMode(hdc, TRANSPARENT);
        static HBRUSH hBtnBrush = CreateSolidBrush(ACCENT_DARK);
        return (LRESULT)hBtnBrush;
    }
    case WM_PAINT:
    {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hwnd, &ps);

        RECT rc;
        GetClientRect(hwnd, &rc);

        // 背景渐变
        DrawVerticalGradient(hdc, rc, BG_TOP, BG_BOTTOM);

        // 面板（居中）—— 只负责背景，子控件盖在上面
        int w = rc.right - rc.left;
        int h = rc.bottom - rc.top;
        int panelW = 760;
        int panelH = 360;
        int panelX = (w - panelW) / 2;
        int panelY = (h - panelH) / 2;
        RECT rcPanel { panelX, panelY, panelX + panelW, panelY + panelH };

        DrawRoundPanel(hdc, rcPanel, PANEL_COLOR, 22);

        EndPaint(hwnd, &ps);
        return 0;
    }
    case WM_DESTROY:
    {
        // 等待并关闭线程
        for (HANDLE h : g_threadHandles)
        {
            if (h)
            {
                WaitForSingleObject(h, INFINITE);
                CloseHandle(h);
            }
        }
        g_threadHandles.clear();
        g_threadIndex.clear();

        if (g_hFontTitle)  DeleteObject(g_hFontTitle);
        if (g_hFontNormal) DeleteObject(g_hFontNormal);
        if (g_hPanelBrush) DeleteObject(g_hPanelBrush);
        if (g_hEditBrush)  DeleteObject(g_hEditBrush);

        PostQuitMessage(0);
        return 0;
    }
    }

    return DefWindowProc(hwnd, msg, wParam, lParam);
}

// ===================== WinMain 入口 =====================

int APIENTRY WinMain(HINSTANCE hInstance,
                     HINSTANCE hPrevInstance,
                     LPSTR     lpCmdLine,
                     int       nCmdShow)
{
    // 支持中文输出（如果有 console）
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);

    WNDCLASSEXW wcex = { 0 };
    wcex.cbSize        = sizeof(WNDCLASSEXW);
    wcex.style         = CS_HREDRAW | CS_VREDRAW;
    wcex.lpfnWndProc   = WndProc;
    wcex.hInstance     = hInstance;
    wcex.hIcon         = LoadIcon(nullptr, IDI_APPLICATION);
    wcex.hCursor       = LoadCursor(nullptr, IDC_ARROW);
    wcex.hbrBackground = nullptr; // 我们自己画背景
    wcex.lpszClassName = L"ThreadDemoWindowClass";
    wcex.hIconSm       = LoadIcon(nullptr, IDI_APPLICATION);

    if (!RegisterClassExW(&wcex))
    {
        MessageBoxW(nullptr, L"窗口类注册失败！", L"错误", MB_ICONERROR);
        return 1;
    }

    HWND hwnd = CreateWindowExW(
        0,
        L"ThreadDemoWindowClass",
        L"C++ 多线程演示（Win32）",
        WS_OVERLAPPEDWINDOW & ~WS_MAXIMIZEBOX, // 禁止最大化，风格更像你的 Pygame 界面
        CW_USEDEFAULT, 0, 900, 540,
        nullptr, nullptr, hInstance, nullptr);

    if (!hwnd)
    {
        MessageBoxW(nullptr, L"创建窗口失败！", L"错误", MB_ICONERROR);
        return 1;
    }

    g_hMainWnd = hwnd;

    ShowWindow(hwnd, nCmdShow);
    UpdateWindow(hwnd);

    MSG msg;
    while (GetMessageW(&msg, nullptr, 0, 0))
    {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }
    return (int)msg.wParam;
}
