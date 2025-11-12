"""
短视频数据分析看板 - 启动文件
运行命令: streamlit run run_dashboard.py"""

import os
import sys

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.dashboard import VideoAnalyticsDashboard

if __name__ == "__main__":
    dashboard = VideoAnalyticsDashboard()
    dashboard.run()