from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


STATUS_CHOICES = (
    ('1', 'Неактивный'),
    ('2', 'Активный'),
    ('3', 'Заморожен'),
    ('4', 'Полное заполнение'),
)


def get_status_text(key):
    for i in STATUS_CHOICES:
        if i[0] == str(key):
            return i[1]
    return False


class BinaryTree(MPTTModel):
    user = models.CharField(max_length=200, verbose_name='Пользователь', unique=True)
    parent = TreeForeignKey('self', null=True, blank=True, verbose_name='Родитель', db_index=True, on_delete=models.SET_NULL)
    left_node = models.PositiveIntegerField(verbose_name='Левый ребёнок', default=None, blank=True, null=True)
    right_node = models.PositiveIntegerField(verbose_name='Правый ребёнок', default=None, blank=True, null=True)
    left_points = models.PositiveIntegerField(verbose_name='Баллы в левой ноге', default=0, blank=True, null=True)
    right_points = models.PositiveIntegerField(verbose_name='Баллы в правой ноге', default=0, blank=True, null=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, verbose_name='Статус', default='1')
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Бинарное дерево'
        verbose_name_plural = 'Бинарные деревья'

    class MPTTMeta:
        order_insertion_by = ('user',)

    def __str__(self):
        return self.user

    def set_status_not_active(self):
        self.status = '1'

    def set_status_active(self):
        self.status = '2'

    def set_status_frozen(self):
        self.status = '3'


class Reason(models.Model):
    """
    Основание для начисления или списания баллов
    Константы:
        1101 - Начисление баллов при регистрации/апгрейде пользователя в бинарном дереве
        1102 - Списание баллов на основании премии
    """
    title = models.CharField(max_length=250, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    code = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        verbose_name = 'Основание для начисления или списания баллов'
        verbose_name_plural = 'Основания для начисления или списания баллов'

    def __str__(self):
        return self.title


class BinaryPointsHistory(models.Model):
    """
    История начисления и списания баллов
    """
    tree_node = models.ForeignKey(BinaryTree, verbose_name='Пользователь', on_delete=models.SET_NULL, blank=True, null=True)
    left_points = models.IntegerField(verbose_name='Баллы', blank=True, null=True)
    right_points = models.IntegerField(verbose_name='Баллы', blank=True, null=True)
    reason = models.ForeignKey(Reason, on_delete=models.SET_NULL, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, auto_now=False, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'История начисления и списания баллов'
        verbose_name_plural = 'История начисления и списания баллов'

    def __str__(self):
        return self.tree_node.user
