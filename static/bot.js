document.addEventListener('DOMContentLoaded', async function() {
    try {
        const response = await fetch('http://192.168.28.226:5001/bot');
        // const response = await fetch('https://33b9-101-9-133-94.ngrok-free.app/bot');
        if (!response.ok) {
            throw new Error('网络响应不正确');
        }
        const html = await response.text();
        const container = document.createElement('div');
        container.innerHTML = html;

        // 插入 HTML 内容
        document.body.appendChild(container);

        // 查找并执行插入的脚本
        const scripts = container.getElementsByTagName('script');
        for (const script of scripts) {
            const newScript = document.createElement('script');
            if (script.src) {
                newScript.src = script.src;
            } else {
                newScript.textContent = script.textContent;
            }
            document.body.appendChild(newScript);
        }
    } catch (error) {
        console.error('加载 Bot HTML 内容时出错:', error);
    }
});
