// 将窗口位置和大小调整为和python代码窗口位置和大小一摸一样
#include <windows.h>
#include <string>
#include <vector>

// 主题配色
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

#define WM_USER_THREAD_MSG (WM_USER + 1)

HWND g_hMainWnd   = nullptr;
HWND g_hEditCount = nullptr;
HWND g_hOutput    = nullptr;

HFONT  g_hFontTitle  = nullptr;
HFONT  g_hFontNormal = nullptr;
HBRUSH g_hPanelBrush = nullptr;
HBRUSH g_hEditBrush  = nullptr;

std::vector<int>    g_threadIndex;
std::vector<HANDLE> g_threadHandles;

// 绘制单色背景（简化渐变）
void DrawVerticalGradient(HDC hdc, const RECT& rc, COLORREF top, COLORREF bottom)
{
    HBRUSH hBrush = CreateSolidBrush(top);
    FillRect(hdc, &rc, hBrush);
    DeleteObject(hBrush);
}

// 绘制圆角面板
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

// 线程函数
DWORD WINAPI ThreadFunc(LPVOID lpParam)
{
    int index = *reinterpret_cast<int*>(lpParam);
    DWORD tid = GetCurrentThreadId();
    PostMessage(g_hMainWnd, WM_USER_THREAD_MSG, (WPARAM)index, (LPARAM)tid);
    Sleep(100);
    return 0;
}

// 追加文本到输出框
void AppendTextToOutput(const std::wstring& text)
{
    if (!g_hOutput) return;
    int len = GetWindowTextLengthW(g_hOutput);
    SendMessageW(g_hOutput, EM_SETSEL, len, len);
    SendMessageW(g_hOutput, EM_REPLACESEL, FALSE, (LPARAM)text.c_str());
}

