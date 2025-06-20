from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField('Название категории', max_length=20, unique=True)
    slug = models.SlugField('Слаг категории', max_length=20, unique=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def get_absolute_url(self):
        return reverse('main:product_list_by_category', 
                       args=[self.slug])

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, verbose_name='Категория',
                                 related_name='товары', on_delete=models.CASCADE)
    name = models.CharField('Название товара', max_length=50)
    slug = models.SlugField( max_length=50)
    image = models.ImageField('Изображение', upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    available = models.BooleanField('В наличии', default=True)
    created = models.DateTimeField('Создан', auto_now_add=True)
    updated = models.DateTimeField('Обновлён', auto_now=True)
    discount = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:product_detail', args=[self.slug])

    def sell_price(self):
        if self.discount:
            return round(self.price - self.price * self.discount / 100, 2)
        return self.price


class ProductImage(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='изображения',
                                on_delete=models.CASCADE)
    image = models.ImageField('Доп. изображение', upload_to='products/%Y/%m/%d', blank=True)

    def __str__(self):
        return f'{self.product.name} - {self.image.name}'
