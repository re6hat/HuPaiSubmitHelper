#!/usr/bin/python3

import pyautogui as auto
import keyboard
import time
from pymouse import PyMouse
import threading
import argparse
import json
from datetime import datetime, timedelta

OPERATION_DELAY = 0.15 # 操作延时

#jiajia_pos = (2694, 822)
#chujia_pos = (2692, 1029)
#yanzhengma_pos = (2528, 1107)
#queren_pos = (2246, 1293)

log = None

def printToLog(s, flush=True):
  global log
  print(s, file=log)
  if flush:
    log.flush()
  print(s)

class calibration(): # 校正

  def __init__(self, pos_dict = None):
    self.positions = {}
    if pos_dict is None:
      self.i_jiajia()
      self.b_jiajia()
      self.b_chujia()
      self.i_yanzhengma()
      self.b_queren()
    else:
      def extract(name):
        self.positions[name] = (pos_dict[name][0], pos_dict[name][1])
      extract("i_jiajia")
      extract("b_jiajia")
      extract("b_chujia")
      extract("i_yanzhengma")
      extract("b_queren")

  def i_jiajia(self):
    printToLog("按下 i 确认当前鼠标位置为 *加价输入* 坐标：")
    keyboard.wait('i')  # 等待输入 i
    pos = PyMouse().position()
    printToLog(f"加价(i)坐标: {pos}")
    self.positions["i_jiajia"] = pos

  def b_jiajia(self):
    printToLog("按下 j 确认当前鼠标位置为 *加价* 坐标：")
    keyboard.wait('j')  # 等待输入 j
    pos = PyMouse().position()
    printToLog(f"加价(j)坐标: {pos}")
    self.positions["b_jiajia"] = pos

  def b_chujia(self):
    printToLog("按下 c 确认当前鼠标位置为 *出价* 坐标：")
    keyboard.wait('c')  # 等待输入 c
    pos = PyMouse().position()
    printToLog(f"出价(c)坐标: {pos}")
    self.positions["b_chujia"] = pos

  def i_yanzhengma(self):
    printToLog("按下 y 确认当前鼠标位置为 *输入验证码区域* 坐标：")
    keyboard.wait('y')  # 等待输入 y
    pos = PyMouse().position()
    printToLog(f"验证区(y)坐标: {pos}")
    self.positions["i_yanzhengma"] = pos

  def b_queren(self):
    printToLog("按下 q 确认当前鼠标位置为 *确认* 坐标：")
    keyboard.wait('q')  # 等待输入 q
    pos = PyMouse().position()
    printToLog(f"确认(q)坐标: {pos}")
    self.positions["b_queren"] = pos


yanzhengma_ready = False

class OperationPart():

  def __init__(self, positions):
    self.positions = positions

  def add(self, key, delta):
    printToLog(f"按{key}，加价{delta}")
    while True:
      keyboard.wait(key) # 等待输入 c
      #auto.moveTo(self.positions["i_jiajia"])
      auto.click(self.positions["i_jiajia"]) # 自动点击加价键
      auto.press('backspace', presses=6)
      auto.typewrite(f'{delta}')
      time.sleep(0.3)
      auto.click(self.positions["b_jiajia"]) # 自动点击加价键
      auto.click(self.positions["b_chujia"]) # 延时后自动点击出价键
      auto.click(self.positions["i_yanzhengma"]) # 在延时后自动点击输入验证码区域

  def bid(self):
    while True:
      keyboard.wait('j') # 等待输入 j
      auto.click(self.positions["b_chujia"]) # 延时后自动点击出价键
      time.sleep(OPERATION_DELAY)
      auto.click(self.positions["i_yanzhengma"]) # 在延时后自动点击输入验证码区域
      time.sleep(OPERATION_DELAY)

#  def submit(self):
#    while True:
#      keyboard.wait('enter') # 等待输入回车
#      auto.click(self.positions["b_queren"]) # 按回车后自动点击确认键
#      time.sleep(OPERATION_DELAY)

