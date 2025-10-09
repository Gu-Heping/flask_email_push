// // 将Base64编码的VAPID公钥解码为Uint8Array
// function urlBase64ToUint8Array(base64String) {
//     const padding = '='.repeat((4 - base64String.length % 4) % 4);
//     const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
//     const rawData = window.atob(base64);
//     const outputArray = new Uint8Array(rawData.length);
//     for (let i = 0; i < rawData.length; i++) {
//         outputArray[i] = rawData.charCodeAt(i);
//     }
//     return outputArray;
// }

// const PUSH_SERVER_URL = 'http://127.0.0.1:5000/api/v1/subscribe';
// // VAPID公钥
// const VAPID_PUBLIC_KEY = document.getElementById('config').dataset.vapidPublicKey;

// // 注册service worker
// async function registerServiceWorker() {
//     if (!('serviceWorker' in navigator)) {
//         console.warn('浏览器不支持Service Worker');
//         document.getElementById('status').textContent = '浏览器不支持Service Worker';
//         return null;
//     }
//     try {
//         // 注册service worker脚本
//         const registration = await navigator.serviceWorker.register('/static/js/sw.js');
//         console.log('[main.js] Service Worker 注册成功:', registration);
//         return registration;
//     } catch (error) {
//         console.error('[main.js] Service Worker 注册失败:', error);
//     }
// }

// // 订阅推送通知并发送到Flask
// async function subscribeUser(registration) {
//     // 检查是否订阅
//     let subscription = await registration.pushManager.getSubscription();
//     if (subscription) {
//         console.log('[main.js] 已经订阅，跳过');
//         document.getElementById('status').textContent = '已经订阅';
//         return null;
//     }

//     // 请求用户授权
//     const permission = await Notification.requestPermission();
//     if (permission !== 'granted') {
//         document.getElemnetById('status').textContent = '用户拒绝了通知权限';
//         return null;
//     }

//     // 开始订阅
//     const applicationServerKey = urlBase64ToUint8Array(VAPID_PUBLIC_KEY);
//     subscription = await registration.pushManager.subscribe({
//         userVisibleOnly: true,
//         applicationServerKey: applicationServerKey // 使用Flask的VAPID公钥
//     });
//     console.log('[main.js] 成功获取订阅对象:', subscription);

//     // 将订阅对象发送到Flask服务器
//     const response = await fetch(PUSH_SERVER_URL, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json'
//         },
//         body: JSON.stringify(subscription)
//     });

//     if (response.status === 201) {
//         document.getElementById('status').textContent = '订阅成功，已发送给Flask后端';
//     } else {
//         document.getElementById('status').textContent = '订阅失败，服务器返回状态码: ' + response.status;
//     }
// }

// // 绑定按钮点击事件
// document.getElementById('subscribeButton').addEventListener('click', async () => {
//     const swRegistration = await registerServiceWorker();
//     if (swRegistration) {
//         subscribeUser(swRegistration);
//     }
// });

// // 页面加载时注册Service Worker
// registerServiceWorker();

// 将Socket声明放在最顶部
let socket;

// 加载DOM
document.addEventListener('DOMContentLoaded', () => {
    const statusElement = document.getElementById('status');
    const notificationsDiv = document.getElementById('notifications');
    const sendButton = document.getElementById('sendButton');
    const send = document.getElementById('send');
    const input = document.getElementById('input');

    // 链接Socket.IO服务器
    // 默认连接当前主机和端口（如http://127.0.0.1:5000）
    socket = io();

    // Socket.IO连接事件处理

    // 监听连接成功事件
    socket.on('connect', () => {
        statusElement.textContent = 'SocketIO连接成功';
        console.log('[SocketIO] 连接成功');
    });

    // 监听连接断开事件
    socket.on('disconnect', () => {
        statusElement.textContent = 'SocketIO连接断开';
        console.log('[SocketIO] 连接断开');
    });

    // 监听来自服务器的通知事件

    // 监听Flask使用emit('server_response', ...)发送的消息
    socket.on('server_response', (data) => {
        console.log('[SocketIO] 收到服务器消息:', data.data);

        // 显示通知
        const notification = document.createElement('p');
        notification.className = 'new-notification';
        notification.innerHTML = `<strong>[${new Date().toLocaleTimeString()}]</strong> ${data.data}`;

        // 添加新通知到顶部
        notificationsDiv.prepend(notification);

        // TODO:添加声音提醒或其他效果
    });

    // 按钮事件：向前台发送测试消息
    sendButton.addEventListener('click', () => {
        //向后端发送一个测试消息 'test_message'
        // 检查连接是否可用
        if (socket.connected) {
            socket.emit('test_message', { 'message': '前端请求发送测试通知' });
            console.log('[SocketIO] 向后端发送测试消息');
        } else {
            console.error('[SocketIO] 连接不可用，无法发送消息');
            statusElement.textContent = 'SocketIO连接不可用';
        }
    });

    // 按钮事件：监测用户发送的自定义消息
    send.addEventListener('click', () => {
        //向后端发送一个测试消息 'test_message'
        // 检查连接是否可用
        if (socket.connected) {
            var message = input.value;
            socket.emit('message', {'message': message});
            console.log('[SocketIO] 用户发送自定义消息: ' + message);            
        } else {
            console.error('[SocketIO] 连接不可用，无法发送消息');
            statusElement.textContent = 'SocketIO连接不可用';
        }
    });

});