// 窗口过程
LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    switch (msg)
    {
    case WM_CREATE:
    {
        g_hFontTitle = CreateFontW(
            48, 0, 0, 0, FW_BOLD, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_OUTLINE_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, VARIABLE_PITCH, L"Microsoft YaHei UI");

        g_hFontNormal = CreateFontW(
            24, 0, 0, 0, FW_NORMAL, FALSE, FALSE, FALSE,
            DEFAULT_CHARSET, OUT_OUTLINE_PRECIS, CLIP_DEFAULT_PRECIS,
            CLEARTYPE_QUALITY, VARIABLE_PITCH, L"Microsoft YaHei UI");

        g_hPanelBrush = CreateSolidBrush(PANEL_COLOR);
        g_hEditBrush  = CreateSolidBrush(EDIT_BG);

        // 创建控件
        HWND hTitle = CreateWindowExW(
            0, L"STATIC", L"C++ 多线程演示",
            WS_CHILD | WS_VISIBLE,
            0, 0, 0, 0,
            hwnd, nullptr, GetModuleHandle(nullptr), nullptr);
        SendMessageW(hTitle, WM_SETFONT, (WPARAM)g_hFontTitle, TRUE);

        HWND hLabel = CreateWindowExW(
            0, L"STATIC", L"线程数量：",
            WS_CHILD | WS_VISIBLE,
            0, 0, 0, 0,
            hwnd, nullptr, GetModuleHandle(nullptr), nullptr);
        SendMessageW(hLabel, WM_SETFONT, (WPARAM)g_hFontNormal, TRUE);

        g_hEditCount = CreateWindowExW(
            WS_EX_CLIENTEDGE, L"EDIT", L"8",
            WS_CHILD | WS_VISIBLE | ES_NUMBER | ES_LEFT,
            0, 0, 0, 0,
            hwnd, (HMENU)ID_EDIT_COUNT, GetModuleHandle(nullptr), nullptr);
        SendMessageW(g_hEditCount, WM_SETFONT, (WPARAM)g_hFontNormal, TRUE);

        HWND hBtn = CreateWindowExW(
            0, L"BUTTON", L"创建线程",
            WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
            0, 0, 0, 0,
            hwnd, (HMENU)ID_BUTTON_START, GetModuleHandle(nullptr), nullptr);
        SendMessageW(hBtn, WM_SETFONT, (WPARAM)g_hFontNormal, TRUE);

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
        int w = LOWORD(lParam);
        int h = HIWORD(lParam);
        if (w == 0 || h == 0) break;

        int panelW = 760;
        int panelH = 360;
        int panelX = (w - panelW) / 2;
        int panelY = (h - panelH) / 2;

        HWND hTitle = FindWindowExW(hwnd, nullptr, L"Static", L"C++ 多线程演示");
        if (hTitle)
        {
            int titleW = 500;
            int titleH = 60;
            int titleX = (w - titleW) / 2;
            int titleY = panelY - 70;
            SetWindowPos(hTitle, nullptr, titleX, titleY, titleW, titleH, SWP_NOZORDER);
        }

        int labelW = 140;
        int labelH = 34;
        int editW  = 140;
        int editH  = 34;
        int btnW   = 140;
        int btnH   = 36;
        int gap    = 20;
        int rowY   = panelY + 30;

        HWND hLabel = nullptr;
        HWND hChild = nullptr;
        int staticCount = 0;
        while ((hChild = FindWindowExW(hwnd, hChild, L"Static", nullptr)) != nullptr)
        {
            staticCount++;
            if (staticCount == 2) { hLabel = hChild; break; }
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

        int outX = panelX + 30;
        int outY = panelY + 90;
        int outW = panelW - 60;
        int outH = panelH - 120;
        if (g_hOutput) SetWindowPos(g_hOutput, nullptr, outX, outY, outW, outH, SWP_NOZORDER);

        InvalidateRect(hwnd, nullptr, TRUE);
        break;
    }
    case WM_COMMAND:
    {
        if (LOWORD(wParam) == ID_BUTTON_START && HIWORD(wParam) == BN_CLICKED)
        {
            wchar_t buf[32] = { 0 };
            GetWindowTextW(g_hEditCount, buf, 32);
            int threadCount = 0;
            try { threadCount = std::stoi(std::wstring(buf)); }
            catch (...) { MessageBoxW(hwnd, L"请输入有效的正整数。", L"错误", MB_ICONERROR); break; }
            if (threadCount <= 0) { MessageBoxW(hwnd, L"线程数量必须大于 0。", L"错误", MB_ICONERROR); break; }

            for (HANDLE h : g_threadHandles)
            {
                if (h) { WaitForSingleObject(h, INFINITE); CloseHandle(h); }
            }
            g_threadHandles.clear();
            g_threadIndex.clear();

            SetWindowTextW(g_hOutput, L"");

            g_threadIndex.resize(threadCount);
            g_threadHandles.resize(threadCount);

            for (int i = 0; i < threadCount; ++i)
            {
                g_threadIndex[i] = i + 1;
                DWORD tid = 0;
                HANDLE hThread = CreateThread(nullptr, 0, ThreadFunc, &g_threadIndex[i], 0, &tid);
                if (!hThread)
                {
                    std::wstring err = L"创建线程 " + std::to_wstring(i + 1) +
                        L" 失败，错误码: " + std::to_wstring(GetLastError()) + L"\r\n";
                    AppendTextToOutput(err);
                }
                else g_threadHandles[i] = hThread;
            }
        }
        break;
    }
    case WM_USER_THREAD_MSG:
    {
        int index = (int)wParam;
        DWORD tid = (DWORD)lParam;
        std::wstring line = L"线程 #" + std::to_wstring(index) +
                            L"，系统线程ID = " + std::to_wstring((unsigned long)tid) + L"\r\n";
        AppendTextToOutput(line);
        break;
    }
    case WM_CTLCOLORSTATIC:
    {
        HDC hdc = (HDC)wParam;
        SetTextColor(hdc, TEXT_MAIN);
        SetBkMode(hdc, TRANSPARENT);
        return (LRESULT)g_hPanelBrush;
    }
    case WM_CTLCOLOREDIT:
    {
        HDC hdc = (HDC)wParam;
        SetTextColor(hdc, TEXT_MAIN);
        SetBkColor(hdc, EDIT_BG);
        return (LRESULT)g_hEditBrush;
    }
    case WM_CTLCOLORBTN:
    {
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
        DrawVerticalGradient(hdc, rc, BG_TOP, BG_BOTTOM);

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
        for (HANDLE h : g_threadHandles) { if (h) { WaitForSingleObject(h, INFINITE); CloseHandle(h); } }
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

// WinMain
int APIENTRY wWinMain(HINSTANCE hInstance, HINSTANCE, PWSTR, int nCmdShow)
{
    WNDCLASSEXW wcex = { 0 };
    wcex.cbSize        = sizeof(WNDCLASSEXW);
    wcex.style         = CS_HREDRAW | CS_VREDRAW;
    wcex.lpfnWndProc   = WndProc;
    wcex.hInstance     = hInstance;
    wcex.hIcon         = LoadIcon(nullptr, IDI_APPLICATION);
    wcex.hCursor       = LoadCursor(nullptr, IDC_ARROW);
    wcex.hbrBackground = nullptr;
    wcex.lpszClassName = L"ThreadDemoWindowClass";
    wcex.hIconSm       = LoadIcon(nullptr, IDI_APPLICATION);

    if (!RegisterClassExW(&wcex))
    {
        MessageBoxW(nullptr, L"窗口类注册失败！", L"错误", MB_ICONERROR);
        return 1;
    }

    // 多线程窗口位置和大小
    int winX = 200;     // 窗口 X 位置
    int winY = 100;     // 窗口 Y 位置
    int winW = 1280;    // 窗口宽度
    int winH = 760;     // 窗口高度

    HWND hwnd = CreateWindowExW(
        0, L"ThreadDemoWindowClass", L"C++ 多线程演示（Win32）",
        WS_OVERLAPPEDWINDOW & ~WS_MAXIMIZEBOX,
        winX, winY, winW, winH,
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
