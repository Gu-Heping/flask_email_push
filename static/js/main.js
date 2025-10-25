// 在 DOM 加载完毕后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM 已加载完毕，正在初始化表单提交处理。');

    const form = document.getElementById('emailPushForm');

    if (form) {

        console.log('表单已找到，正在绑定提交事件。');
        form.addEventListener('submit', function(event) {
            // 阻止表单的默认提交行为，页面将不会刷新
            event.preventDefault();

            // 获取表单数据
            const formData = new FormData(form);

            // 2. 转换为普通对象
            const formDataObject = Object.fromEntries(formData.entries());

            // 3. 转换为 JSON 字符串
            const jsonString = JSON.stringify(formDataObject);

            // 发送 AJAX 请求
            fetch(form.action, {
                method: form.method,
                body: jsonString,
                // 确保包含 CSRF 令牌
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrf_token]').value,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('网络错误 ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                    form.reset(); // 清空表单
                    alert(data.message);
            })
            .catch(error => {
                console.error('Fetch error:', error);
                alert('发生错误，请稍后重试。');
            });
        });
    } else {
        console.error('未找到表单，无法绑定提交事件。');
    }
});
