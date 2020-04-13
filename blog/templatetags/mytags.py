from django import template
from django.db.models import Count
from blog.models import *
register = template.Library()
@register.inclusion_tag('classfication.html')
def get_calssfication_style(username):
    user = UserInfo.objects.filter(username=username).first()
    # print(user.username)
    blog = user.blog
    nblog_id = blog.id
    # print(nblog_id)
    cate_list = Category.objects.filter(blog_id=nblog_id).values("pk").annotate(c=Count("article__title")).values_list("name", "c")
    # print(cate_list)
    tag_list = Tag.objects.filter(blog_id=nblog_id).values("pk").annotate(c=Count("article")).values_list("name", "c")
    date_list = Article.objects.filter(user=user).extra(
        select={'y_m_date': "date_format(create_time,'%%Y/%%m')"}).values("y_m_date").annotate(
        c=Count("id")).values_list("y_m_date", "c")
    return{"blog": blog, "cate_list": cate_list, "date_list": date_list, "tag_list": tag_list, "username": username}
