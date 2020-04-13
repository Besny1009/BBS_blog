from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class UserInfo(AbstractUser):
    """
    用户表
    """
    avatar = models.FileField(upload_to='avatars/', default='avatars/default.png', verbose_name='头像')
    telephone = models.CharField(verbose_name='电话', max_length=11, null=True)
    blog = models.OneToOneField('Blog', verbose_name='所属博客', null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
class Category(models.Model):
    """
    分类表
    """
    name = models.CharField(verbose_name='分类名称', max_length=32, null=True)
    blog = models.ForeignKey('Blog', verbose_name='所属博客', null=True, on_delete=models.CASCADE)
    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Tag(models.Model):
    """
    标签表
    """
    name = models.CharField(verbose_name='标签', max_length=32, null=True)
    blog = models.ForeignKey('Blog', verbose_name='所属博客', null=True, on_delete=models.CASCADE, )
    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

class Blog(models.Model):
    """
    博主
    """
    title = models.CharField(verbose_name='标题', max_length=64)
    site_name = models.CharField(verbose_name='站点名称', max_length=64)
    theme = models.CharField(verbose_name='站点主题', max_length=32)

    class Meta:
        verbose_name = '博客'
        verbose_name_plural = verbose_name

class Article(models.Model):
    """
    文章表
    """
    title = models.CharField(verbose_name='标题', max_length=64, null=True)
    desc = models.CharField(verbose_name='简介', max_length=255, null=True)
    content = models.TextField(verbose_name='内容')
    user = models.ForeignKey('UserInfo', verbose_name='作者', null=True, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', verbose_name='分类', null=True, on_delete=models.CASCADE)
    tag = models.ManyToManyField('Tag', verbose_name='标签')
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    modified_time = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    up_count = models.IntegerField(verbose_name='点赞数量',  default=0)
    comment_count = models.IntegerField(verbose_name='评论数量', default=0)
    down_count = models.IntegerField(verbose_name='下载量', default=0)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.title

class Comment(models.Model):
    """
    评论表
    """
    user = models.ForeignKey('UserInfo', verbose_name='评论者', on_delete=models.CASCADE, null=True)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    article = models.ForeignKey('Article', null=True, on_delete=models.CASCADE, verbose_name='文章')
    parent_comment = models.ForeignKey('self', null=True, on_delete=models.CASCADE, verbose_name='评论的上一级')
    create_time = models.DateTimeField(verbose_name='评论时间', auto_now_add=True)
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = verbose_name
    def __str__(self):
        return self.content

class ArticleUpDown(models.Model):
    """
    点赞表
    """
    user = models.ForeignKey('UserInfo', null=True, on_delete=models.CASCADE, verbose_name='点赞人')
    article = models.ForeignKey('Article', null=True, on_delete=models.CASCADE, verbose_name='点赞文章')
    is_up = models.BooleanField(default=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '点赞'
        verbose_name_plural = verbose_name



