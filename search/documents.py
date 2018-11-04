# -*- coding:utf-8 -*-

from django_elasticsearch_dsl import Index, DocType, fields
from blog.models import Post, Category
from django.conf import settings
from elasticsearch_dsl import analyzer
post = Index(settings.ELASTICSEARCH_INDEX)

ik_max_word = analyzer('ik_max_word')

@post.doc_type
class PostDocument(DocType):

    '''
    适配Elasticsearch的类，跟着django-elasticsearch-dsl写的。
    '''
    title = fields.TextField(analyzer=ik_max_word,search_analyzer=ik_max_word)
    content = fields.TextField(analyzer=ik_max_word,search_analyzer=ik_max_word)
    category = fields.ObjectField(properties={
        'name': fields.TextField(),
        'cate_id': fields.TextField()
    })

    def get_queryset(self):
        return super(PostDocument,self).get_queryset().select_related('category')

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Category):
            return related_instance.in_category_posts.all()

    class Meta:
        model = Post

        fields = [
            'abstract',
            'create_time',
            'update_time',
            'status',
        ]

        related_models = [Category,]


