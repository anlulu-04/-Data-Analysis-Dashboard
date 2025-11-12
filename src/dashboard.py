import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import src.data_processor as dp

# 页面设置
st.set_page_config(
    page_title="短视频业务分析看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


class VideoAnalyticsDashboard:
    def __init__(self):
        self.processor = dp.DataProcessor('data/sample_data.csv')

    def setup_sidebar(self):
        """设置侧边栏"""
        st.sidebar.title("📊 控制面板")

        # 数据加载状态
        if st.sidebar.button("🔄 重新加载数据"):
            st.rerun()

        st.sidebar.markdown("---")
        st.sidebar.info("""
        **使用说明：**
        1. 查看核心指标概览
        2. 分析内容类型表现
        3. 优化发布时间策略
        4. 探索详细数据
        """)

    def display_header(self):
        """显示页头"""
        st.title("🎬 短视频业务智能分析看板")
        st.markdown("---")

    def display_summary_metrics(self, df, summary):
        """显示核心指标概览"""
        st.header("📈 核心指标概览")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                label="总视频数",
                value=f"{summary['total_videos']}",
                help="分析期间发布的视频总数"
            )

        with col2:
            st.metric(
                label="总播放量",
                value=f"{summary['total_views']:,}",
                help="所有视频的总播放次数"
            )

        with col3:
            st.metric(
                label="平均互动率",
                value=f"{summary['avg_engagement_rate']}%",
                help="(点赞+评论+转发)/播放量"
            )

        with col4:
            st.metric(
                label="爆款视频数",
                value=f"{summary['hot_videos_count']}",
                help="互动率>5%且播放量>2万的视频"
            )

        with col5:
            st.metric(
                label="爆款率",
                value=f"{summary['hot_videos_rate']}%",
                help="爆款视频占总视频数的比例"
            )

        st.markdown("---")

    def display_content_analysis(self, content_stats):
        """显示内容类型分析"""
        st.header("🎯 内容类型分析")

        col1, col2 = st.columns(2)

        with col1:
            # 互动率柱状图
            fig1 = px.bar(
                content_stats,
                x='content_type',
                y='engagement_rate',
                title='各内容类型平均互动率',
                color='engagement_rate',
                color_continuous_scale='Blues'
            )
            fig1.update_layout(xaxis_title="内容类型", yaxis_title="互动率 (%)")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # 播放量散点图
            fig2 = px.scatter(
                content_stats,
                x='video_count',
                y='views',
                size='hot_rate',
                color='content_type',
                title='内容类型表现分布',
                hover_data=['hot_rate']
            )
            fig2.update_layout(xaxis_title="视频数量", yaxis_title="平均播放量")
            st.plotly_chart(fig2, use_container_width=True)

    def display_time_analysis(self, time_stats):
        """显示时间段分析"""
        st.header("⏰ 发布时间段分析")

        col1, col2 = st.columns(2)

        with col1:
            # 时间段互动率
            fig1 = px.bar(
                time_stats,
                x='time_period',
                y='engagement_rate',
                title='各时间段平均互动率',
                color='engagement_rate',
                color_continuous_scale='Viridis'
            )
            fig1.update_layout(xaxis_title="时间段", yaxis_title="互动率 (%)")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            # 视频发布数量分布
            fig2 = px.pie(
                time_stats,
                values='video_count',
                names='time_period',
                title='视频发布时段分布'
            )
            st.plotly_chart(fig2, use_container_width=True)

    def display_video_ranking(self, df):
        """显示视频排行榜"""
        st.header("🏆 视频表现排行榜")

        # 计算综合得分
        df_rank = df.copy()
        df_rank['composite_score'] = (
                df_rank['engagement_rate'] * 0.4 +
                (df_rank['views'] / 1000) * 0.3 +
                df_rank['completion_rate'] * 100 * 0.3
        )

        top_videos = df_rank.nlargest(10, 'composite_score')[[
            'video_id', 'content_type', 'views', 'engagement_rate',
            'completion_rate', 'composite_score', 'upload_time'
        ]]

        # 格式化显示
        display_df = top_videos.copy()
        display_df['views'] = display_df['views'].apply(lambda x: f"{x:,}")
        display_df['engagement_rate'] = display_df['engagement_rate'].apply(lambda x: f"{x}%")
        display_df['completion_rate'] = display_df['completion_rate'].apply(lambda x: f"{x * 100:.1f}%")
        display_df['composite_score'] = display_df['composite_score'].round(2)

        st.dataframe(
            display_df,
            column_config={
                "video_id": "视频ID",
                "content_type": "内容类型",
                "views": "播放量",
                "engagement_rate": "互动率",
                "completion_rate": "完播率",
                "composite_score": "综合得分",
                "upload_time": "发布时间"
            },
            use_container_width=True
        )

    def display_raw_data(self, df):
        """显示原始数据"""
        st.header("📋 详细数据")

        with st.expander("查看原始数据"):
            st.dataframe(df, use_container_width=True)

            # 数据下载
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 下载数据 (CSV)",
                data=csv,
                file_name="video_analytics_data.csv",
                mime="text/csv"
            )

    def run(self):
        """运行仪表板"""
        # 加载数据
        if not self.processor.load_data():
            st.error("数据加载失败，请检查数据文件")
            return

        # 计算指标
        df = self.processor.calculate_metrics()
        summary = self.processor.get_summary_metrics(df)
        content_stats = self.processor.get_content_type_analysis(df)
        time_stats = self.processor.get_time_period_analysis(df)

        # 渲染界面
        self.setup_sidebar()
        self.display_header()
        self.display_summary_metrics(df, summary)

        col1, col2 = st.columns([3, 1])
        with col1:
            self.display_content_analysis(content_stats)
        with col2:
            st.dataframe(content_stats, use_container_width=True)

        self.display_time_analysis(time_stats)
        self.display_video_ranking(df)
        self.display_raw_data(df)


# 运行应用
if __name__ == "__main__":
    dashboard = VideoAnalyticsDashboard()
    dashboard.run()