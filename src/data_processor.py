import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


class DataProcessor:
    def __init__(self, data_path):
        self.data_path = data_path
        self.df = None

    def load_data(self):
        """加载数据"""
        try:
            self.df = pd.read_csv(self.data_path)
            self.df['upload_time'] = pd.to_datetime(self.df['upload_time'])
            return True
        except Exception as e:
            print(f"数据加载失败: {e}")
            return False

    def calculate_metrics(self):
        """计算核心业务指标"""
        if self.df is None:
            return None

        df = self.df.copy()

        # 计算互动率 (likes + comments + shares) / views
        df['engagement_rate'] = ((df['likes'] + df['comments'] + df['shares']) / df['views'] * 100).round(2)

        # 计算爆款视频 (互动率 > 5% 且 播放量 > 20000)
        df['is_hot'] = (df['engagement_rate'] > 5) & (df['views'] > 20000)

        # 计算发布时间段
        df['upload_hour'] = df['upload_time'].dt.hour
        df['time_period'] = df['upload_hour'].apply(self._categorize_time_period)

        return df

    def _categorize_time_period(self, hour):
        """分类时间段"""
        if 6 <= hour < 12:
            return '早晨 (6-12)'
        elif 12 <= hour < 14:
            return '中午 (12-14)'
        elif 14 <= hour < 18:
            return '下午 (14-18)'
        elif 18 <= hour < 22:
            return '晚上 (18-22)'
        else:
            return '深夜 (22-6)'

    def get_summary_metrics(self, df):
        """获取汇总指标"""
        total_videos = len(df)
        total_views = df['views'].sum()
        avg_engagement_rate = df['engagement_rate'].mean()
        hot_videos_count = df['is_hot'].sum()
        hot_videos_rate = (hot_videos_count / total_videos * 100).round(2)

        return {
            'total_videos': total_videos,
            'total_views': total_views,
            'avg_engagement_rate': avg_engagement_rate,
            'hot_videos_count': hot_videos_count,
            'hot_videos_rate': hot_videos_rate
        }

    def get_content_type_analysis(self, df):
        """内容类型分析"""
        content_stats = df.groupby('content_type').agg({
            'views': 'mean',
            'engagement_rate': 'mean',
            'video_id': 'count',
            'is_hot': 'sum'
        }).round(2).reset_index()

        content_stats = content_stats.rename(columns={
            'video_id': 'video_count',
            'is_hot': 'hot_videos'
        })

        content_stats['hot_rate'] = (content_stats['hot_videos'] / content_stats['video_count'] * 100).round(2)

        return content_stats.sort_values('engagement_rate', ascending=False)

    def get_time_period_analysis(self, df):
        """时间段分析"""
        time_stats = df.groupby('time_period').agg({
            'views': 'mean',
            'engagement_rate': 'mean',
            'video_id': 'count'
        }).round(2).reset_index()

        time_stats = time_stats.rename(columns={
            'video_id': 'video_count'
        })

        return time_stats.sort_values('engagement_rate', ascending=False)

    def generate_sample_data(self, num_records=50):
        """生成示例数据 - 用于演示"""
        content_types = ['知识科普', '生活娱乐', '美食制作', '科技数码', '健身教学',
                         '搞笑段子', '美妆护肤', '游戏解说', '旅行摄影', '宠物萌宠']
        creators = [f'C{2000 + i}' for i in range(1, 11)]

        data = []
        base_date = datetime(2024, 1, 1)

        for i in range(num_records):
            video_id = f"V{10000 + i}"
            upload_time = base_date + timedelta(days=random.randint(1, 30),
                                                hours=random.randint(6, 23))
            content_type = random.choice(content_types)
            duration = random.randint(60, 300)

            # 基于内容类型设置不同的表现
            base_views = random.randint(5000, 30000)
            if content_type in ['知识科普', '科技数码']:
                base_views += 10000

            views = base_views + random.randint(-2000, 2000)
            likes = int(views * random.uniform(0.1, 0.3))
            comments = int(views * random.uniform(0.01, 0.05))
            shares = int(views * random.uniform(0.005, 0.02))
            completion_rate = round(random.uniform(0.3, 0.8), 2)
            creator_id = random.choice(creators)

            data.append({
                'video_id': video_id,
                'upload_time': upload_time.strftime('%Y-%m-%d %H:%M:%S'),
                'content_type': content_type,
                'duration_sec': duration,
                'views': views,
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'completion_rate': completion_rate,
                'creator_id': creator_id
            })

        sample_df = pd.DataFrame(data)
        sample_df.to_csv(self.data_path, index=False)
        print(f"已生成示例数据，共 {num_records} 条记录")