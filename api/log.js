export default async function handler(req, res) {
  // 允许跨域
  res.setHeader('Access-Control-Allow-Origin', '*');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });

  // 验证密钥
  const secret = process.env.LOG_SECRET;
  const provided = req.headers['x-secret'] || req.query.secret;
  if (!provided || provided !== secret) {
    return res.status(401).json({ error: 'unauthorized' });
  }

  const token = process.env.GITHUB_TOKEN;
  const owner = process.env.GITHUB_OWNER;
  const repo = process.env.GITHUB_REPO;

  if (!token || !owner || !repo) {
    return res.status(500).json({ error: 'missing env vars' });
  }

  // 解析请求体
  const { event, app, timestamp } = req.body;
  const now = timestamp || new Date().toISOString();
  const date = now.slice(0, 10);
  const path = `data/${date}.json`;

  // 最多重试 3 次，解决并发 SHA 冲突
  for (let attempt = 0; attempt < 3; attempt++) {
    // 每次重试都重新读取最新 SHA 和内容
    let existing = [];
    let sha = null;

    try {
      const getRes = await fetch(
        `https://api.github.com/repos/${owner}/${repo}/contents/${path}`,
        { headers: { 'Authorization': `Bearer ${token}`, 'User-Agent': 'phone-monitor' } }
      );
      if (getRes.ok) {
        const data = await getRes.json();
        sha = data.sha;
        const content = Buffer.from(data.content, 'base64').toString('utf-8');
        existing = JSON.parse(content);
      }
    } catch (e) {
      // 文件不存在，用空数组
    }

    // 追加新事件
    existing.push({
      event: event || 'app_open',
      app: app || 'unknown',
      time: now
    });

    // 写回 GitHub
    const putBody = {
      message: `${event || 'log'}: ${app || 'unknown'} @ ${now.slice(11, 16)}`,
      content: Buffer.from(JSON.stringify(existing, null, 2)).toString('base64'),
      ...(sha ? { sha } : {})
    };

    const putRes = await fetch(
      `https://api.github.com/repos/${owner}/${repo}/contents/${path}`,
      {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          'User-Agent': 'phone-monitor'
        },
        body: JSON.stringify(putBody)
      }
    );

    if (putRes.ok) {
      return res.status(200).json({ success: true, count: existing.length, attempt });
    }

    const errText = await putRes.text();

    // 409 是 SHA 冲突，重试；其他错误直接返回
    if (putRes.status !== 409 && !errText.includes('conflict')) {
      return res.status(500).json({ error: errText });
    }

    // 冲突了，等一小会儿再重试
    await new Promise(r => setTimeout(r, 200 + attempt * 100));
  }

  return res.status(500).json({ error: 'write conflict after 3 retries' });
}
