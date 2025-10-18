from celery import shared_task

@shared_task
def process_data(data):
    """处理数据的 Celery 异步任务"""
    # 模拟数据处理逻辑
    print(f"正在处理数据: {data}")