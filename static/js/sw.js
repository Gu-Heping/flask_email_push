self.addEventListener('push', function(event) {
    console.log('[sw] 收到推送事件');

    // 解析消息体
    let data = { title: '默认标题', body: '默认内容' };
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            // 如果不是JSON格式，使用纯文本处理
            data.body = event.data.text();
        }
    }

    const title = data.title || '服务器推送';
    const options = {
        body: data.body || '你有一条新消息',
        // TODO: 可以添加图标、振动等选项
        icon: 'https://cdn.nlark.com/yuque/0/2019/png/294617/1567646355691-avatar/ff2f6133-4491-4a50-8fad-cfb98b73219f.png?x-oss-process=image%2Fresize%2Cm_fill%2Cw_32%2Ch_32%2Fformat%2Cpng', // 替换为你的图标URL
    };

    // 使用event.waitUntil确保在显示通知前不会终止Service Worker
    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

// 监听通知点击事件
self.addEventListener('notificationclick', function(event) {
    console.log('[sw] 通知被点击');
    event.notification.close(); // 关闭通知

    // 可以在这里处理点击事件，例如打开一个特定的URL
    event.waitUntil(
        clients.openWindow('https://nova.yuque.com') // 替换为你想打开的URL
    );
});
