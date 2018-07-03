from django.db import models


class Setting(models.Model):
    """
    Основные настройки системы
    """

    api_secret_key = models.CharField(max_length=100, verbose_name='Секретный ключ для доступа по API')
    tree_deep = models.PositiveSmallIntegerField(default=13)
    pages_paginator = models.PositiveSmallIntegerField(default=100, verbose_name='Количество записей для пагинатора')

    class Meta:
        verbose_name_plural = 'Настройки'
        verbose_name = 'Настройка'

    def __str__(self):
        return 'Настройки системы'
