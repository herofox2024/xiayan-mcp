#!/usr/bin/env python3
"""
Direct test publishing without complex formatting
"""

import asyncio
import aiohttp
import json

async def direct_publish_test():
    """Test direct publishing with properly encoded content"""
    
    # Get fresh access token
    token_url = "https://api.weixin.qq.com/cgi-bin/stable_token"
    token_data = {
        "grant_type": "client_credential",
        "appid": "your_wechat_app_id",
        "secret": "your_wechat_app_secret",
        "force_refresh": False
    }
    
    async with aiohttp.ClientSession() as session:
        # Get access token
        async with session.post(token_url, json=token_data) as token_response:
            token_result = await token_response.json()
            access_token = token_result['access_token']
            print(f"Got access token: {access_token[:50]}...")
        
        # Prepare article content
        article_content = """<h1>《活着》书评</h1>

<blockquote><p>"人是为了活着本身而活着，而不是为了活着之外的任何事物所活着。"</p></blockquote>

<h2>关于作者</h2>
<p>余华，中国当代著名作家，以其深刻的人性洞察和朴实的叙事风格闻名。《活着》是他的代表作之一，发表于1993年，被誉为中国当代文学的经典之作。</p>

<h2>内容简介</h2>
<p>《活着》讲述了福贵一生的悲欢离合。从富家少爷到贫困农民，从纸醉金迷到一贫如洗，福贵经历了中国近代史上最动荡的几十年。他失去了财富，失去了亲人，但始终没有失去活下去的勇气。</p>

<h2>精彩摘录</h2>
<blockquote>
<p>"我知道他不是那种容易哭的人，可是我听到他哭的声音，他的哭声让我很难受，我也想哭了。"</p>
<p>"没有什么比时间更具有说服力了，因为时间无需通知我们就可以改变一切。"</p>
</blockquote>

<h2>阅读感悟</h2>
<h3>生命的意义</h3>
<p>福贵的故事告诉我们，生命的意义不在于拥有多少，而在于如何面对失去。当一切都被剥夺时，能够依然选择活着，这就是最大的勇气。</p>

<h3>人性的光辉</h3>
<p>在极度贫困和苦难中，福贵依然保持着对人性的基本信任和对生活的热爱。这种在绝境中绽放的人性之光，是最令人动容的地方。</p>

<h2>推荐理由</h2>
<ol>
<li><strong>深刻的人生哲理</strong>：通过一个普通人的生命历程，展现了生命的本质意义</li>
<li><strong>精湛的叙事技巧</strong>：余华用最朴实的语言，讲述了最深刻的故事</li>
<li><strong>珍贵的历史记忆</strong>：记录了中国历史上特殊时期的社会变迁</li>
<li><strong>永恒的人性主题</strong>：无论时代如何变化，人性的光辉永远不会熄灭</li>
</ol>

<h2>适合读者</h2>
<ul>
<li>喜欢深度思考的读者</li>
<li>对中国现当代历史感兴趣的读者</li>
<li>寻找人生意义的探索者</li>
<li>文学爱好者</li>
</ul>

<h2>结语</h2>
<p>《活着》不仅仅是一部小说，更是一面镜子，让我们重新审视生命的意义。在这个快节奏的时代，福贵的故事提醒我们：活着本身就是一种胜利，保持尊严地活着更是一种勇气。</p>

<hr>

<p><strong>文颜书评</strong> —— 与好书相遇，与灵魂对话</p>"""
        
        # Prepare article data
        article_data = {
            "articles": [{
                "title": "《活着》书评",
                "author": "文颜",
                "digest": "余华的《活着》是一部深刻的人性小说，讲述了福贵一生的悲欢离合。",
                "content": article_content,
                "show_cover_pic": 1,
                "thumb_media_id": "9q5Pthue6WCZZGn3PsSlVuxwgdn6-Rp6gQtkTy4Z3caBbU2CfeH9zYql18ItO05L",
                "need_open_comment": 0,
                "only_fans_can_comment": 0
            }]
        }
        
        # Publish article
        draft_url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
        headers = {'Content-Type': 'application/json'}
        
        async with session.post(draft_url, json=article_data, headers=headers) as draft_response:
            response_text = await draft_response.text()
            print(f"Response content type: {draft_response.headers.get('content-type')}")
            print(f"Response text (first 200 chars): {response_text[:200]}")
            
            try:
                draft_result = json.loads(response_text)
            except json.JSONDecodeError:
                # Handle text/plain response
                print("Handling text/plain response...")
                draft_result = json.loads(response_text)
            
            print("Publish result:")
            print(json.dumps(draft_result, ensure_ascii=False, indent=2))
            
            if 'media_id' in draft_result:
                print(f"\n✅ 文章发布成功!")
                print(f"📝 草稿ID: {draft_result['media_id']}")
                print("📱 请在微信公众号草稿箱中查看文章")
            else:
                print(f"\n❌ 发布失败: {draft_result}")

if __name__ == "__main__":
    asyncio.run(direct_publish_test())
