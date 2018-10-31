# -*- coding:utf-8 -*-

from django_elasticsearch_dsl import Index, DocType, fields
from .models import Post, Category

post = Index('posts')

# post.settings(
#     number_of_shards=1,
#     number_of_replicas=0
# )

@post.doc_type
class PostDocument(DocType):

    '''
    适配Elasticsearch的类，跟着django-elasticsearch-dsl写的。
    '''

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
            'title',
            'abstract',
            'content',
            'create_time',
            'update_time',
            'status',
        ]

        related_models = [Category,]