#  def auto_submit(self, tp):
#    while True:
#      if datetime.now() >= tp:
#        auto.click(self.positions["b_queren"]) # 自动提交
#        break
#      else:
#        time.sleep(0.01)

  def auto_jiajia(self, now, delta):
    printToLog(f"{now} !! 加价{delta}", flush=False)
    auto.click(self.positions["i_jiajia"]) # 自动点击加价键
    auto.press('backspace', presses=6)
    auto.typewrite(f'{delta}')
    time.sleep(0.3)
    auto.click(self.positions["b_jiajia"]) # 自动点击加价键
    auto.click(self.positions["b_chujia"]) # 延时后自动点击出价键
    auto.click(self.positions["i_yanzhengma"]) # 在延时后自动点击输入验证码区域
    printToLog(f"{now} !! 加价{delta}完毕")

  def auto_submit(self, now):
    printToLog(f"{now} !! 提交", flush=False)
    auto.click(self.positions["b_queren"]) # 自动提交
    printToLog(f"{now} !! 提交完毕")

  def auto_jiajia_and_submit(self, tp):
    """
    This is the main algorithm. Run this before 11:29:00. Then, it schedules
    four timers
    11:29:00 input 300 & make yanzhengma & press enter!!
    11:29:20 auto submit
    11:29:50 inpput 600 & make yanzhengma & press enter!!
    11:29:55 auto submit, if enter is not seen, this will be delayed till seeing enter
    """
    global yanzhengma_ready

    tp_jiajia1 = tp - timedelta(seconds=40) # aka, 11:29:20
    tp_submit1 = tp - timedelta(seconds=30) # aka, 11:29:30
    tp_jiajia2 = tp - timedelta(seconds=11) # aka, 11:29:49
    tp_submit2 = tp - timedelta(seconds=5, milliseconds=80) # aka, 11:29:54.920
    yanzhengma_ready = False

    delta1 = 300
    delta2 = 600

    printToLog(f"第一次自动加价{delta1} 将于 {tp_jiajia1} 触发")
    printToLog(f"第一次自动提交 将于 {tp_submit1} 触发")
    printToLog(f"第二次自动加价{delta2} 将于 {tp_jiajia2} 触发")
    printToLog(f"第二次自动提交 将于 {tp_submit2} 触发")

    while True:
      now = datetime.now()

      if tp_jiajia1 is not None and now >= tp_jiajia1:
        yanzhengma_ready = False
        self.auto_jiajia(now, delta1)
        tp_jiajia1 = None

      elif tp_submit1 is not None and now >= tp_submit1 and yanzhengma_ready:
        yanzhengma_ready = False
        self.auto_submit(now)
        tp_submit1 = None

      elif tp_jiajia2 is not None and now >= tp_jiajia2:
        self.anzhengma_ready = False
        self.auto_jiajia(now, delta2)
        tp_jiajia2 = None

      elif tp_submit2 is not None and now >= tp_submit2 and yanzhengma_ready:
        yanzhengma_ready = False
        self.auto_submit(now)
        tp_submit2 = None

      else:
        time.sleep(0.01)

  def auto_test(self):
    printToLog(f"按v，自动测试加价和提交")
    while True:
      keyboard.wait('v') # 等待输入 v
      now = datetime.now()
      self.auto_jiajia(now, 300)
      time.sleep(10)
      now = datetime.now()
      self.auto_submit(now)

  def wait_enter(self):
    global yanzhengma_ready
    printToLog(f"按回车，设置为允许到时自动提交")
    while True:
      keyboard.wait("enter") # 等待输入 enter
      yanzhengma_ready = True
      printToLog(f"{datetime.now()} !! 验证码输入完毕")


if __name__ == "__main__":

  parser = argparse.ArgumentParser(description = "沪牌工具")
  parser.add_argument("--cal", action="store_true", default=False, help="重新校准")
  parser.add_argument("--pos", required=True, help="校准文件(JSON)")
  args = parser.parse_args()

  if args.cal: # re-calibration
    cal = calibration()

    if args.pos:
      with open(args.pos, "w") as f:
        json.dump(cal.positions, f, indent=2)
  else:
    with open(args.pos) as f:
      cal = calibration(json.load(f))

  threads = []

  log_filename = f"{args.pos}-{datetime.now().strftime('%Y%m%d')}.log"
  log = open(log_filename, "a")
  log.write(f"\n\n========={datetime.now()}==========\n\n")

  if "moni" in args.pos:
    seconds = input("enter remaining seconds before auto submit:")
    threads.append(threading.Thread(target=OperationPart(cal.positions).auto_jiajia_and_submit,
      args=(datetime.now() + timedelta(seconds=int(seconds)),)))
  else:
    now = datetime.now()
    threads.append(threading.Thread(target=OperationPart(cal.positions).auto_jiajia_and_submit,
      args=(datetime(year=now.year, month=now.month, day=now.day, hour=11, minute=30, second=0, microsecond=0),)))

  printToLog("Press c 出价, j 加价, enter 确认")
  #threads.append(threading.Thread(target=OperationPart(cal.positions).add, args=('q', 100)))
  #threads.append(threading.Thread(target=OperationPart(cal.positions).add, args=('w', 200)))
  #threads.append(threading.Thread(target=OperationPart(cal.positions).add, args=('e', 300)))
  #threads.append(threading.Thread(target=OperationPart(cal.positions).add, args=('r', 400)))
  #threads.append(threading.Thread(target=OperationPart(cal.positions).add, args=('t', 500)))
  #threads.append(threading.Thread(target=OperationPart(cal.positions).add, args=('y', 600)))
  #threads.append(threading.Thread(target=OperationPart(cal.positions).add, args=('u', 700)))
  #threads.append(threading.Thread(target=OperationPart(cal.positions).add, args=('i', 800)))
  #threads.append(threading.Thread(target=OperationPart(cal.positions).add, args=('z', 300)))
  #threads.append(threading.Thread(target=OperationPart(cal.positions).bid))
  threads.append(threading.Thread(target=OperationPart(cal.positions).auto_test))
  threads.append(threading.Thread(target=OperationPart(cal.positions).wait_enter))
  #threads.append(threading.Thread(target=OperationPart(cal.positions).submit))

  for t in threads:
    t.start()
