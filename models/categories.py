from tortoise import fields, models


class Category(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32, unique=True)
    name_uk = fields.CharField(max_length=64)
    name_en = fields.CharField(max_length=64)
    name_pl = fields.CharField(max_length=64)
    name_fr = fields.CharField(max_length=64, null=True)
    name_de = fields.CharField(max_length=64, null=True)
    
    slug_uk = fields.CharField(max_length=128, null=True)
    slug_en = fields.CharField(max_length=128, null=True)
    slug_pl = fields.CharField(max_length=128, null=True)
    slug_fr = fields.CharField(max_length=128, null=True)
    slug_de = fields.CharField(max_length=128, null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "category"


class UnderCategory(models.Model):
    id = fields.IntField(pk=True)
    full_category = fields.ForeignKeyField('models.Category', related_name='undercategories')
    name_uk = fields.CharField(max_length=64, null=True)
    name_en = fields.CharField(max_length=64, null=True)
    name_pl = fields.CharField(max_length=64, null=True)
    name_fr = fields.CharField(max_length=64, null=True)
    name_de = fields.CharField(max_length=64, null=True)
    
    slug_uk = fields.CharField(max_length=128, null=True)
    slug_en = fields.CharField(max_length=128, null=True)
    slug_pl = fields.CharField(max_length=128, null=True)
    slug_fr = fields.CharField(max_length=128, null=True)
    slug_de = fields.CharField(max_length=128, null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "undercategory"