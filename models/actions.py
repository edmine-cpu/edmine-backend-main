from tortoise import models, fields


from tortoise import models, fields

class Bid(models.Model):
    id = fields.IntField(pk=True)
    title_uk = fields.CharField(max_length=128, null=True)
    title_en = fields.CharField(max_length=128, null=True)
    title_pl = fields.CharField(max_length=128, null=True)
    title_fr = fields.CharField(max_length=128, null=True)
    title_de = fields.CharField(max_length=128, null=True)

    slug_uk = fields.CharField(max_length=256, null=True)
    slug_en = fields.CharField(max_length=256, null=True)
    slug_pl = fields.CharField(max_length=256, null=True)
    slug_fr = fields.CharField(max_length=256, null=True)
    slug_de = fields.CharField(max_length=256, null=True)

    categories = fields.JSONField(null=True)  # Список категорий
    under_categories = fields.JSONField(null=True)  # Список подкатегорий

    description_uk = fields.TextField(max_length=2048, null=True)
    description_en = fields.TextField(max_length=2048, null=True)
    description_pl = fields.TextField(max_length=2048, null=True)
    description_fr = fields.TextField(max_length=2048, null=True)
    description_de = fields.TextField(max_length=2048, null=True)

    city = fields.ForeignKeyField('models.City', related_name='bids', null=True)
    country = fields.ForeignKeyField('models.Country', related_name='bids', null=True)

    author = fields.ForeignKeyField('models.User', related_name='bids', null=True)
    budget = fields.CharField(max_length=32, null=True)
    budget_type = fields.CharField(max_length=8, null=True)

    files = fields.JSONField(null=True)
    auto_translated_fields = fields.JSONField(null=True)

    delete_token = fields.CharField(max_length=64, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "bids"



class BlogArticle(models.Model):
    id = fields.IntField(pk=True)
    
    title_uk = fields.CharField(max_length=256)
    title_en = fields.CharField(max_length=256, null=True)
    title_pl = fields.CharField(max_length=256, null=True)
    title_fr = fields.CharField(max_length=256, null=True)
    title_de = fields.CharField(max_length=256, null=True)
    
    slug_uk = fields.CharField(max_length=300, null=True)
    slug_en = fields.CharField(max_length=300, null=True)
    slug_pl = fields.CharField(max_length=300, null=True)
    slug_fr = fields.CharField(max_length=300, null=True)
    slug_de = fields.CharField(max_length=300, null=True)
    
    content_uk = fields.TextField()
    content_en = fields.TextField(null=True)
    content_pl = fields.TextField(null=True)
    content_fr = fields.TextField(null=True)
    content_de = fields.TextField(null=True)
    
    description_uk = fields.CharField(max_length=300, null=True)
    description_en = fields.CharField(max_length=300, null=True)
    description_pl = fields.CharField(max_length=300, null=True)
    description_fr = fields.CharField(max_length=300, null=True)
    description_de = fields.CharField(max_length=300, null=True)
    
    keywords_uk = fields.CharField(max_length=500, null=True)
    keywords_en = fields.CharField(max_length=500, null=True)
    keywords_pl = fields.CharField(max_length=500, null=True)
    keywords_fr = fields.CharField(max_length=500, null=True)
    keywords_de = fields.CharField(max_length=500, null=True)
    
    author = fields.ForeignKeyField('models.User', related_name='blog_articles')
    
    is_published = fields.BooleanField(default=False)
    
    auto_translated_fields = fields.JSONField(null=True)
    
    featured_image = fields.CharField(max_length=500, null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "blog_articles"