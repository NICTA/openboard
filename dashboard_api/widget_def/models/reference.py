from django.db import models

# Create your models here.

class Theme(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url  = models.SlugField(unique=True)
    sort_order = models.IntegerField()
    def __unicode__(self):
        return self.url
    def __getstate__(self):
        return {"name": self.name, "url": self.url}
    class Meta:
        ordering=("sort_order",)

class Location(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url  = models.SlugField(unique=True)
    sort_order = models.IntegerField()
    def __unicode__(self):
        return self.url
    def __getstate__(self):
        return {"name": self.name, "url": self.url}
    class Meta:
        ordering=("sort_order",)

class Frequency(models.Model):
    name = models.CharField(max_length=60, unique=True)
    url  = models.SlugField(unique=True)
    display_mode = models.BooleanField(default=True)
    actual_display = models.CharField(max_length=60, unique=True)
    sort_order = models.IntegerField()
    def __unicode__(self):
        return self.url
    class Meta:
        verbose_name_plural = "frequencies"
        ordering=("sort_order",)
    def __getstate__(self):
        return {"name": self.name, "url": self.url}

class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    category_aspect = models.IntegerField()
    sort_order = models.IntegerField()
    def __unicode__(self):
        return self.name
    class Meta:
        ordering=("sort_order",)

class Subcategory(models.Model):
    category = models.ForeignKey(Category)
    name = models.CharField(max_length=60)
    sort_order = models.IntegerField()
    def __unicode__(self):
        return "%s:%s" % (self.category.name, self.name)
    class Meta:
        unique_together=(('category', 'name'), ('category', 'sort_order'))
        ordering= ('category', 'sort_order')

