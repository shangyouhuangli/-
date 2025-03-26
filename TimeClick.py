import sys
sys.path.append(r"D:\python\Lib\site-packages")
import pyautogui
import schedule
import time
import keyboard
import threading
import tkinter as tk
from tkinter import messagebox
import ntplib
from datetime import datetime, timedelta, UTC

# 创建 GUI 窗口
root = tk.Tk()
root.title("自动点击器")
root.geometry("350x450")

# 变量
click_time = tk.StringVar(value="12:00:00.000000")  # 默认时间
click_mode = tk.StringVar(value="current")  # 默认点击模式
click_count = tk.IntVar(value=1)  # 默认点击次数
click_interval = tk.DoubleVar(value=0.01)  # 默认点击间隔（秒）
correction = tk.IntVar(value=0)  # 误差修正（微秒）
is_running = False  # 运行状态

# 显示同步后的网络时间
network_time_display = tk.StringVar(value="同步后时间: 未同步")  # 默认文本


def get_ntp_time():
    """从 time.windows.com 获取当前网络时间（北京时间）"""
    client = ntplib.NTPClient()
    try:
        response = client.request('time.windows.com', version=3)
        ntp_time = datetime.fromtimestamp(response.tx_time, UTC)  # 获取 UTC 时间
        beijing_time = ntp_time + timedelta(hours=8)  # 转换为北京时间（UTC+8）
        return beijing_time
    except Exception as e:
        print("NTP 时间同步失败，错误:", e)
        return None


def sync_system_time():
    """同步北京时间并显示网络时间"""
    ntp_time = get_ntp_time()
    if ntp_time:
        beijing_time_str = ntp_time.strftime("%H:%M:%S.%f")
        network_time_display.set(f"同步后时间: {beijing_time_str}")
        messagebox.showinfo("时间同步", f"已同步北京时间: {beijing_time_str}")
    else:
        network_time_display.set("同步后时间: 获取失败")
        messagebox.showwarning("错误", "无法同步 NTP 时间！")


def click_position():
    """执行点击操作"""
    if click_mode.get() == "current":
        x, y = pyautogui.position()
    else:
        x = int(entry_x.get() or 0)
        y = int(entry_y.get() or 0)

    for _ in range(click_count.get()):
        pyautogui.click(x, y)
        time.sleep(click_interval.get())

    # 显示点击时间
    current_time = datetime.now().strftime("%H:%M:%S.%f")
    messagebox.showinfo("点击时间", f"触发时间: {current_time}")


def start_clicking():
    """开始自动点击"""
    global is_running
    if is_running:
        messagebox.showinfo("提示", "自动点击已在运行！")
        return

    is_running = True
    schedule.clear()

    # 修正目标时间
    target_time = datetime.strptime(click_time.get(), "%H:%M:%S.%f").time()
    target_datetime = datetime.combine(datetime.today(), target_time)
    correction_value = timedelta(microseconds=correction.get())
    corrected_time = target_datetime - correction_value
    corrected_time_str = corrected_time.strftime("%H:%M:%S.%f")
    click_time.set(corrected_time_str)  # 更新 click_time 变量

    schedule.every().day.at(corrected_time.strftime("%H:%M:%S")).do(schedule_click)
    threading.Thread(target=run_schedule, daemon=True).start()
    messagebox.showinfo("提示", f"已设置每天 {corrected_time_str} 自动点击 {click_count.get()} 次！")


def schedule_click():
    """定时执行点击，确保精确到微秒，并应用误差修正"""
    target_time = datetime.strptime(click_time.get(), "%H:%M:%S.%f").time()
    target_datetime = datetime.combine(datetime.today(), target_time)
    correction_value = timedelta(microseconds=correction.get())
    corrected_time = target_datetime - correction_value

    while is_running:
        now = datetime.now()
        if now >= corrected_time:
            click_position()
            break
        time.sleep(0.0005)  # 更精确的检查间隔


def stop_clicking():
    """停止自动点击"""
    global is_running
    is_running = False
    schedule.clear()
    messagebox.showinfo("提示", "自动点击已停止！")


def run_schedule():
    """运行定时任务"""
    while is_running:
        schedule.run_pending()
        if keyboard.is_pressed('esc'):
            stop_clicking()
            break
        time.sleep(0.0005)  # 提高检测频率，确保准确性


# GUI 组件
tk.Label(root, text="设置点击时间（HH:MM:SS.ffffff）").pack()
tk.Entry(root, textvariable=click_time).pack()

tk.Button(root, text="同步网络时间", command=sync_system_time).pack(pady=5)  # 新增同步按钮

tk.Label(root, text="误差修正（微秒，可正可负）").pack()
tk.Entry(root, textvariable=correction).pack()

tk.Label(root, text="选择点击模式").pack()
tk.Radiobutton(root, text="鼠标当前位置", variable=click_mode, value="current").pack()
tk.Radiobutton(root, text="指定坐标", variable=click_mode, value="custom").pack()

# 坐标输入框
coord_frame = tk.Frame(root)
coord_frame.pack()
tk.Label(coord_frame, text="X:").pack(side=tk.LEFT)
entry_x = tk.Entry(coord_frame, width=5)
entry_x.pack(side=tk.LEFT)
tk.Label(coord_frame, text="Y:").pack(side=tk.LEFT)
entry_y = tk.Entry(coord_frame, width=5)
entry_y.pack(side=tk.LEFT)

# 点击次数
tk.Label(root, text="点击次数").pack()
tk.Entry(root, textvariable=click_count).pack()

# 点击间隔
tk.Label(root, text="点击间隔（秒）").pack()
tk.Entry(root, textvariable=click_interval).pack()

# 显示同步后的网络时间
tk.Label(root, textvariable=network_time_display).pack(pady=5)  # 显示同步后的时间

# 按钮
tk.Button(root, text="开始", command=start_clicking).pack(pady=5)
tk.Button(root, text="停止", command=stop_clicking).pack(pady=5)

root.mainloop()
