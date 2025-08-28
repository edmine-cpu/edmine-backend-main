from tortoise import fields, models


class Country(models.Model):
    id = fields.IntField(pk=True)
    name_uk = fields.CharField(max_length=64)
    name_en = fields.CharField(max_length=64)
    name_pl = fields.CharField(max_length=64)
    name_fr = fields.CharField(max_length=64)
    name_de = fields.CharField(max_length=64)
    
    slug_uk = fields.CharField(max_length=128, null=True)
    slug_en = fields.CharField(max_length=128, null=True)
    slug_pl = fields.CharField(max_length=128, null=True)
    slug_fr = fields.CharField(max_length=128, null=True)
    slug_de = fields.CharField(max_length=128, null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "countries"


class City(models.Model):
    id = fields.IntField(pk=True)
    country = fields.ForeignKeyField('models.Country', related_name='cities')
    name_uk = fields.CharField(max_length=64)
    name_en = fields.CharField(max_length=64)
    name_pl = fields.CharField(max_length=64)
    name_fr = fields.CharField(max_length=64)
    name_de = fields.CharField(max_length=64)
    
    slug_uk = fields.CharField(max_length=128, null=True)
    slug_en = fields.CharField(max_length=128, null=True)
    slug_pl = fields.CharField(max_length=128, null=True)
    slug_fr = fields.CharField(max_length=128, null=True)
    slug_de = fields.CharField(max_length=128, null=True)
    
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "cities"