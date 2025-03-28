import schedule
import time
from app import main
import sys
import os

def job():
    try:
        main()
    except Exception as e:
        print(f"发送失败: {str(e)}")
        # 如果发送失败，等待5分钟后重试
        time.sleep(300)
        try:
            main()
        except Exception as e:
            print(f"重试失败: {str(e)}")

def main():
    # 设置每天早上8:00发送
    schedule.every().day.at("08:00").do(job)
    
    print("定时任务已启动，将在每天早上8:00发送消息...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("程序已停止")
        sys.exit(0)
    except Exception as e:
        print(f"发生错误: {str(e)}")
        os.system("pause") 