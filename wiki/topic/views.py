import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from message.models import Message
from tools.login_check import login_check, get_user_by_request
from topic.models import Topic
from user.models import UserProfile


@login_check('POST', 'DELETE')
def topics(request, author_id):
    if request.method == 'POST':
        # 发表博客
        author = request.user
        if author.username != author_id:
            result = {'code': 30101, 'error': 'The author is error!'}
            return JsonResponse(result)
        json_str = request.body
        json_obj = json.loads(json_str)
        title = json_obj.get('title')
        # 注意xss攻击
        import html
        title = html.escape(title)

        category = json_obj.get('category')
        if category not in ['tec', 'no-tec']:
            result = {'code': 30102, 'error': 'Thanks, your category is error~'}
            return JsonResponse(result)
        limit = json_obj.get('limit')
        if limit not in ['private', 'public']:
            result = {'code': 30103, 'error': 'Thanks, your limit is error!!'}
            return JsonResponse(result)
        # 带样式的文章内容
        content = json_obj.get('content')
        # 纯文本的 文章内容 - 用于做文章简介的切片
        content_text = json_obj.get('content_text')
        introduce = content_text[:30]

        # 创建topic
        Topic.objects.create(title=title, category=category, limit=limit, content=content, introduce=introduce,
                             author=author)

        result = {'code': 200, 'username': author.username}
        return JsonResponse(result)

    if request.method == 'GET':
        # 获取用户文章数据
        # /v1/topics/tony - tony的所有文章
        # /v1/topics/tony?category=tec
        # /v1/topics/tony?t_id=33查看具体文章

        # 1.访问当前博客的访问者 visitor
        # 2.被访问的博客的博主 author
        author = UserProfile.objects.filter(username=author_id)
        if not author:
            result = {'code': 30104, 'error': 'The author is not existed!'}
            return JsonResponse(result)
        author = author[0]
        # 访问者
        visitor = get_user_by_request(request)
        visitor_username = None
        if visitor:
            visitor_username = visitor.username

        t_id = request.GET.get('t_id')
        if t_id:
            # 获取指定文章的详情页
            t_id = int(t_id)
            # 生成标记为 True 为博主自己访问自己, False 为陌生人访问博主
            is_self = False
            if author_id == visitor_username:
                is_self = True
                try:
                    author_topic = Topic.objects.get(id=t_id, author_id=visitor_username)
                except Exception as e:
                    result = {'code': 400, 'error': 'No topic'}
                    return JsonResponse(result)
            else:
                try:
                    author_topic = Topic.objects.get(id=t_id, limit='public')
                except Exception as e:
                    result = {'code': 400, 'error': 'No topic'}
                    return JsonResponse(result)
            # 生成具体返回值
            result = make_topic_res(author, author_topic, is_self)
            return JsonResponse(result)

        else:
            # 列表页
            category = request.GET.get('category')
            if category in ['tec', 'no-tec']:
                # 按种类筛选
                if author_id == visitor_username:
                    author_topics = Topic.objects.filter(author_id=author_id, category=category)
                else:
                    author_topics = Topic.objects.filter(author_id=author_id, limit='public', category=category)
            else:
                # 不分种类

                if author_id == visitor_username:
                    # 博主访问自己的博客,作者文章全部都返回
                    author_topics = Topic.objects.filter(author_id=author_id)
                else:
                    # 陌生人访问他人博客, 只返回公开权限的
                    author_topics = Topic.objects.filter(author_id=author_id, limit='public')
        res = make_topics_res(author, author_topics)
        return JsonResponse(res)

    if request.method == 'DELETE':
        # 删除博客文章, 真删除
        # 请求中携带查询字符串 ?topic_id=3
        # 响应{'code':200}
        user = request.user

        if user.username != author_id:
            print(user.username, author_id)
            result = {'code': 30105, 'error': 'Your id is error'}
            return JsonResponse(result)
        topic_id = request.GET.get('topic_id')
        if not topic_id:
            result = {'code': 30106, 'error': 'Must be give me topic_id!'}
            return JsonResponse(result)
        topic_id = int(topic_id)
        try:
            topic = Topic.objects.get(id=topic_id, author_id=author_id)
            print(topic)
            topic.delete()
            result = {'code': 200}
        except Exception as e:
            print('--topic-delete-error--')
            print(e)
            result = {'code': 30107, 'error': 'The topic is not exist'}
        return JsonResponse(result)


def make_topics_res(author, author_topics):
    # 生成文章列表返回值
    res = {'code': 200, 'data': {}}
    res['data']['nickname'] = author.nickname
    res['data']['topics'] = []
    for topic in author_topics:
        d = {}
        d['id'] = topic.id
        d['title'] = topic.title
        d['category'] = topic.category
        d['introduce'] = topic.introduce
        d['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        d['author'] = author.nickname
        res['data']['topics'].append(d)
    return res


def make_topic_res(author, author_topic, is_self):
    # 后去上一篇文章的id 和 title
    if is_self:
        # 博主自己的博客
        next_topic = Topic.objects.filter(id__gt=author_topic.id, author_id=author).first()
        last_topic = Topic.objects.filter(id__lt=author_topic.id, author_id=author).last()

    else:
        # 访客访问自己的博客
        next_topic = Topic.objects.filter(id__gt=author_topic.id, author_id=author, limit='public').first()
        last_topic = Topic.objects.filter(id__lt=author_topic.id, author_id=author, limit='public').last()

    res = {'code': 200, 'data': {}}
    res['data']['title'] = author_topic.title
    res['data']['nickname'] = author.nickname
    res['data']['content'] = author_topic.content
    res['data']['introduce'] = author_topic.introduce
    res['data']['category'] = author_topic.category
    res['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
    res['data']['author'] = author.nickname

    # 留言
    # TODO 添加留言显示
    all_messages = Message.objects.filter(topic_id=author_topic.id).order_by('-created_time')
    # 留言专属容器
    msg_list = []
    # 回复专属容器
    reply_home = {}

    msg_cnt = 0
    for msg in all_messages:
        msg_cnt += 1
        if msg.parent_message:
            # 回复
            reply_home.setdefault(msg.parent_message, [])
            reply_home[msg.parent_message].append({
                'msg_id': msg.id,
                'content': msg.content,
                'publisher': msg.publisher.nickname,
                'publisher_avatar': str(msg.publisher.avatar),
                'created_time': msg.created_time.strftime('%T-%m-%d %H:%M:%S')
            })
        else:
            # 留言
            msg_list.append({
                'id': msg.id,
                'content': msg.content,
                'publisher': msg.publisher.nickname,
                'publisher_avatar': str(msg.publisher.avatar),
                'created_time': msg.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                'reply': []
            })

        # 关联 留言及回复
        for m in msg_list:
            if m['id'] in reply_home:
                m['reply'] = reply_home[m['id']]
        res['data']['messages'] = msg_list
        res['data']['messages_count'] = msg_cnt



    if next_topic:
        res['data']['next_id'] = next_topic.id
        res['data']['next_title'] = next_topic.title
    else:
        res['data']['next_id'] = None
        res['data']['next_title'] = None

    if last_topic:
        res['data']['last_id'] = last_topic.id
        res['data']['last_title'] = last_topic.title
    else:
        res['data']['last_id'] = None
        res['data']['last_title'] = None

    return res

# def find_son(son_list, target_son):
#     dic = {}
#     if son_list and son_list[0]:
#         so    n = son_list[0]['parent_id']
#         self = son_list[0]['id']
#         if self == 0:
#
#     for i in sonq
